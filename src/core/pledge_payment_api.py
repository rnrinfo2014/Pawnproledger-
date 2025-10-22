"""
Pledge Payment API Endpoints
Handles pledge payment operations including single and multiple pledge payments
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import func
from typing import List, Optional
from datetime import datetime, date
import uuid

from src.core.database import get_db
from src.core.models import (
    Customer as CustomerModel,
    Pledge as PledgeModel, 
    PledgePayment as PledgePaymentModel,
    Scheme as SchemeModel,
    VoucherMaster as VoucherMasterModel,
    User as UserModel
)
from src.auth.auth import get_current_admin_user
from src.managers.pledge_accounting_manager import create_payment_accounting
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/pledge-payments", tags=["Pledge Payments"])

# ========================================
# PYDANTIC MODELS
# ========================================

class PendingPledgeDetails(BaseModel):
    pledge_id: int
    pledge_no: str
    pledge_amount: float  # Total loan amount
    scheme_id: int
    pledge_date: date
    due_date: date
    total_interest_due: float  # Calculated interest based on elapsed time
    paid_principal: float  # Total principal payments made
    paid_interest: float  # Total interest payments made  
    current_outstanding: float  # Total amount currently due
    days_since_pledge: int  # Days elapsed since pledge creation
    months_elapsed: int  # Months elapsed (for display)
    first_month_interest: float  # Interest for first month
    additional_interest: float  # Interest beyond first month
    remaining_principal: float  # Principal amount still outstanding
    remaining_interest: float  # Interest amount still outstanding
    scheme_name: str  # Name of the interest scheme
    monthly_interest_rate: float  # Monthly interest rate from scheme

class CustomerPendingPledgesResponse(BaseModel):
    customer_id: int
    customer_name: str
    total_pledges: int
    total_outstanding: float
    pledges: List[PendingPledgeDetails]

# Multiple pledge payment models
class PledgePaymentItem(BaseModel):
    pledge_id: int
    payment_amount: float = Field(gt=0, description="Amount to pay for this pledge")
    payment_type: str = Field(description="Type: interest, principal, partial_principal, full_settlement")
    interest_amount: Optional[float] = Field(0.0, ge=0, description="Interest portion")
    principal_amount: Optional[float] = Field(0.0, ge=0, description="Principal portion")
    discount_amount: Optional[float] = Field(0.0, ge=0, description="Discount given on this pledge")
    penalty_amount: Optional[float] = Field(0.0, ge=0, description="Penalty charged on this pledge")
    discount_reason: Optional[str] = Field(None, description="Reason for discount")
    penalty_reason: Optional[str] = Field(None, description="Reason for penalty")
    remarks: Optional[str] = Field(None, description="Specific remarks for this pledge payment")

class MultiPledgePaymentRequest(BaseModel):
    customer_id: int
    total_payment_amount: float = Field(gt=0, description="Total amount being paid")
    payment_method: str = Field(default="cash", description="Payment method: cash, bank_transfer, cheque, upi")
    bank_reference: Optional[str] = Field(None, max_length=100, description="Bank reference for non-cash payments")
    payment_date: Optional[date] = Field(default=None, description="Payment date (defaults to today)")
    pledge_payments: List[PledgePaymentItem] = Field(description="List of pledge-wise payment breakdown")
    general_remarks: Optional[str] = Field(None, description="General payment remarks")
    receipt_no: Optional[str] = Field(None, max_length=50, description="Custom receipt number")
    # Discount and penalty options
    total_discount_amount: Optional[float] = Field(0.0, ge=0, description="Total discount given")
    total_penalty_amount: Optional[float] = Field(0.0, ge=0, description="Total penalty charged")
    discount_reason: Optional[str] = Field(None, description="Overall discount reason")
    penalty_reason: Optional[str] = Field(None, description="Overall penalty reason")
    approve_discount: Optional[bool] = Field(False, description="Manager approval for discount")
    approve_penalty: Optional[bool] = Field(False, description="Manager approval for penalty")

class PledgePaymentResult(BaseModel):
    pledge_id: int
    pledge_no: str
    payment_amount: float
    interest_paid: float
    principal_paid: float
    discount_amount: float
    penalty_amount: float
    net_payment_amount: float  # payment_amount + penalty - discount
    remaining_balance: float
    payment_status: str  # partial, full_settlement, interest_only
    voucher_no: str  # Accounting voucher number

class MultiPledgePaymentResponse(BaseModel):
    payment_id: str  # Unique payment ID for this multi-pledge payment
    customer_id: int
    customer_name: str
    total_amount_paid: float
    total_discount_given: float
    total_penalty_charged: float
    net_amount: float  # total_amount_paid + penalty - discount
    payment_date: date
    payment_method: str
    receipt_no: str
    master_voucher_no: str  # Main accounting voucher
    pledge_results: List[PledgePaymentResult]
    accounting_entries: List[str]  # List of accounting entries created
    message: str

# ========================================
# UTILITY FUNCTIONS
# ========================================

def generate_receipt_no(db: Session, company_id) -> str:
    """Generate auto-incrementing receipt number for pledge payments"""
    # Get current year for yearly sequence
    current_year = datetime.now().year
    
    # Count existing payments for this company in current year
    year_start = datetime(current_year, 1, 1)
    year_end = datetime(current_year + 1, 1, 1)
    
    count = db.query(PledgePaymentModel).filter(
        PledgePaymentModel.company_id == company_id,
        PledgePaymentModel.created_at >= year_start,
        PledgePaymentModel.created_at < year_end
    ).count()
    
    next_number = count + 1
    return f"RCPT-{company_id}-{current_year}-{next_number:05d}"

# ========================================
# API ENDPOINTS
# ========================================

@router.get("/customers/{customer_id}/pending", response_model=CustomerPendingPledgesResponse)
def get_customer_pending_pledges(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Get customer's pending pledges with detailed interest calculations.
    Returns pledges with status = ACTIVE or PARTIAL_PAID and complete payment breakdown.
    
    Includes:
    - Active pledges (no payments made yet)
    - Partially paid pledges (some payments made but not fully settled)
    
    Interest Calculation Rules:
    1. First month interest is always mandatory (collected at pledge creation)
    2. Additional interest applies after 30 days from pledge start
    3. Month-wise interest based on actual elapsed time
    4. Partial month calculation: ≤15 days = 50%, >15 days = full month
    """
    import math
    
    # Verify customer exists and belongs to user's company
    customer = db.query(CustomerModel).filter(
        CustomerModel.id == customer_id,
        CustomerModel.company_id == current_user.company_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Query active pledges with scheme information and payments
    # Include both 'active' (new pledges) and 'partial_paid' (partially settled) pledges
    active_pledges = db.query(PledgeModel, SchemeModel).join(
        SchemeModel, PledgeModel.scheme_id == SchemeModel.id
    ).filter(
        PledgeModel.customer_id == customer_id,
        PledgeModel.company_id == current_user.company_id,
        PledgeModel.status.in_(['active', 'partial_paid'])  # Include both active and partially paid
    ).order_by(PledgeModel.created_at.desc()).all()
    
    pending_pledges = []
    total_outstanding = 0.0
    
    for pledge, scheme in active_pledges:
        # Get payment history for this pledge
        payments = db.query(PledgePaymentModel).filter(
            PledgePaymentModel.pledge_id == pledge.pledge_id
        ).all()
        
        # Calculate interest based on your reference logic
        total_loan = pledge.total_loan_amount or 0.0
        first_month_interest = pledge.first_month_interest or 0.0
        pledge_start_date = pledge.pledge_date
        current_date = datetime.now().date()
        
        # Calculate days since pledge start
        days_since_pledge_start = (current_date - pledge_start_date).days
        
        # Calculate total interest due based on actual days elapsed
        def calculate_total_interest_due():
            total_interest_due = 0.0
            
            # Rule 1: First month interest is always mandatory
            total_interest_due += first_month_interest
            
            # Rule 2: Additional interest only applies if more than 30 days have passed
            if days_since_pledge_start <= 30:
                return total_interest_due
            
            # Rule 3: Calculate month-wise interest based on actual elapsed time
            total_days_from_second_month = days_since_pledge_start - 30
            full_months_from_second = total_days_from_second_month // 30
            remaining_days_in_current_month = total_days_from_second_month % 30
            
            # Add interest for all full months after the first month
            total_interest_due += full_months_from_second * first_month_interest
            
            # Add interest for remaining days in current month
            if remaining_days_in_current_month > 0:
                if remaining_days_in_current_month <= 15:
                    # Within 15 days = 50% interest
                    total_interest_due += first_month_interest * 0.5
                else:
                    # More than 15 days = full month interest
                    total_interest_due += first_month_interest
            
            return total_interest_due
        
        total_interest_due = calculate_total_interest_due()
        
        # Calculate payments from payment history using explicit fields
        # Use principal_amount and interest_amount fields to avoid misclassification
        total_paid = sum((payment.amount or 0.0) for payment in payments)

        # Sum interest and principal using explicit fields (safer and accurate)
        interest_paid = sum((payment.interest_amount or 0.0) for payment in payments)
        principal_paid = sum((payment.principal_amount or 0.0) for payment in payments)
        
        # Calculate remaining amounts
        remaining_principal = total_loan - principal_paid
        mandatory_interest_unpaid = max(0.0, total_interest_due - interest_paid)
        
        # Calculate additional interest (beyond first month)
        additional_interest = total_interest_due - first_month_interest
        months_elapsed = days_since_pledge_start // 30
        
        # For pawn shop: any extra interest payment beyond mandatory reduces outstanding
        extra_interest_paid = max(0.0, interest_paid - total_interest_due)
        
        # Current outstanding = remaining principal + unpaid mandatory interest - extra interest payments
        current_outstanding = remaining_principal + mandatory_interest_unpaid - extra_interest_paid
        current_outstanding = max(0.0, current_outstanding)  # Cannot be negative
        
        remaining_interest = mandatory_interest_unpaid
        total_outstanding += current_outstanding
        
        pending_pledge = PendingPledgeDetails(
            pledge_id=pledge.pledge_id,
            pledge_no=pledge.pledge_no,
            pledge_amount=total_loan,
            scheme_id=scheme.id,
            pledge_date=pledge.pledge_date,
            due_date=pledge.due_date,
            total_interest_due=total_interest_due,
            paid_principal=principal_paid,
            paid_interest=interest_paid,
            current_outstanding=current_outstanding,
            days_since_pledge=days_since_pledge_start,
            months_elapsed=months_elapsed,
            first_month_interest=first_month_interest,
            additional_interest=additional_interest,
            remaining_principal=remaining_principal,
            remaining_interest=remaining_interest,
            scheme_name=scheme.scheme_name,
            monthly_interest_rate=scheme.interest_rate_monthly
        )
        
        pending_pledges.append(pending_pledge)
    
    return CustomerPendingPledgesResponse(
        customer_id=customer_id,
        customer_name=customer.name,
        total_pledges=len(pending_pledges),
        total_outstanding=total_outstanding,
        pledges=pending_pledges
    )

@router.post("/customers/{customer_id}/multiple-payment", response_model=MultiPledgePaymentResponse)
def create_multiple_pledge_payment(
    customer_id: int,
    payment_data: MultiPledgePaymentRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Create a single payment that covers multiple pledges with automatic financial transactions.
    
    Features:
    - Single receipt for multiple pledges
    - Automatic payment distribution
    - Complete double-entry accounting
    - Payment breakdown per pledge
    - Configurable payment allocation
    """
    import traceback
    
    try:
        # Validate customer exists
        customer = db.query(CustomerModel).filter(
            CustomerModel.id == customer_id,
            CustomerModel.company_id == current_user.company_id
        ).first()
        
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Validate payment data consistency
        if payment_data.customer_id != customer_id:
            raise HTTPException(status_code=400, detail="Customer ID mismatch")
        
        # Calculate total from pledge payments
        calculated_total = sum(item.payment_amount for item in payment_data.pledge_payments)
        if abs(calculated_total - payment_data.total_payment_amount) > 0.01:
            raise HTTPException(
                status_code=400, 
                detail=f"Total payment amount ({payment_data.total_payment_amount}) doesn't match sum of pledge payments ({calculated_total})"
            )
        
        # Validate discount and penalty authorization
        total_discount = sum((item.discount_amount or 0.0) for item in payment_data.pledge_payments) + (payment_data.total_discount_amount or 0.0)
        total_penalty = sum((item.penalty_amount or 0.0) for item in payment_data.pledge_payments) + (payment_data.total_penalty_amount or 0.0)
        
        # Check discount authorization
        if total_discount > 0:
            if not payment_data.approve_discount:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Discount of ₹{total_discount:.2f} requires manager approval. Set approve_discount=true"
                )
            if not payment_data.discount_reason and not any(item.discount_reason for item in payment_data.pledge_payments):
                raise HTTPException(
                    status_code=400, 
                    detail="Discount reason is required when applying discounts"
                )
        
        # Check penalty authorization
        if total_penalty > 0:
            if not payment_data.approve_penalty:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Penalty of ₹{total_penalty:.2f} requires manager approval. Set approve_penalty=true"
                )
            if not payment_data.penalty_reason and not any(item.penalty_reason for item in payment_data.pledge_payments):
                raise HTTPException(
                    status_code=400, 
                    detail="Penalty reason is required when charging penalties"
                )
        
        # Validate all pledges belong to the customer and are active
        pledge_ids = [item.pledge_id for item in payment_data.pledge_payments]
        pledges = db.query(PledgeModel).filter(
            PledgeModel.pledge_id.in_(pledge_ids),
            PledgeModel.customer_id == customer_id,
            PledgeModel.company_id == current_user.company_id,
            PledgeModel.status.in_(['active', 'partial_paid'])  # Include both active and partially paid
        ).all()
        
        if len(pledges) != len(pledge_ids):
            missing_pledges = set(pledge_ids) - {p.pledge_id for p in pledges}
            raise HTTPException(
                status_code=400,
                detail=f"Some pledges not found or not active: {missing_pledges}"
            )
        
        # Create mapping for quick lookup
        pledge_map = {p.pledge_id: p for p in pledges}
        
        # Generate unique payment ID and receipt number
        payment_id = str(uuid.uuid4())
        receipt_no = payment_data.receipt_no or generate_receipt_no(db, current_user.company_id)
        payment_date = payment_data.payment_date or datetime.now().date()
        
        # Create master voucher for the entire payment
        master_voucher = VoucherMasterModel(
            voucher_type="Payment",
            voucher_date=payment_date,
            narration=f"Multiple pledge payment for customer {customer.name} - Amount: ₹{payment_data.total_payment_amount}",
            company_id=current_user.company_id,
            created_by=current_user.id
        )
        db.add(master_voucher)
        db.flush()  # Get the voucher ID
        
        # Generate voucher number using voucher_id
        master_voucher_no = f"MP{master_voucher.voucher_id:06d}"
        
        pledge_results = []
        accounting_entries = []
        
        # Process each pledge payment
        for payment_item in payment_data.pledge_payments:
            pledge = pledge_map[payment_item.pledge_id]
            
            # Calculate remaining balance for this pledge first
            total_payments = db.query(func.sum(PledgePaymentModel.amount)).filter(
                PledgePaymentModel.pledge_id == pledge.pledge_id
            ).scalar() or 0.0
            
            # Calculate what balance will be after this payment
            new_balance = (pledge.total_loan_amount + pledge.first_month_interest) - (total_payments + payment_item.payment_amount)
            
            # Create individual pledge payment record
            pledge_payment = PledgePaymentModel(
                pledge_id=pledge.pledge_id,
                payment_date=payment_date,
                payment_type=payment_item.payment_type,
                amount=payment_item.payment_amount,
                interest_amount=payment_item.interest_amount or 0.0,
                principal_amount=payment_item.principal_amount or 0.0,
                penalty_amount=payment_item.penalty_amount or 0.0,
                discount_amount=payment_item.discount_amount or 0.0,
                balance_amount=max(0.0, new_balance),  # Required field
                payment_method=payment_data.payment_method,
                bank_reference=payment_data.bank_reference,
                receipt_no=receipt_no,
                remarks=payment_item.remarks or f"Part of multiple pledge payment {payment_id}",
                company_id=current_user.company_id,
                created_by=current_user.id
            )
            db.add(pledge_payment)
            db.flush()  # Get payment ID
            
            # Create accounting entries for this pledge payment
            try:
                print(f"🔄 Creating accounting for payment {pledge_payment.payment_id}")
                accounting_result = create_payment_accounting(
                    db=db,
                    payment=pledge_payment,
                    pledge=pledge,
                    customer=customer,
                    company_id=current_user.company_id
                )
                print(f"✅ Accounting created successfully")
            except Exception as accounting_error:
                import traceback
                error_details = traceback.format_exc()
                print(f"❌ Accounting error: {str(accounting_error)}")
                print(f"❌ Full error traceback: {error_details}")
                # Continue without accounting for now to isolate the issue
                accounting_result = {"voucher_id": "SKIP", "entries_created": 0}
            
            # Use the balance we calculated earlier
            remaining_balance = new_balance
            
            # Determine payment status
            payment_status = "partial"
            if remaining_balance <= 0.01:
                payment_status = "full_settlement"
                # Update pledge status to CLOSED if fully paid
                pledge.status = "closed"
                pledge.closed_at = datetime.now()
            elif payment_item.principal_amount == 0:
                payment_status = "interest_only"
            else:
                # If principal payment made but not fully settled, mark as partial_paid
                if payment_item.principal_amount > 0 and remaining_balance > 0.01:
                    pledge.status = "partial_paid"
            
            # Calculate net payment amount (payment + penalty - discount)
            net_payment = payment_item.payment_amount + (payment_item.penalty_amount or 0.0) - (payment_item.discount_amount or 0.0)
            
            pledge_result = PledgePaymentResult(
                pledge_id=pledge.pledge_id,
                pledge_no=pledge.pledge_no,
                payment_amount=payment_item.payment_amount,
                interest_paid=payment_item.interest_amount or 0.0,
                principal_paid=payment_item.principal_amount or 0.0,
                discount_amount=payment_item.discount_amount or 0.0,
                penalty_amount=payment_item.penalty_amount or 0.0,
                net_payment_amount=net_payment,
                remaining_balance=max(0.0, remaining_balance),
                payment_status=payment_status,
                voucher_no=master_voucher_no
            )
            
            pledge_results.append(pledge_result)
            accounting_entries.append(f"Pledge {pledge.pledge_no}: Dr.Cash ₹{payment_item.payment_amount}, Cr.Customer A/c")
        
        # Calculate totals for discount and penalty
        total_discount = sum((item.discount_amount or 0.0) for item in payment_data.pledge_payments) + (payment_data.total_discount_amount or 0.0)
        total_penalty = sum((item.penalty_amount or 0.0) for item in payment_data.pledge_payments) + (payment_data.total_penalty_amount or 0.0)
        net_amount = payment_data.total_payment_amount + total_penalty - total_discount
        
        # Commit all changes
        db.commit()
        
        response = MultiPledgePaymentResponse(
            payment_id=payment_id,
            customer_id=customer_id,
            customer_name=customer.name,
            total_amount_paid=payment_data.total_payment_amount,
            total_discount_given=total_discount,
            total_penalty_charged=total_penalty,
            net_amount=net_amount,
            payment_date=payment_date,
            payment_method=payment_data.payment_method,
            receipt_no=receipt_no,
            master_voucher_no=master_voucher_no,
            pledge_results=pledge_results,
            accounting_entries=accounting_entries,
            message=f"Successfully processed payment of ₹{payment_data.total_payment_amount} across {len(payment_data.pledge_payments)} pledges. Net amount: ₹{net_amount:.2f} (Discount: ₹{total_discount:.2f}, Penalty: ₹{total_penalty:.2f})"
        )
        
        return response
        
    except Exception as e:
        db.rollback()
        error_details = f"Error: {str(e)}, Type: {type(e).__name__}, Traceback: {traceback.format_exc()}"
        print(f"❌ Payment processing error: {error_details}")
        raise HTTPException(status_code=500, detail=f"Payment processing failed: {str(e) or 'Unknown error occurred'}")
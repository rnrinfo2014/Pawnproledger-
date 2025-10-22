"""
Payment Receipt Management API - Update, Delete, and Transaction Reversal
Provides secure payment receipt modification with complete accounting transaction reversal
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field

from src.core.database import get_db
from src.core.models import (
    PledgePayment as PledgePaymentModel,
    VoucherMaster as VoucherMasterModel,
    LedgerEntry as LedgerEntryModel,
    Pledge as PledgeModel,
    Customer as CustomerModel,
    User as UserModel
)
from src.auth.auth import get_current_admin_user

router = APIRouter(prefix="/api/v1/payment-management", tags=["Payment Management"])

# Pydantic Models
class PaymentUpdateRequest(BaseModel):
    payment_amount: Optional[float] = Field(None, gt=0, description="New payment amount")
    interest_amount: Optional[float] = Field(None, ge=0, description="New interest amount")
    principal_amount: Optional[float] = Field(None, ge=0, description="New principal amount")
    payment_method: Optional[str] = Field(None, description="New payment method")
    bank_reference: Optional[str] = Field(None, description="New bank reference")
    remarks: Optional[str] = Field(None, description="New remarks")
    reason_for_change: str = Field(..., description="Reason for modifying payment")

class PaymentDeletionRequest(BaseModel):
    reason_for_deletion: str = Field(..., description="Reason for deleting payment")
    confirm_deletion: bool = Field(..., description="Confirm deletion (must be true)")

class TransactionReversalInfo(BaseModel):
    voucher_id: int
    voucher_type: str
    entries_reversed: int
    total_debit_reversed: float
    total_credit_reversed: float

class PaymentOperationResponse(BaseModel):
    success: bool
    message: str
    payment_id: Optional[int] = None
    receipt_no: Optional[str] = None
    operation_type: str  # "update", "delete", "reversal"
    accounting_impact: Optional[TransactionReversalInfo] = None
    pledge_status_updated: bool = False
    audit_trail: Dict[str, Any]

# Helper Functions
def reverse_accounting_entries(db: Session, payment: PledgePaymentModel, user_id: int, reason: str) -> Optional[TransactionReversalInfo]:
    """
    Reverse all accounting entries for a payment
    Creates opposite entries to cancel out the original transaction
    """
    
    # Find all ledger entries for this payment
    ledger_entries = db.query(LedgerEntryModel).filter(
        LedgerEntryModel.reference_type == 'payment',
        LedgerEntryModel.reference_id == payment.payment_id
    ).all()
    
    if not ledger_entries:
        return None
    
    # Get the original voucher
    voucher_id = ledger_entries[0].voucher_id if ledger_entries else None
    original_voucher = db.query(VoucherMasterModel).filter(
        VoucherMasterModel.voucher_id == voucher_id
    ).first() if voucher_id else None
    
    if not original_voucher:
        return None
    
    # Create reversal voucher (use Journal type for reversals)
    reversal_voucher = VoucherMasterModel()
    reversal_voucher.voucher_type = "Journal"
    reversal_voucher.voucher_date = datetime.now().date()
    reversal_voucher.narration = f"Reversal of {original_voucher.voucher_type} payment {payment.receipt_no} - Reason: {reason}"
    reversal_voucher.company_id = payment.company_id
    reversal_voucher.created_by = user_id
    db.add(reversal_voucher)
    db.flush()  # Get voucher ID
    
    # Create opposite entries
    total_debit_reversed = 0.0
    total_credit_reversed = 0.0
    entries_reversed = 0
    
    for original_entry in ledger_entries:
        # Create opposite entry
        reversal_entry = LedgerEntryModel()
        reversal_entry.voucher_id = reversal_voucher.voucher_id
        reversal_entry.account_id = original_entry.account_id
        # Swap debit/credit to reverse
        reversal_entry.dr_cr = 'C' if original_entry.dr_cr == 'D' else 'D'
        reversal_entry.amount = original_entry.amount
        reversal_entry.debit = original_entry.credit  # Swap amounts
        reversal_entry.credit = original_entry.debit
        reversal_entry.narration = f"Reversal: {original_entry.narration}"
        reversal_entry.reference_type = 'payment_reversal'
        reversal_entry.reference_id = payment.payment_id
        reversal_entry.transaction_date = datetime.now().date()
        db.add(reversal_entry)
        
        # Track totals
        total_debit_reversed += original_entry.debit or 0.0
        total_credit_reversed += original_entry.credit or 0.0
        entries_reversed += 1
    
    return TransactionReversalInfo(
        voucher_id=reversal_voucher.voucher_id,
        voucher_type=reversal_voucher.voucher_type,
        entries_reversed=entries_reversed,
        total_debit_reversed=total_debit_reversed,
        total_credit_reversed=total_credit_reversed
    )

def update_pledge_status_after_payment_change(db: Session, pledge_id: int) -> bool:
    """
    Recalculate pledge status after payment modification
    """
    
    pledge = db.query(PledgeModel).filter(PledgeModel.pledge_id == pledge_id).first()
    if not pledge:
        return False
    
    # Get all remaining payments for this pledge
    remaining_payments = db.query(PledgePaymentModel).filter(
        PledgePaymentModel.pledge_id == pledge_id
    ).all()
    
    total_paid = sum(payment.amount or 0.0 for payment in remaining_payments)
    total_due = (pledge.total_loan_amount or 0.0) + (pledge.first_month_interest or 0.0)
    
    # Update pledge status based on remaining payments
    if total_paid <= 0:
        pledge.status = 'active'
    elif total_paid >= total_due:
        pledge.status = 'closed'
        pledge.closed_at = datetime.now()
    else:
        pledge.status = 'partial_paid'
    
    return True

# API Endpoints
@router.put("/payment/{payment_id}", response_model=PaymentOperationResponse)
async def update_payment_receipt(
    payment_id: int,
    update_data: PaymentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Update an existing payment receipt
    CAUTION: This will reverse existing accounting entries and create new ones
    """
    
    # Find payment
    payment = db.query(PledgePaymentModel).filter(
        PledgePaymentModel.payment_id == payment_id,
        PledgePaymentModel.company_id == current_user.company_id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check if payment is recent (safety check)
    payment_age_days = (datetime.now().date() - payment.payment_date).days
    if payment_age_days > 30:
        raise HTTPException(
            status_code=400, 
            detail="Cannot modify payments older than 30 days. Contact administrator."
        )
    
    # Store original values for audit
    original_values = {
        "payment_amount": payment.amount,
        "interest_amount": payment.interest_amount,
        "principal_amount": payment.principal_amount,
        "payment_method": payment.payment_method,
        "bank_reference": payment.bank_reference,
        "remarks": payment.remarks
    }
    
    try:
        # Step 1: Reverse existing accounting entries
        reversal_info = reverse_accounting_entries(
            db, payment, current_user.id, update_data.reason_for_change
        )
        
        # Step 2: Update payment record
        if update_data.payment_amount is not None:
            payment.amount = update_data.payment_amount
        if update_data.interest_amount is not None:
            payment.interest_amount = update_data.interest_amount
        if update_data.principal_amount is not None:
            payment.principal_amount = update_data.principal_amount
        if update_data.payment_method is not None:
            payment.payment_method = update_data.payment_method
        if update_data.bank_reference is not None:
            payment.bank_reference = update_data.bank_reference
        if update_data.remarks is not None:
            payment.remarks = f"{payment.remarks} | Updated: {update_data.reason_for_change}"
        
        # Recalculate balance
        pledge = db.query(PledgeModel).filter(PledgeModel.pledge_id == payment.pledge_id).first()
        if pledge:
            # Get all payments for this pledge to recalculate balance
            total_payments = db.query(PledgePaymentModel).filter(
                PledgePaymentModel.pledge_id == payment.pledge_id
            ).all()
            total_paid = sum(p.amount or 0.0 for p in total_payments)
            total_due = (pledge.total_loan_amount or 0.0) + (pledge.first_month_interest or 0.0)
            payment.balance_amount = max(0.0, total_due - total_paid)
        
        # Step 3: Create new accounting entries (using existing function)
        customer = db.query(CustomerModel).filter(CustomerModel.id == pledge.customer_id).first()
        if customer and reversal_info:
            from src.managers.pledge_accounting_manager import create_payment_accounting
            create_payment_accounting(db, payment, pledge, customer, current_user.company_id)
        
        # Step 4: Update pledge status
        pledge_updated = update_pledge_status_after_payment_change(db, payment.pledge_id)
        
        # Commit all changes
        db.commit()
        
        return PaymentOperationResponse(
            success=True,
            message=f"Payment {payment.receipt_no} updated successfully",
            payment_id=payment.payment_id,
            receipt_no=payment.receipt_no,
            operation_type="update",
            accounting_impact=reversal_info,
            pledge_status_updated=pledge_updated,
            audit_trail={
                "updated_by": current_user.id,
                "update_date": datetime.now().isoformat(),
                "reason": update_data.reason_for_change,
                "original_values": original_values,
                "new_values": {
                    "payment_amount": payment.amount,
                    "interest_amount": payment.interest_amount,
                    "principal_amount": payment.principal_amount,
                    "payment_method": payment.payment_method,
                    "bank_reference": payment.bank_reference
                }
            }
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update payment: {str(e)}")

@router.delete("/payment/{payment_id}", response_model=PaymentOperationResponse)
async def delete_payment_receipt(
    payment_id: int,
    deletion_data: PaymentDeletionRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Delete a payment receipt and reverse all associated transactions
    CAUTION: This will permanently delete the payment and reverse accounting entries
    """
    
    if not deletion_data.confirm_deletion:
        raise HTTPException(status_code=400, detail="Deletion not confirmed")
    
    # Find payment
    payment = db.query(PledgePaymentModel).filter(
        PledgePaymentModel.payment_id == payment_id,
        PledgePaymentModel.company_id == current_user.company_id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check if payment is recent (safety check)
    payment_age_days = (datetime.now().date() - payment.payment_date).days
    if payment_age_days > 7:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete payments older than 7 days. Contact administrator."
        )
    
    # Store payment info for response
    payment_info = {
        "payment_id": payment.payment_id,
        "receipt_no": payment.receipt_no,
        "amount": payment.amount,
        "payment_date": payment.payment_date.isoformat(),
        "pledge_id": payment.pledge_id
    }
    
    try:
        # Step 1: Reverse accounting entries
        reversal_info = reverse_accounting_entries(
            db, payment, current_user.id, deletion_data.reason_for_deletion
        )
        
        # Step 2: Delete the payment record
        db.delete(payment)
        
        # Step 3: Update pledge status
        pledge_updated = update_pledge_status_after_payment_change(db, payment.pledge_id)
        
        # Commit all changes
        db.commit()
        
        return PaymentOperationResponse(
            success=True,
            message=f"Payment {payment_info['receipt_no']} deleted successfully",
            payment_id=None,  # Payment no longer exists
            receipt_no=payment_info['receipt_no'],
            operation_type="delete",
            accounting_impact=reversal_info,
            pledge_status_updated=pledge_updated,
            audit_trail={
                "deleted_by": current_user.id,
                "deletion_date": datetime.now().isoformat(),
                "reason": deletion_data.reason_for_deletion,
                "deleted_payment": payment_info
            }
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete payment: {str(e)}")

@router.get("/payment/{payment_id}/can-modify")
async def check_payment_modifiable(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Check if a payment can be modified or deleted
    Returns restrictions and warnings
    """
    
    payment = db.query(PledgePaymentModel).filter(
        PledgePaymentModel.payment_id == payment_id,
        PledgePaymentModel.company_id == current_user.company_id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment_age_days = (datetime.now().date() - payment.payment_date).days
    
    # Check for related entries
    ledger_entries = db.query(LedgerEntryModel).filter(
        LedgerEntryModel.reference_type == 'payment',
        LedgerEntryModel.reference_id == payment.payment_id
    ).count()
    
    # Get pledge info
    pledge = db.query(PledgeModel).filter(PledgeModel.pledge_id == payment.pledge_id).first()
    
    return {
        "payment_id": payment_id,
        "receipt_no": payment.receipt_no,
        "payment_age_days": payment_age_days,
        "can_update": payment_age_days <= 30,
        "can_delete": payment_age_days <= 7,
        "has_accounting_entries": ledger_entries > 0,
        "accounting_entries_count": ledger_entries,
        "pledge_status": pledge.status if pledge else None,
        "restrictions": {
            "update_limit": "30 days",
            "delete_limit": "7 days",
            "requires_admin": True
        },
        "warnings": [
            "Modifying payments will reverse and recreate accounting entries",
            "This action creates an audit trail",
            "Pledge status may change after modification"
        ]
    }

@router.get("/recent-modifications")
async def get_recent_payment_modifications(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Get recent payment modifications and deletions for audit purposes
    """
    from datetime import timedelta
    
    cutoff_date = datetime.now().date() - timedelta(days=days)
    
    # Find journal vouchers with reversal narration (indicating modifications/deletions)
    reversal_vouchers = db.query(VoucherMasterModel).filter(
        VoucherMasterModel.voucher_type == "Journal",
        VoucherMasterModel.narration.like("Reversal of%"),
        VoucherMasterModel.voucher_date >= cutoff_date,
        VoucherMasterModel.company_id == current_user.company_id
    ).order_by(VoucherMasterModel.voucher_date.desc()).all()
    
    modifications = []
    for voucher in reversal_vouchers:
        # Get associated ledger entries to find payment reference
        entries = db.query(LedgerEntryModel).filter(
            LedgerEntryModel.voucher_id == voucher.voucher_id
        ).all()
        
        payment_id = entries[0].reference_id if entries else None
        
        modifications.append({
            "voucher_id": voucher.voucher_id,
            "voucher_type": voucher.voucher_type,
            "date": voucher.voucher_date,
            "narration": voucher.narration,
            "payment_id": payment_id,
            "entries_count": len(entries),
            "created_by": voucher.created_by
        })
    
    return {
        "period_days": days,
        "modifications_found": len(modifications),
        "modifications": modifications
    }
"""
Payment Receipt API Module
==========================

Comprehensive API for payment receipt management including:
- Receipt retrieval by receipt number, customer, pledge, date range
- Receipt details for printing/PDF generation
- Receipt search and filtering
- Receipt summary and analytics

Author: PawnPro Development Team
Created: 2025-10-15
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Union
from datetime import date, datetime
from pydantic import BaseModel, Field

# Import dependencies
from src.auth.auth import get_current_user, get_current_admin_user
from src.core.database import get_db
from src.core.models import (
    User as UserModel,
    PledgePayment as PledgePaymentModel,
    Pledge as PledgeModel,
    Customer as CustomerModel,
    Company as CompanyModel,
    VoucherMaster as VoucherMasterModel
)

# Create router
router = APIRouter(prefix="/api/v1/receipts", tags=["Payment Receipts"])

# ========================================
# PYDANTIC MODELS
# ========================================

class ReceiptBasicInfo(BaseModel):
    """Basic receipt information for listing"""
    payment_id: int
    receipt_no: str
    payment_date: date
    customer_name: str
    pledge_no: str
    amount: float
    payment_type: str
    payment_method: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReceiptDetailInfo(BaseModel):
    """Detailed receipt information"""
    payment_id: int
    receipt_no: str
    payment_date: date
    payment_type: str
    payment_method: str
    bank_reference: Optional[str]
    amount: float
    interest_amount: float
    principal_amount: float
    penalty_amount: float
    discount_amount: float
    balance_amount: float
    remarks: Optional[str]
    created_at: datetime
    created_by: int
    
    # Customer information
    customer_id: int
    customer_name: str
    customer_phone: Optional[str]
    customer_address: Optional[str]
    
    # Pledge information
    pledge_id: int
    pledge_no: str
    pledge_date: date
    loan_amount: float
    final_amount: float
    
    # Company information
    company_name: str
    company_address: Optional[str]
    company_phone: Optional[str]
    
    # Staff information
    staff_name: str
    
    class Config:
        from_attributes = True

class ReceiptSummary(BaseModel):
    """Receipt summary for analytics"""
    total_receipts: int
    total_amount: float
    payment_methods: dict
    payment_types: dict
    date_range: dict
    
class ReceiptSearchRequest(BaseModel):
    """Receipt search parameters"""
    receipt_no: Optional[str] = Field(None, description="Receipt number (partial match)")
    customer_name: Optional[str] = Field(None, description="Customer name (partial match)")
    pledge_no: Optional[str] = Field(None, description="Pledge number (partial match)")
    payment_type: Optional[str] = Field(None, description="Payment type filter")
    payment_method: Optional[str] = Field(None, description="Payment method filter")
    from_date: Optional[date] = Field(None, description="Start date filter")
    to_date: Optional[date] = Field(None, description="End date filter")
    min_amount: Optional[float] = Field(None, ge=0, description="Minimum amount filter")
    max_amount: Optional[float] = Field(None, ge=0, description="Maximum amount filter")
    
class ReceiptListResponse(BaseModel):
    """Receipt listing response"""
    receipts: List[ReceiptBasicInfo]
    total_count: int
    page: int
    limit: int
    total_amount: float
    
    class Config:
        from_attributes = True

# ========================================
# API ENDPOINTS
# ========================================

@router.get("/", response_model=ReceiptListResponse)
def get_receipts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=500, description="Records per page"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    pledge_id: Optional[int] = Query(None, description="Filter by pledge ID"),
    payment_type: Optional[str] = Query(None, description="Filter by payment type"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    from_date: Optional[date] = Query(None, description="Start date filter"),
    to_date: Optional[date] = Query(None, description="End date filter"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get paginated list of payment receipts with filtering options.
    
    Features:
    - Pagination support
    - Multiple filter options
    - Sorting capabilities
    - Total amount calculation
    """
    try:
        # Build base query
        query = db.query(
            PledgePaymentModel,
            CustomerModel.name.label("customer_name"),
            PledgeModel.pledge_no
        ).join(
            PledgeModel, PledgePaymentModel.pledge_id == PledgeModel.pledge_id
        ).join(
            CustomerModel, PledgeModel.customer_id == CustomerModel.id
        ).filter(
            PledgePaymentModel.company_id == current_user.company_id
        )
        
        # Apply filters
        if customer_id:
            query = query.filter(PledgeModel.customer_id == customer_id)
        
        if pledge_id:
            query = query.filter(PledgePaymentModel.pledge_id == pledge_id)
            
        if payment_type:
            query = query.filter(PledgePaymentModel.payment_type == payment_type)
            
        if payment_method:
            query = query.filter(PledgePaymentModel.payment_method == payment_method)
            
        if from_date:
            query = query.filter(PledgePaymentModel.payment_date >= from_date)
            
        if to_date:
            query = query.filter(PledgePaymentModel.payment_date <= to_date)
        
        # Get total count and amount before pagination
        total_count = query.count()
        total_amount = query.with_entities(
            func.sum(PledgePaymentModel.amount)
        ).scalar() or 0.0
        
        # Apply sorting
        sort_field = getattr(PledgePaymentModel, sort_by, PledgePaymentModel.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))
        
        # Apply pagination
        skip = (page - 1) * limit
        results = query.offset(skip).limit(limit).all()
        
        # Format response
        receipts = []
        for payment, customer_name, pledge_no in results:
            receipts.append(ReceiptBasicInfo(
                payment_id=payment.payment_id,
                receipt_no=payment.receipt_no,
                payment_date=payment.payment_date,
                customer_name=customer_name,
                pledge_no=pledge_no,
                amount=payment.amount,
                payment_type=payment.payment_type,
                payment_method=payment.payment_method,
                created_at=payment.created_at
            ))
        
        return ReceiptListResponse(
            receipts=receipts,
            total_count=total_count,
            page=page,
            limit=limit,
            total_amount=float(total_amount)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving receipts: {str(e)}"
        )

@router.get("/receipt/{receipt_no}", response_model=ReceiptDetailInfo)
def get_receipt_by_number(
    receipt_no: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get detailed receipt information by receipt number.
    
    Returns complete receipt details suitable for printing or PDF generation.
    """
    try:
        # Query with all related information
        result = db.query(
            PledgePaymentModel,
            CustomerModel,
            PledgeModel,
            CompanyModel,
            UserModel.username.label("staff_name")
        ).join(
            PledgeModel, PledgePaymentModel.pledge_id == PledgeModel.pledge_id
        ).join(
            CustomerModel, PledgeModel.customer_id == CustomerModel.id
        ).join(
            CompanyModel, PledgePaymentModel.company_id == CompanyModel.id
        ).join(
            UserModel, PledgePaymentModel.created_by == UserModel.id
        ).filter(
            PledgePaymentModel.receipt_no == receipt_no,
            PledgePaymentModel.company_id == current_user.company_id
        ).first()
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Receipt '{receipt_no}' not found"
            )
        
        payment, customer, pledge, company, staff_name = result
        
        return ReceiptDetailInfo(
            payment_id=payment.payment_id,
            receipt_no=payment.receipt_no,
            payment_date=payment.payment_date,
            payment_type=payment.payment_type,
            payment_method=payment.payment_method,
            bank_reference=payment.bank_reference,
            amount=payment.amount,
            interest_amount=payment.interest_amount,
            principal_amount=payment.principal_amount,
            penalty_amount=payment.penalty_amount,
            discount_amount=payment.discount_amount,
            balance_amount=payment.balance_amount,
            remarks=payment.remarks,
            created_at=payment.created_at,
            created_by=payment.created_by,
            
            # Customer info
            customer_id=customer.customer_id,
            customer_name=customer.name,
            customer_phone=customer.phone,
            customer_address=customer.address,
            
            # Pledge info
            pledge_id=pledge.pledge_id,
            pledge_no=pledge.pledge_no,
            pledge_date=pledge.pledge_date,
            loan_amount=pledge.loan_amount,
            final_amount=pledge.final_amount,
            
            # Company info
            company_name=company.name,
            company_address=company.address,
            company_phone=company.phone,
            
            # Staff info
            staff_name=staff_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving receipt details: {str(e)}"
        )

@router.get("/payment/{payment_id}", response_model=ReceiptDetailInfo)
def get_receipt_by_payment_id(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get detailed receipt information by payment ID.
    """
    try:
        # Query with all related information
        result = db.query(
            PledgePaymentModel,
            CustomerModel,
            PledgeModel,
            CompanyModel,
            UserModel.username.label("staff_name")
        ).join(
            PledgeModel, PledgePaymentModel.pledge_id == PledgeModel.pledge_id
        ).join(
            CustomerModel, PledgeModel.customer_id == CustomerModel.id
        ).join(
            CompanyModel, PledgePaymentModel.company_id == CompanyModel.id
        ).join(
            UserModel, PledgePaymentModel.created_by == UserModel.id
        ).filter(
            PledgePaymentModel.payment_id == payment_id,
            PledgePaymentModel.company_id == current_user.company_id
        ).first()
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Payment ID '{payment_id}' not found"
            )
        
        payment, customer, pledge, company, staff_name = result
        
        return ReceiptDetailInfo(
            payment_id=payment.payment_id,
            receipt_no=payment.receipt_no,
            payment_date=payment.payment_date,
            payment_type=payment.payment_type,
            payment_method=payment.payment_method,
            bank_reference=payment.bank_reference,
            amount=payment.amount,
            interest_amount=payment.interest_amount,
            principal_amount=payment.principal_amount,
            penalty_amount=payment.penalty_amount,
            discount_amount=payment.discount_amount,
            balance_amount=payment.balance_amount,
            remarks=payment.remarks,
            created_at=payment.created_at,
            created_by=payment.created_by,
            
            # Customer info
            customer_id=customer.customer_id,
            customer_name=customer.name,
            customer_phone=customer.phone,
            customer_address=customer.address,
            
            # Pledge info
            pledge_id=pledge.pledge_id,
            pledge_no=pledge.pledge_no,
            pledge_date=pledge.pledge_date,
            loan_amount=pledge.loan_amount,
            final_amount=pledge.final_amount,
            
            # Company info
            company_name=company.name,
            company_address=company.address,
            company_phone=company.phone,
            
            # Staff info
            staff_name=staff_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving receipt details: {str(e)}"
        )

@router.get("/customer/{customer_id}", response_model=ReceiptListResponse)
def get_customer_receipts(
    customer_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=500, description="Records per page"),
    from_date: Optional[date] = Query(None, description="Start date filter"),
    to_date: Optional[date] = Query(None, description="End date filter"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get all payment receipts for a specific customer.
    """
    try:
        # Verify customer exists and belongs to company
        customer = db.query(CustomerModel).filter(
            CustomerModel.id == customer_id,
            CustomerModel.company_id == current_user.company_id
        ).first()
        
        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )
        
        # Build query
        query = db.query(
            PledgePaymentModel,
            CustomerModel.name.label("customer_name"),
            PledgeModel.pledge_no
        ).join(
            PledgeModel, PledgePaymentModel.pledge_id == PledgeModel.pledge_id
        ).join(
            CustomerModel, PledgeModel.customer_id == CustomerModel.id
        ).filter(
            PledgeModel.customer_id == customer_id,
            PledgePaymentModel.company_id == current_user.company_id
        )
        
        # Apply date filters
        if from_date:
            query = query.filter(PledgePaymentModel.payment_date >= from_date)
        if to_date:
            query = query.filter(PledgePaymentModel.payment_date <= to_date)
        
        # Get totals
        total_count = query.count()
        total_amount = query.with_entities(
            func.sum(PledgePaymentModel.amount)
        ).scalar() or 0.0
        
        # Apply pagination and sorting
        skip = (page - 1) * limit
        results = query.order_by(desc(PledgePaymentModel.created_at)).offset(skip).limit(limit).all()
        
        # Format response
        receipts = []
        for payment, customer_name, pledge_no in results:
            receipts.append(ReceiptBasicInfo(
                payment_id=payment.payment_id,
                receipt_no=payment.receipt_no,
                payment_date=payment.payment_date,
                customer_name=customer_name,
                pledge_no=pledge_no,
                amount=payment.amount,
                payment_type=payment.payment_type,
                payment_method=payment.payment_method,
                created_at=payment.created_at
            ))
        
        return ReceiptListResponse(
            receipts=receipts,
            total_count=total_count,
            page=page,
            limit=limit,
            total_amount=float(total_amount)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving customer receipts: {str(e)}"
        )

@router.get("/pledge/{pledge_id}", response_model=ReceiptListResponse)
def get_pledge_receipts(
    pledge_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=500, description="Records per page"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get all payment receipts for a specific pledge.
    """
    try:
        # Verify pledge exists and belongs to company
        pledge = db.query(PledgeModel).filter(
            PledgeModel.pledge_id == pledge_id,
            PledgeModel.company_id == current_user.company_id
        ).first()
        
        if not pledge:
            raise HTTPException(
                status_code=404,
                detail="Pledge not found"
            )
        
        # Build query
        query = db.query(
            PledgePaymentModel,
            CustomerModel.name.label("customer_name"),
            PledgeModel.pledge_no
        ).join(
            PledgeModel, PledgePaymentModel.pledge_id == PledgeModel.pledge_id
        ).join(
            CustomerModel, PledgeModel.customer_id == CustomerModel.id
        ).filter(
            PledgePaymentModel.pledge_id == pledge_id,
            PledgePaymentModel.company_id == current_user.company_id
        )
        
        # Get totals
        total_count = query.count()
        total_amount = query.with_entities(
            func.sum(PledgePaymentModel.amount)
        ).scalar() or 0.0
        
        # Apply pagination and sorting
        skip = (page - 1) * limit
        results = query.order_by(desc(PledgePaymentModel.created_at)).offset(skip).limit(limit).all()
        
        # Format response
        receipts = []
        for payment, customer_name, pledge_no in results:
            receipts.append(ReceiptBasicInfo(
                payment_id=payment.payment_id,
                receipt_no=payment.receipt_no,
                payment_date=payment.payment_date,
                customer_name=customer_name,
                pledge_no=pledge_no,
                amount=payment.amount,
                payment_type=payment.payment_type,
                payment_method=payment.payment_method,
                created_at=payment.created_at
            ))
        
        return ReceiptListResponse(
            receipts=receipts,
            total_count=total_count,
            page=page,
            limit=limit,
            total_amount=float(total_amount)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving pledge receipts: {str(e)}"
        )

@router.post("/search", response_model=ReceiptListResponse)
def search_receipts(
    search_params: ReceiptSearchRequest,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=500, description="Records per page"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Advanced search for payment receipts with multiple criteria.
    
    Supports partial matching for text fields and range filtering for dates and amounts.
    """
    try:
        # Build base query
        query = db.query(
            PledgePaymentModel,
            CustomerModel.name.label("customer_name"),
            PledgeModel.pledge_no
        ).join(
            PledgeModel, PledgePaymentModel.pledge_id == PledgeModel.pledge_id
        ).join(
            CustomerModel, PledgeModel.customer_id == CustomerModel.id
        ).filter(
            PledgePaymentModel.company_id == current_user.company_id
        )
        
        # Apply search filters
        if search_params.receipt_no:
            query = query.filter(
                PledgePaymentModel.receipt_no.ilike(f"%{search_params.receipt_no}%")
            )
        
        if search_params.customer_name:
            query = query.filter(
                CustomerModel.name.ilike(f"%{search_params.customer_name}%")
            )
        
        if search_params.pledge_no:
            query = query.filter(
                PledgeModel.pledge_no.ilike(f"%{search_params.pledge_no}%")
            )
        
        if search_params.payment_type:
            query = query.filter(PledgePaymentModel.payment_type == search_params.payment_type)
        
        if search_params.payment_method:
            query = query.filter(PledgePaymentModel.payment_method == search_params.payment_method)
        
        if search_params.from_date:
            query = query.filter(PledgePaymentModel.payment_date >= search_params.from_date)
        
        if search_params.to_date:
            query = query.filter(PledgePaymentModel.payment_date <= search_params.to_date)
        
        if search_params.min_amount:
            query = query.filter(PledgePaymentModel.amount >= search_params.min_amount)
        
        if search_params.max_amount:
            query = query.filter(PledgePaymentModel.amount <= search_params.max_amount)
        
        # Get totals
        total_count = query.count()
        total_amount = query.with_entities(
            func.sum(PledgePaymentModel.amount)
        ).scalar() or 0.0
        
        # Apply pagination and sorting
        skip = (page - 1) * limit
        results = query.order_by(desc(PledgePaymentModel.created_at)).offset(skip).limit(limit).all()
        
        # Format response
        receipts = []
        for payment, customer_name, pledge_no in results:
            receipts.append(ReceiptBasicInfo(
                payment_id=payment.payment_id,
                receipt_no=payment.receipt_no,
                payment_date=payment.payment_date,
                customer_name=customer_name,
                pledge_no=pledge_no,
                amount=payment.amount,
                payment_type=payment.payment_type,
                payment_method=payment.payment_method,
                created_at=payment.created_at
            ))
        
        return ReceiptListResponse(
            receipts=receipts,
            total_count=total_count,
            page=page,
            limit=limit,
            total_amount=float(total_amount)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching receipts: {str(e)}"
        )

@router.get("/summary", response_model=ReceiptSummary)
def get_receipt_summary(
    from_date: Optional[date] = Query(None, description="Start date filter"),
    to_date: Optional[date] = Query(None, description="End date filter"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get summary analytics for payment receipts.
    
    Includes counts, totals, and breakdowns by payment method and type.
    """
    try:
        # Build base query
        query = db.query(PledgePaymentModel).filter(
            PledgePaymentModel.company_id == current_user.company_id
        )
        
        # Apply date filters
        if from_date:
            query = query.filter(PledgePaymentModel.payment_date >= from_date)
        if to_date:
            query = query.filter(PledgePaymentModel.payment_date <= to_date)
        
        # Get total count and amount
        total_receipts = query.count()
        total_amount = query.with_entities(
            func.sum(PledgePaymentModel.amount)
        ).scalar() or 0.0
        
        # Get payment method breakdown
        payment_methods = {}
        method_results = query.with_entities(
            PledgePaymentModel.payment_method,
            func.count(PledgePaymentModel.payment_id),
            func.sum(PledgePaymentModel.amount)
        ).group_by(PledgePaymentModel.payment_method).all()
        
        for method, count, amount in method_results:
            payment_methods[method] = {
                "count": count,
                "amount": float(amount or 0.0)
            }
        
        # Get payment type breakdown
        payment_types = {}
        type_results = query.with_entities(
            PledgePaymentModel.payment_type,
            func.count(PledgePaymentModel.payment_id),
            func.sum(PledgePaymentModel.amount)
        ).group_by(PledgePaymentModel.payment_type).all()
        
        for type_, count, amount in type_results:
            payment_types[type_] = {
                "count": count,
                "amount": float(amount or 0.0)
            }
        
        # Get date range info
        date_range = {}
        if total_receipts > 0:
            date_info = query.with_entities(
                func.min(PledgePaymentModel.payment_date),
                func.max(PledgePaymentModel.payment_date)
            ).first()
            
            date_range = {
                "earliest_payment": date_info[0].isoformat() if date_info[0] else None,
                "latest_payment": date_info[1].isoformat() if date_info[1] else None
            }
        
        return ReceiptSummary(
            total_receipts=total_receipts,
            total_amount=float(total_amount),
            payment_methods=payment_methods,
            payment_types=payment_types,
            date_range=date_range
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating receipt summary: {str(e)}"
        )

@router.get("/latest", response_model=List[ReceiptBasicInfo])
def get_latest_receipts(
    count: int = Query(10, ge=1, le=100, description="Number of latest receipts"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get the latest payment receipts for quick access.
    """
    try:
        results = db.query(
            PledgePaymentModel,
            CustomerModel.name.label("customer_name"),
            PledgeModel.pledge_no
        ).join(
            PledgeModel, PledgePaymentModel.pledge_id == PledgeModel.pledge_id
        ).join(
            CustomerModel, PledgeModel.customer_id == CustomerModel.id
        ).filter(
            PledgePaymentModel.company_id == current_user.company_id
        ).order_by(
            desc(PledgePaymentModel.created_at)
        ).limit(count).all()
        
        receipts = []
        for payment, customer_name, pledge_no in results:
            receipts.append(ReceiptBasicInfo(
                payment_id=payment.payment_id,
                receipt_no=payment.receipt_no,
                payment_date=payment.payment_date,
                customer_name=customer_name,
                pledge_no=pledge_no,
                amount=payment.amount,
                payment_type=payment.payment_type,
                payment_method=payment.payment_method,
                created_at=payment.created_at
            ))
        
        return receipts
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving latest receipts: {str(e)}"
        )

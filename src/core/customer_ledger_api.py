"""
Customer Ledger API - Customer Account Statement and Ledger Reports
Provides comprehensive customer ledger reports with date range and financial year options
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, desc, asc
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from pydantic import BaseModel, Field

from src.core.database import get_db
from src.core.models import (
    Customer as CustomerModel, 
    LedgerEntry as LedgerEntryModel, 
    VoucherMaster as VoucherMasterModel, 
    MasterAccount as MasterAccountModel,
    User as UserModel
)
from src.auth.auth import get_current_user, get_current_admin_user

router = APIRouter(prefix="/api/v1/customer-ledger", tags=["Customer Ledger Reports"])

# Pydantic Models
class LedgerEntryDetail(BaseModel):
    entry_date: date
    voucher_id: int
    voucher_type: str
    voucher_no: str
    narration: Optional[str] = None
    debit: float = 0.0
    credit: float = 0.0
    running_balance: float = 0.0
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None

class CustomerLedgerSummary(BaseModel):
    customer_id: int
    customer_name: str
    account_code: str
    opening_balance: float
    closing_balance: float
    total_debit: float
    total_credit: float
    net_movement: float
    transaction_count: int
    period_start: date
    period_end: date

class CustomerLedgerResponse(BaseModel):
    summary: CustomerLedgerSummary
    entries: List[LedgerEntryDetail]
    balance_verification: Dict[str, float]

class FinancialYearSummary(BaseModel):
    financial_year: str  # e.g., "2024-25"
    start_date: date
    end_date: date
    opening_balance: float
    closing_balance: float
    total_debits: float
    total_credits: float
    net_movement: float
    transaction_count: int
    months_summary: List[Dict[str, Any]]

# Helper Functions
def get_financial_year_dates(year: int) -> tuple:
    """Get financial year start and end dates (April 1 to March 31)"""
    start_date = date(year, 4, 1)
    end_date = date(year + 1, 3, 31)
    return start_date, end_date

def calculate_opening_balance(db: Session, customer_id: int, start_date: date) -> float:
    """Calculate opening balance before the start date"""
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not customer or not customer.coa_account_id:
        return 0.0
    
    # Sum all transactions before start_date
    result = db.query(
        func.sum(LedgerEntryModel.credit - LedgerEntryModel.debit).label('opening_balance')
    ).join(
        VoucherMasterModel, LedgerEntryModel.voucher_id == VoucherMasterModel.voucher_id
    ).filter(
        LedgerEntryModel.account_id == customer.coa_account_id,
        VoucherMasterModel.voucher_date < start_date
    ).first()
    
    return float(result.opening_balance) if result.opening_balance else 0.0

# API Endpoints
@router.get("/customer/{customer_id}/statement", response_model=CustomerLedgerResponse)
async def get_customer_ledger_statement(
    customer_id: int,
    start_date: date = Query(..., description="Start date for ledger statement"),
    end_date: date = Query(..., description="End date for ledger statement"),
    include_zero_balance: bool = Query(False, description="Include entries with zero amounts"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Get detailed customer ledger statement for date range
    Shows all transactions, running balance, opening and closing balance
    """
    
    # Validate customer
    customer = db.query(CustomerModel).filter(
        CustomerModel.id == customer_id,
        CustomerModel.company_id == current_user.company_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if not customer.coa_account_id:
        raise HTTPException(status_code=400, detail="Customer does not have a Chart of Accounts account")
    
    # Validate date range
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    # Calculate opening balance
    opening_balance = calculate_opening_balance(db, customer_id, start_date)
    
    # Get ledger entries for the period
    query = db.query(
        LedgerEntryModel,
        VoucherMasterModel,
        MasterAccountModel
    ).join(
        VoucherMasterModel, LedgerEntryModel.voucher_id == VoucherMasterModel.voucher_id
    ).join(
        MasterAccountModel, LedgerEntryModel.account_id == MasterAccountModel.account_id
    ).filter(
        LedgerEntryModel.account_id == customer.coa_account_id,
        VoucherMasterModel.voucher_date.between(start_date, end_date),
        VoucherMasterModel.company_id == current_user.company_id
    ).order_by(
        VoucherMasterModel.voucher_date.asc(),
        VoucherMasterModel.voucher_id.asc(),
        LedgerEntryModel.entry_id.asc()
    )
    
    if not include_zero_balance:
        query = query.filter(LedgerEntryModel.amount > 0)
    
    results = query.all()
    
    # Process entries and calculate running balance
    entries = []
    running_balance = opening_balance
    total_debit = 0.0
    total_credit = 0.0
    
    for ledger_entry, voucher_master, master_account in results:
        debit = ledger_entry.debit or 0.0
        credit = ledger_entry.credit or 0.0
        
        # Update running balance (for liability account: credit increases, debit decreases)
        running_balance = running_balance + credit - debit
        
        total_debit += debit
        total_credit += credit
        
        entry_detail = LedgerEntryDetail(
            entry_date=voucher_master.voucher_date,
            voucher_id=voucher_master.voucher_id,
            voucher_type=voucher_master.voucher_type,
            voucher_no=getattr(voucher_master, 'master_voucher_no', f"V{voucher_master.voucher_id:06d}"),
            narration=ledger_entry.narration,
            debit=debit,
            credit=credit,
            running_balance=running_balance,
            reference_type=ledger_entry.reference_type,
            reference_id=ledger_entry.reference_id
        )
        entries.append(entry_detail)
    
    closing_balance = running_balance
    net_movement = closing_balance - opening_balance
    
    # Create summary
    summary = CustomerLedgerSummary(
        customer_id=customer_id,
        customer_name=customer.name,
        account_code=customer.acc_code or f"CUST-{customer_id}",
        opening_balance=opening_balance,
        closing_balance=closing_balance,
        total_debit=total_debit,
        total_credit=total_credit,
        net_movement=net_movement,
        transaction_count=len(entries),
        period_start=start_date,
        period_end=end_date
    )
    
    # Balance verification
    balance_verification = {
        "calculated_closing": opening_balance + total_credit - total_debit,
        "running_balance_closing": closing_balance,
        "difference": abs((opening_balance + total_credit - total_debit) - closing_balance),
        "is_balanced": abs((opening_balance + total_credit - total_debit) - closing_balance) < 0.01
    }
    
    return CustomerLedgerResponse(
        summary=summary,
        entries=entries,
        balance_verification=balance_verification
    )

@router.get("/customer/{customer_id}/financial-year-summary", response_model=FinancialYearSummary)
async def get_customer_financial_year_summary(
    customer_id: int,
    financial_year: int = Query(..., description="Financial year (e.g., 2024 for FY 2024-25)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Get customer ledger summary for entire financial year
    Includes month-wise breakdown and yearly totals
    """
    
    # Validate customer
    customer = db.query(CustomerModel).filter(
        CustomerModel.id == customer_id,
        CustomerModel.company_id == current_user.company_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if not customer.coa_account_id:
        raise HTTPException(status_code=400, detail="Customer does not have a Chart of Accounts account")
    
    # Get financial year dates
    fy_start, fy_end = get_financial_year_dates(financial_year)
    
    # Calculate opening balance for FY
    fy_opening_balance = calculate_opening_balance(db, customer_id, fy_start)
    
    # Get FY totals
    fy_totals = db.query(
        func.sum(LedgerEntryModel.debit).label('total_debits'),
        func.sum(LedgerEntryModel.credit).label('total_credits'),
        func.count(LedgerEntryModel.entry_id).label('transaction_count')
    ).join(
        VoucherMasterModel, LedgerEntryModel.voucher_id == VoucherMasterModel.voucher_id
    ).filter(
        LedgerEntryModel.account_id == customer.coa_account_id,
        VoucherMasterModel.voucher_date.between(fy_start, fy_end),
        VoucherMasterModel.company_id == current_user.company_id
    ).first()
    
    total_debits = float(fy_totals.total_debits) if fy_totals.total_debits else 0.0
    total_credits = float(fy_totals.total_credits) if fy_totals.total_credits else 0.0
    transaction_count = fy_totals.transaction_count or 0
    
    fy_closing_balance = fy_opening_balance + total_credits - total_debits
    net_movement = fy_closing_balance - fy_opening_balance
    
    # Get month-wise summary
    months_summary = []
    current_date = fy_start
    
    while current_date <= fy_end:
        # Get month start and end
        month_start = current_date.replace(day=1)
        if current_date.month == 12:
            month_end = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
        
        # Ensure we don't go beyond FY end
        month_end = min(month_end, fy_end)
        
        # Get month totals
        month_totals = db.query(
            func.sum(LedgerEntryModel.debit).label('month_debits'),
            func.sum(LedgerEntryModel.credit).label('month_credits'),
            func.count(LedgerEntryModel.entry_id).label('month_transactions')
        ).join(
            VoucherMasterModel, LedgerEntryModel.voucher_id == VoucherMasterModel.voucher_id
        ).filter(
            LedgerEntryModel.account_id == customer.coa_account_id,
            VoucherMasterModel.voucher_date.between(month_start, month_end),
            VoucherMasterModel.company_id == current_user.company_id
        ).first()
        
        month_debits = float(month_totals.month_debits) if month_totals.month_debits else 0.0
        month_credits = float(month_totals.month_credits) if month_totals.month_credits else 0.0
        month_transactions = month_totals.month_transactions or 0
        
        months_summary.append({
            "month": current_date.strftime("%B %Y"),
            "month_start": month_start,
            "month_end": month_end,
            "debits": month_debits,
            "credits": month_credits,
            "net_movement": month_credits - month_debits,
            "transactions": month_transactions
        })
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
        
        if current_date > fy_end:
            break
    
    return FinancialYearSummary(
        financial_year=f"{financial_year}-{str(financial_year + 1)[-2:]}",
        start_date=fy_start,
        end_date=fy_end,
        opening_balance=fy_opening_balance,
        closing_balance=fy_closing_balance,
        total_debits=total_debits,
        total_credits=total_credits,
        net_movement=net_movement,
        transaction_count=transaction_count,
        months_summary=months_summary
    )

@router.get("/customer/{customer_id}/current-balance")
async def get_customer_current_balance(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get customer's current balance from ledger"""
    
    # Import the existing function
    from src.managers.pledge_accounting_manager import get_customer_balance_from_ledger
    
    try:
        balance_info = get_customer_balance_from_ledger(db, customer_id)
        return balance_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating balance: {str(e)}")

@router.get("/customers/ledger-summary")
async def get_all_customers_ledger_summary(
    as_of_date: Optional[date] = Query(None, description="Get balances as of specific date (default: today)"),
    min_balance: Optional[float] = Query(None, description="Filter customers with minimum balance"),
    max_balance: Optional[float] = Query(None, description="Filter customers with maximum balance"),
    has_transactions: Optional[bool] = Query(None, description="Filter customers with/without transactions"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Get ledger summary for all customers
    Shows current balances and transaction counts
    """
    
    as_of_date = as_of_date or date.today()
    
    # Get all customers with COA accounts
    customers_query = db.query(CustomerModel).filter(
        CustomerModel.company_id == current_user.company_id,
        CustomerModel.coa_account_id.isnot(None)
    )
    
    customers = customers_query.all()
    
    customer_summaries = []
    
    for customer in customers:
        # Calculate balance as of date
        balance_result = db.query(
            func.sum(LedgerEntryModel.credit - LedgerEntryModel.debit).label('balance'),
            func.count(LedgerEntryModel.entry_id).label('transaction_count')
        ).join(
            VoucherMasterModel, LedgerEntryModel.voucher_id == VoucherMasterModel.voucher_id
        ).filter(
            LedgerEntryModel.account_id == customer.coa_account_id,
            VoucherMasterModel.voucher_date <= as_of_date,
            VoucherMasterModel.company_id == current_user.company_id
        ).first()
        
        balance = float(balance_result.balance) if balance_result.balance else 0.0
        transaction_count = balance_result.transaction_count or 0
        
        # Apply filters
        if min_balance is not None and balance < min_balance:
            continue
        if max_balance is not None and balance > max_balance:
            continue
        if has_transactions is not None:
            if has_transactions and transaction_count == 0:
                continue
            if not has_transactions and transaction_count > 0:
                continue
        
        customer_summaries.append({
            "customer_id": customer.id,
            "customer_name": customer.name,
            "account_code": customer.acc_code or f"CUST-{customer.id}",
            "current_balance": balance,
            "transaction_count": transaction_count,
            "phone": customer.phone,
            "has_coa_account": True
        })
    
    # Sort by balance (highest first)
    customer_summaries.sort(key=lambda x: x['current_balance'], reverse=True)
    
    return {
        "as_of_date": as_of_date,
        "total_customers": len(customer_summaries),
        "total_outstanding": sum(c['current_balance'] for c in customer_summaries),
        "customers": customer_summaries
    }
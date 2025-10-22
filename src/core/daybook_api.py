# type: ignore
# pylint: disable=all
# mypy: ignore-errors
"""
Daybook API - Daily Transaction Summary System
Provides comprehensive daily transaction reports and summaries
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm.session import Session  # type: ignore
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from src.core.database import get_db
from src.core.models import VoucherMaster, LedgerEntry, MasterAccount, Company, User
from pydantic import BaseModel
from sqlalchemy import func, and_, or_, case  # type: ignore

router = APIRouter(prefix="/api/v1/daybook", tags=["Daybook"])

def calculate_opening_balance(db: Session, company_id: int, transaction_date: date) -> float:
    """
    Calculate opening balance based on net cash flow till previous day
    """
    try:
        previous_date = transaction_date - timedelta(days=1)
        
        # Simple approach: Get cash account balance till previous day
        balance_query = db.query(  # type: ignore
            func.sum(  # type: ignore
                case([
                    (LedgerEntry.dr_cr == 'D', LedgerEntry.amount),
                    (LedgerEntry.dr_cr == 'C', -LedgerEntry.amount)
                ], else_=0)  # type: ignore
            ).label('net_balance')
        ).select_from(  # type: ignore
            LedgerEntry
        ).join(  # type: ignore
            VoucherMaster, LedgerEntry.voucher_id == VoucherMaster.voucher_id
        ).join(  # type: ignore
            MasterAccount, LedgerEntry.account_id == MasterAccount.account_id
        ).filter(  # type: ignore
            VoucherMaster.voucher_date <= previous_date,
            VoucherMaster.company_id == company_id,
            MasterAccount.account_code == '1001'  # Cash account only
        )
        
        result = balance_query.first()
        opening_balance = float(result.net_balance) if result and result.net_balance else 0.0
        
        return opening_balance
        
    except Exception as e:
        print(f"Error calculating opening balance: {e}")
        return 0.0

# Pydantic Models
class DaybookEntryBase(BaseModel):
    entry_date: date
    voucher_id: int
    voucher_type: str
    voucher_no: str
    account_name: str
    account_code: str
    narration: Optional[str] = None
    debit: float = 0.0
    credit: float = 0.0
    running_balance: float = 0.0

class DaybookSummary(BaseModel):
    date: date
    total_vouchers: int
    total_debit: float
    total_credit: float
    balance_difference: float
    voucher_types: Dict[str, int]

class DayBookResponse(BaseModel):
    summary: DaybookSummary
    entries: List[DaybookEntryBase]
    opening_balance: float
    closing_balance: float

class DateRangeRequest(BaseModel):
    start_date: date
    end_date: date
    company_id: int
    account_filter: Optional[str] = None
    voucher_type_filter: Optional[str] = None

@router.get("/daily-summary")
async def get_daily_summary(
    transaction_date: date = Query(..., description="Date for daybook summary"),
    company_id: int = Query(..., description="Company ID"),
    account_type: Optional[str] = Query(None, description="Filter by account type (Asset, Liability, Income, Expense, Equity)"),
    voucher_type: Optional[str] = Query(None, description="Filter by voucher type (Pledge, Receipt, Payment, Journal, Auction)"),
    db: Session = Depends(get_db)
):
    """Get complete daybook summary for a specific date"""
    
    # Base query for the specific date
    query = db.query(  # type: ignore
        LedgerEntry,
        VoucherMaster,
        MasterAccount
    ).join(  # type: ignore
        VoucherMaster, LedgerEntry.voucher_id == VoucherMaster.voucher_id
    ).join(  # type: ignore
        MasterAccount, LedgerEntry.account_id == MasterAccount.account_id
    ).filter(  # type: ignore
        VoucherMaster.voucher_date == transaction_date,
        VoucherMaster.company_id == company_id
    )
    
    # Apply filters
    if account_type:
        query = query.filter(MasterAccount.account_type == account_type)  # type: ignore
    
    if voucher_type:
        query = query.filter(VoucherMaster.voucher_type == voucher_type)  # type: ignore
    
    # Order by voucher_id and entry_id
    results = query.order_by(VoucherMaster.voucher_id, LedgerEntry.entry_id).all()  # type: ignore
    
    # Calculate opening balance from previous day's closing balance
    opening_balance = calculate_opening_balance(db, company_id, transaction_date)
    
    if not results:
        return {
            "summary": {
                "date": transaction_date,
                "total_vouchers": 0,
                "total_debit": 0.0,
                "total_credit": 0.0,
                "balance_difference": 0.0,
                "voucher_types": {}
            },
            "entries": [],
            "opening_balance": opening_balance,
            "closing_balance": opening_balance
        }
    
    # Process entries
    entries = []
    total_debit = 0.0
    total_credit = 0.0
    voucher_types = {}
    voucher_ids = set()
    
    for ledger_entry, voucher_master, master_account in results:
        voucher_ids.add(voucher_master.voucher_id)
        
        # Count voucher types
        voucher_type_key = voucher_master.voucher_type
        voucher_types[voucher_type_key] = voucher_types.get(voucher_type_key, 0) + 1
        
        # Calculate amounts
        debit_amount = ledger_entry.amount if ledger_entry.dr_cr == 'D' else 0.0
        credit_amount = ledger_entry.amount if ledger_entry.dr_cr == 'C' else 0.0
        
        total_debit += debit_amount
        total_credit += credit_amount
        
        entries.append(DaybookEntryBase(
            entry_date=transaction_date,
            voucher_id=voucher_master.voucher_id,
            voucher_type=voucher_master.voucher_type,
            voucher_no=f"{voucher_master.voucher_type}-{voucher_master.voucher_id:06d}",
            account_name=master_account.account_name,
            account_code=master_account.account_code,
            narration=ledger_entry.narration or voucher_master.narration,
            debit=debit_amount,
            credit=credit_amount,
            running_balance=0.0  # Will calculate below
        ))
    
    # Calculate running balance starting from opening balance
    running_balance = opening_balance
    for entry in entries:
        running_balance += (entry.debit - entry.credit)
        entry.running_balance = running_balance
    
    # Create summary
    summary = DaybookSummary(
        date=transaction_date,
        total_vouchers=len(voucher_ids),
        total_debit=total_debit,
        total_credit=total_credit,
        balance_difference=total_debit - total_credit,
        voucher_types=voucher_types
    )
    
    # Calculate closing balance: opening + today's cash movements
    try:
        today_cash_movement = db.query(  # type: ignore
            func.sum(  # type: ignore
                case([
                    (LedgerEntry.dr_cr == 'D', LedgerEntry.amount),
                    (LedgerEntry.dr_cr == 'C', -LedgerEntry.amount)
                ], else_=0)  # type: ignore
            ).label('movement')
        ).select_from(  # type: ignore
            LedgerEntry
        ).join(  # type: ignore
            VoucherMaster, LedgerEntry.voucher_id == VoucherMaster.voucher_id
        ).join(  # type: ignore
            MasterAccount, LedgerEntry.account_id == MasterAccount.account_id
        ).filter(  # type: ignore
            VoucherMaster.voucher_date == transaction_date,
            VoucherMaster.company_id == company_id,
            MasterAccount.account_code == '1001'  # Cash account only
        ).first()
        
        today_movement = float(today_cash_movement.movement) if today_cash_movement and today_cash_movement.movement else 0.0
        closing_balance = opening_balance + today_movement
        
    except Exception as e:
        print(f"Error calculating closing balance: {e}")
        closing_balance = opening_balance
    
    return DayBookResponse(
        summary=summary,
        entries=entries,
        opening_balance=opening_balance,
        closing_balance=closing_balance
    )

@router.get("/date-range-summary")
async def get_date_range_summary(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    company_id: int = Query(..., description="Company ID"),
    account_type: Optional[str] = Query(None, description="Filter by account type"),
    voucher_type: Optional[str] = Query(None, description="Filter by voucher type"),
    db: Session = Depends(get_db)
):
    """Get daybook summary for a date range"""
    
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    
    # Query for date range
    query = db.query(  # type: ignore
        VoucherMaster.voucher_date,
        func.count(func.distinct(VoucherMaster.voucher_id)).label('total_vouchers'),  # type: ignore
        func.sum(  # type: ignore
            func.case([(LedgerEntry.dr_cr == 'D', LedgerEntry.amount)], else_=0)  # type: ignore
        ).label('total_debit'),
        func.sum(  # type: ignore
            func.case([(LedgerEntry.dr_cr == 'C', LedgerEntry.amount)], else_=0)  # type: ignore
        ).label('total_credit'),
        VoucherMaster.voucher_type
    ).join(  # type: ignore
        LedgerEntry, VoucherMaster.voucher_id == LedgerEntry.voucher_id
    ).join(  # type: ignore
        MasterAccount, LedgerEntry.account_id == MasterAccount.account_id
    ).filter(  # type: ignore
        VoucherMaster.voucher_date.between(start_date, end_date),
        VoucherMaster.company_id == company_id
    )
    
    # Apply filters
    if account_type:
        query = query.filter(MasterAccount.account_type == account_type)  # type: ignore
    
    if voucher_type:
        query = query.filter(VoucherMaster.voucher_type == voucher_type)  # type: ignore
    
    # Group by date and voucher type
    results = query.group_by(  # type: ignore
        VoucherMaster.voucher_date, 
        VoucherMaster.voucher_type
    ).order_by(VoucherMaster.voucher_date).all()  # type: ignore
    
    # Process results by date
    daily_summaries = {}
    for result in results:
        date_key = result.voucher_date
        if date_key not in daily_summaries:
            daily_summaries[date_key] = {
                "date": date_key,
                "total_vouchers": 0,
                "total_debit": 0.0,
                "total_credit": 0.0,
                "balance_difference": 0.0,
                "voucher_types": {}
            }
        
        daily_summaries[date_key]["total_vouchers"] += result.total_vouchers or 0
        daily_summaries[date_key]["total_debit"] += float(result.total_debit or 0)
        daily_summaries[date_key]["total_credit"] += float(result.total_credit or 0)
        daily_summaries[date_key]["voucher_types"][result.voucher_type] = result.total_vouchers or 0
    
    # Calculate balance difference
    for summary in daily_summaries.values():
        summary["balance_difference"] = summary["total_debit"] - summary["total_credit"]
    
    return {
        "date_range": {
            "start_date": start_date,
            "end_date": end_date,
            "total_days": len(daily_summaries)
        },
        "daily_summaries": list(daily_summaries.values()),
        "grand_total": {
            "total_debit": sum(s["total_debit"] for s in daily_summaries.values()),
            "total_credit": sum(s["total_credit"] for s in daily_summaries.values()),
            "total_vouchers": sum(s["total_vouchers"] for s in daily_summaries.values()),
            "net_balance": sum(s["balance_difference"] for s in daily_summaries.values())
        }
    }

@router.get("/account-wise-summary")
async def get_account_wise_summary(
    transaction_date: date = Query(..., description="Date for account-wise summary"),
    company_id: int = Query(..., description="Company ID"),
    account_type: Optional[str] = Query(None, description="Filter by account type"),
    db: Session = Depends(get_db)
):
    """Get account-wise transaction summary for a specific date"""
    
    try:
        query = db.query(  # type: ignore
            MasterAccount.account_name,
            MasterAccount.account_code,
            MasterAccount.account_type,
            func.sum(  # type: ignore
                case((LedgerEntry.dr_cr == 'D', LedgerEntry.amount), else_=0)  # type: ignore
            ).label('total_debit'),
            func.sum(  # type: ignore
                case((LedgerEntry.dr_cr == 'C', LedgerEntry.amount), else_=0)  # type: ignore
            ).label('total_credit'),
            func.count(LedgerEntry.entry_id).label('transaction_count')  # type: ignore
        ).join(  # type: ignore
            LedgerEntry, MasterAccount.account_id == LedgerEntry.account_id
        ).join(  # type: ignore
            VoucherMaster, LedgerEntry.voucher_id == VoucherMaster.voucher_id
        ).filter(  # type: ignore
            VoucherMaster.voucher_date == transaction_date,
            VoucherMaster.company_id == company_id
        )
        
        if account_type:
            query = query.filter(MasterAccount.account_type == account_type)  # type: ignore
        
        results = query.group_by(  # type: ignore
            MasterAccount.account_name,
            MasterAccount.account_code,
            MasterAccount.account_type
        ).order_by(MasterAccount.account_code).all()  # type: ignore
        
        account_summaries = []
        for result in results:
            account_summaries.append({
                "account_name": result.account_name,
                "account_code": result.account_code,
                "account_type": result.account_type,
                "total_debit": float(result.total_debit or 0),
                "total_credit": float(result.total_credit or 0),
                "net_balance": float(result.total_debit or 0) - float(result.total_credit or 0),
                "transaction_count": result.transaction_count
            })
        
        return {
            "date": transaction_date,
            "account_summaries": account_summaries,
            "totals": {
                "total_debit": sum(acc["total_debit"] for acc in account_summaries),
                "total_credit": sum(acc["total_credit"] for acc in account_summaries),
                "total_accounts": len(account_summaries),
                "total_transactions": sum(acc["transaction_count"] for acc in account_summaries)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in account-wise summary: {str(e)}"
        )

@router.get("/voucher-wise-summary")
async def get_voucher_wise_summary(
    transaction_date: date = Query(..., description="Date for voucher-wise summary"),
    company_id: int = Query(..., description="Company ID"),
    voucher_type: Optional[str] = Query(None, description="Filter by voucher type"),
    db: Session = Depends(get_db)
):
    """Get voucher-wise transaction summary for a specific date"""
    
    query = db.query(  # type: ignore
        VoucherMaster.voucher_id,
        VoucherMaster.voucher_type,
        VoucherMaster.narration,
        VoucherMaster.created_at,
        func.sum(  # type: ignore
            func.case([(LedgerEntry.dr_cr == 'D', LedgerEntry.amount)], else_=0)  # type: ignore
        ).label('total_debit'),
        func.sum(  # type: ignore
            func.case([(LedgerEntry.dr_cr == 'C', LedgerEntry.amount)], else_=0)  # type: ignore
        ).label('total_credit'),
        func.count(LedgerEntry.entry_id).label('entry_count')  # type: ignore
    ).join(  # type: ignore
        LedgerEntry, VoucherMaster.voucher_id == LedgerEntry.voucher_id
    ).filter(  # type: ignore
        VoucherMaster.voucher_date == transaction_date,
        VoucherMaster.company_id == company_id
    )
    
    if voucher_type:
        query = query.filter(VoucherMaster.voucher_type == voucher_type)  # type: ignore
    
    results = query.group_by(  # type: ignore
        VoucherMaster.voucher_id,
        VoucherMaster.voucher_type,
        VoucherMaster.narration,
        VoucherMaster.created_at
    ).order_by(VoucherMaster.voucher_id).all()  # type: ignore
    
    voucher_summaries = []
    for result in results:
        voucher_summaries.append({
            "voucher_id": result.voucher_id,
            "voucher_no": f"{result.voucher_type}-{result.voucher_id:06d}",
            "voucher_type": result.voucher_type,
            "narration": result.narration,
            "created_at": result.created_at,
            "total_debit": float(result.total_debit or 0),
            "total_credit": float(result.total_credit or 0),
            "is_balanced": float(result.total_debit or 0) == float(result.total_credit or 0),
            "entry_count": result.entry_count
        })
    
    return {
        "date": transaction_date,
        "voucher_summaries": voucher_summaries,
        "totals": {
            "total_vouchers": len(voucher_summaries),
            "total_debit": sum(v["total_debit"] for v in voucher_summaries),
            "total_credit": sum(v["total_credit"] for v in voucher_summaries),
            "balanced_vouchers": sum(1 for v in voucher_summaries if v["is_balanced"]),
            "total_entries": sum(v["entry_count"] for v in voucher_summaries)
        }
    }

@router.get("/current-month-summary")
async def get_current_month_summary(
    company_id: int = Query(..., description="Company ID"),
    year: Optional[int] = Query(None, description="Year (default: current year)"),
    month: Optional[int] = Query(None, description="Month (default: current month)"),
    db: Session = Depends(get_db)
):
    """Get current month's daybook summary"""
    
    today = date.today()
    target_year = year or today.year
    target_month = month or today.month
    
    # Calculate month start and end dates
    start_date = date(target_year, target_month, 1)
    if target_month == 12:
        end_date = date(target_year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(target_year, target_month + 1, 1) - timedelta(days=1)
    
    # Get daily summaries for the month
    daily_summary_response = await get_date_range_summary(
        start_date=start_date,
        end_date=end_date,
        company_id=company_id,
        db=db
    )
    
    return {
        "month": target_month,
        "year": target_year,
        "start_date": start_date,
        "end_date": end_date,
        "month_summary": daily_summary_response
    }

@router.get("/export-daybook")
async def export_daybook_data(
    transaction_date: date = Query(..., description="Date for export"),
    company_id: int = Query(..., description="Company ID"),
    format: str = Query("json", description="Export format (json/csv)"),
    db: Session = Depends(get_db)
):
    """Export daybook data in specified format"""
    
    # Get complete daybook data
    daybook_data = await get_daily_summary(
        transaction_date=transaction_date,
        company_id=company_id,
        db=db
    )
    
    if format.lower() == "csv":
        # Convert to CSV format (you can implement CSV export here)
        csv_data = "Date,Voucher ID,Voucher Type,Account Name,Account Code,Narration,Debit,Credit,Running Balance\n"
        for entry in daybook_data["entries"]:
            csv_data += f"{entry.entry_date},{entry.voucher_id},{entry.voucher_type},{entry.account_name},{entry.account_code},{entry.narration or ''},{entry.debit},{entry.credit},{entry.running_balance}\n"
        
        return {
            "format": "csv",
            "data": csv_data,
            "filename": f"daybook_{transaction_date.strftime('%Y_%m_%d')}.csv"
        }
    
    return {
        "format": "json",
        "data": daybook_data,
        "filename": f"daybook_{transaction_date.strftime('%Y_%m_%d')}.json"
    }

"""
Financial Year Closing and Opening API
Handles year-end closing process, P&L calculation, opening balance carry-forward, and financial reports
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, desc, text, extract
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from pydantic import BaseModel, Field
import json

from src.core.database import get_db
from src.core.models import (
    Customer as CustomerModel, 
    LedgerEntry as LedgerEntryModel, 
    VoucherMaster as VoucherMasterModel, 
    MasterAccount as MasterAccountModel,
    User as UserModel,
    Company as CompanyModel
)
from src.auth.auth import get_current_user, get_current_admin_user

router = APIRouter(prefix="/api/v1/financial-year", tags=["Financial Year Management"])

# Pydantic Models
class FinancialYearClosingRequest(BaseModel):
    financial_year: int  # e.g., 2024 for FY 2024-25
    closing_date: date
    backup_before_closing: bool = True
    admin_confirmation: str = Field(..., description="Type 'CONFIRM' to proceed")
    closing_notes: Optional[str] = None

class FinancialYearOpeningRequest(BaseModel):
    financial_year: int  # e.g., 2025 for FY 2025-26
    opening_date: date
    carry_forward_balances: bool = True
    admin_confirmation: str = Field(..., description="Type 'CONFIRM' to proceed")
    opening_notes: Optional[str] = None

class AccountBalance(BaseModel):
    account_id: int
    account_code: str
    account_name: str
    account_type: str
    debit_balance: float
    credit_balance: float
    net_balance: float

class TrialBalanceResponse(BaseModel):
    as_of_date: date
    company_name: str
    total_debits: float
    total_credits: float
    is_balanced: bool
    difference: float
    accounts: List[AccountBalance]

class ProfitLossResponse(BaseModel):
    financial_year: str
    period_start: date
    period_end: date
    revenue_accounts: List[AccountBalance]
    expense_accounts: List[AccountBalance]
    total_revenue: float
    total_expenses: float
    gross_profit: float
    net_profit: float
    profit_percentage: float

class BalanceSheetResponse(BaseModel):
    as_of_date: date
    financial_year: str
    assets: List[AccountBalance]
    liabilities: List[AccountBalance]
    equity: List[AccountBalance]
    total_assets: float
    total_liabilities: float
    total_equity: float
    is_balanced: bool

class ClosingProcessStatus(BaseModel):
    step: str
    status: str  # 'pending', 'in-progress', 'completed', 'failed'
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

class FinancialYearClosingResponse(BaseModel):
    financial_year: str
    closing_date: date
    status: str  # 'success', 'failed', 'partial'
    profit_loss: ProfitLossResponse
    closing_entries_count: int
    backup_location: Optional[str] = None
    process_steps: List[ClosingProcessStatus]
    rollback_available: bool

class FinancialYearOpeningResponse(BaseModel):
    financial_year: str
    opening_date: date
    status: str
    opening_entries_count: int
    carried_forward_balances: int
    process_steps: List[ClosingProcessStatus]

# Helper Functions
def get_financial_year_dates(year: int) -> tuple:
    """Get financial year start and end dates (April 1 to March 31)"""
    start_date = date(year, 4, 1)
    end_date = date(year + 1, 3, 31)
    return start_date, end_date

def get_company_info(db: Session, company_id: int) -> CompanyModel:
    """Get company information"""
    company = db.query(CompanyModel).filter(CompanyModel.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

def validate_year_closing_eligibility(db: Session, company_id: int, financial_year: int) -> Dict[str, Any]:
    """Validate if financial year can be closed"""
    fy_start, fy_end = get_financial_year_dates(financial_year)
    
    # Check if year already closed
    existing_closing = db.query(VoucherMasterModel).filter(
        VoucherMasterModel.company_id == company_id,
        VoucherMasterModel.voucher_type == "Year-End-Closing",
        VoucherMasterModel.narration.like(f"%FY {financial_year}-{str(financial_year+1)[-2:]}%")
    ).first()
    
    if existing_closing:
        return {
            "eligible": False,
            "reason": f"Financial Year {financial_year}-{str(financial_year+1)[-2:]} already closed",
            "closing_date": existing_closing.voucher_date
        }
    
    # Check for unposted transactions
    current_date = datetime.now().date()
    if fy_end > current_date:
        return {
            "eligible": False,
            "reason": f"Financial Year {financial_year}-{str(financial_year+1)[-2:]} has not ended yet",
            "end_date": fy_end
        }
    
    # Check for pending transactions after FY end
    pending_vouchers = db.query(func.count(VoucherMasterModel.voucher_id)).filter(
        VoucherMasterModel.company_id == company_id,
        VoucherMasterModel.voucher_date <= fy_end,
        VoucherMasterModel.voucher_date >= fy_start,
        ~VoucherMasterModel.ledger_entries.any()  # Vouchers without ledger entries
    ).scalar()
    
    if pending_vouchers > 0:
        return {
            "eligible": False,
            "reason": f"There are {pending_vouchers} vouchers without ledger entries in FY {financial_year}",
            "pending_count": pending_vouchers
        }
    
    return {"eligible": True, "reason": "Financial Year is eligible for closing"}

def calculate_trial_balance(db: Session, company_id: int, as_of_date: date) -> TrialBalanceResponse:
    """Calculate trial balance as of specific date"""
    
    company = get_company_info(db, company_id)
    
    # Get all accounts with their balances
    account_balances = db.query(
        MasterAccountModel.account_id,
        MasterAccountModel.account_code,
        MasterAccountModel.account_name,
        MasterAccountModel.account_type,
        func.coalesce(func.sum(LedgerEntryModel.debit), 0).label('total_debits'),
        func.coalesce(func.sum(LedgerEntryModel.credit), 0).label('total_credits')
    ).outerjoin(
        LedgerEntryModel, MasterAccountModel.account_id == LedgerEntryModel.account_id
    ).outerjoin(
        VoucherMasterModel, LedgerEntryModel.voucher_id == VoucherMasterModel.voucher_id
    ).filter(
        MasterAccountModel.company_id == company_id,
        MasterAccountModel.is_active == True
    ).filter(
        or_(
            LedgerEntryModel.voucher_id.is_(None),  # Accounts with no transactions
            VoucherMasterModel.voucher_date <= as_of_date
        )
    ).group_by(
        MasterAccountModel.account_id,
        MasterAccountModel.account_code,
        MasterAccountModel.account_name,
        MasterAccountModel.account_type
    ).all()
    
    accounts = []
    total_debits = 0.0
    total_credits = 0.0
    
    for balance in account_balances:
        debit_balance = float(balance.total_debits) if balance.total_debits else 0.0
        credit_balance = float(balance.total_credits) if balance.total_credits else 0.0
        net_balance = debit_balance - credit_balance
        
        # For normal balances: Assets & Expenses = Debit, Liabilities & Income = Credit
        if balance.account_type in ['Asset', 'Expense']:
            if net_balance >= 0:
                debit_balance = net_balance
                credit_balance = 0.0
            else:
                debit_balance = 0.0
                credit_balance = abs(net_balance)
        else:  # Liability, Income, Equity
            if net_balance <= 0:
                credit_balance = abs(net_balance)
                debit_balance = 0.0
            else:
                credit_balance = 0.0
                debit_balance = net_balance
        
        total_debits += debit_balance
        total_credits += credit_balance
        
        accounts.append(AccountBalance(
            account_id=balance.account_id,
            account_code=balance.account_code,
            account_name=balance.account_name,
            account_type=balance.account_type,
            debit_balance=debit_balance,
            credit_balance=credit_balance,
            net_balance=net_balance
        ))
    
    difference = abs(total_debits - total_credits)
    is_balanced = difference < 0.01
    
    return TrialBalanceResponse(
        as_of_date=as_of_date,
        company_name=company.name,
        total_debits=total_debits,
        total_credits=total_credits,
        is_balanced=is_balanced,
        difference=difference,
        accounts=accounts
    )

def calculate_profit_loss(db: Session, company_id: int, financial_year: int) -> ProfitLossResponse:
    """Calculate Profit & Loss for financial year"""
    
    fy_start, fy_end = get_financial_year_dates(financial_year)
    
    # Get revenue accounts (Income type)
    revenue_query = db.query(
        MasterAccountModel.account_id,
        MasterAccountModel.account_code,
        MasterAccountModel.account_name,
        MasterAccountModel.account_type,
        func.coalesce(func.sum(LedgerEntryModel.credit - LedgerEntryModel.debit), 0).label('net_balance')
    ).join(
        LedgerEntryModel, MasterAccountModel.account_id == LedgerEntryModel.account_id
    ).join(
        VoucherMasterModel, LedgerEntryModel.voucher_id == VoucherMasterModel.voucher_id
    ).filter(
        MasterAccountModel.company_id == company_id,
        MasterAccountModel.account_type == 'Income',
        VoucherMasterModel.voucher_date.between(fy_start, fy_end)
    ).group_by(
        MasterAccountModel.account_id,
        MasterAccountModel.account_code,
        MasterAccountModel.account_name,
        MasterAccountModel.account_type
    ).all()
    
    # Get expense accounts
    expense_query = db.query(
        MasterAccountModel.account_id,
        MasterAccountModel.account_code,
        MasterAccountModel.account_name,
        MasterAccountModel.account_type,
        func.coalesce(func.sum(LedgerEntryModel.debit - LedgerEntryModel.credit), 0).label('net_balance')
    ).join(
        LedgerEntryModel, MasterAccountModel.account_id == LedgerEntryModel.account_id
    ).join(
        VoucherMasterModel, LedgerEntryModel.voucher_id == VoucherMasterModel.voucher_id
    ).filter(
        MasterAccountModel.company_id == company_id,
        MasterAccountModel.account_type == 'Expense',
        VoucherMasterModel.voucher_date.between(fy_start, fy_end)
    ).group_by(
        MasterAccountModel.account_id,
        MasterAccountModel.account_code,
        MasterAccountModel.account_name,
        MasterAccountModel.account_type
    ).all()
    
    revenue_accounts = []
    total_revenue = 0.0
    
    for rev in revenue_query:
        balance = float(rev.net_balance) if rev.net_balance else 0.0
        total_revenue += balance
        revenue_accounts.append(AccountBalance(
            account_id=rev.account_id,
            account_code=rev.account_code,
            account_name=rev.account_name,
            account_type=rev.account_type,
            debit_balance=0.0,
            credit_balance=balance,
            net_balance=balance
        ))
    
    expense_accounts = []
    total_expenses = 0.0
    
    for exp in expense_query:
        balance = float(exp.net_balance) if exp.net_balance else 0.0
        total_expenses += balance
        expense_accounts.append(AccountBalance(
            account_id=exp.account_id,
            account_code=exp.account_code,
            account_name=exp.account_name,
            account_type=exp.account_type,
            debit_balance=balance,
            credit_balance=0.0,
            net_balance=balance
        ))
    
    gross_profit = total_revenue - total_expenses
    net_profit = gross_profit  # Simplified calculation
    profit_percentage = (net_profit / total_revenue * 100) if total_revenue > 0 else 0.0
    
    return ProfitLossResponse(
        financial_year=f"{financial_year}-{str(financial_year+1)[-2:]}",
        period_start=fy_start,
        period_end=fy_end,
        revenue_accounts=revenue_accounts,
        expense_accounts=expense_accounts,
        total_revenue=total_revenue,
        total_expenses=total_expenses,
        gross_profit=gross_profit,
        net_profit=net_profit,
        profit_percentage=profit_percentage
    )

def create_year_end_closing_entries(db: Session, company_id: int, user_id: int, financial_year: int, profit_loss: ProfitLossResponse) -> tuple:
    """Create year-end closing journal entries"""
    
    closing_date = profit_loss.period_end
    
    # Create master voucher for year-end closing
    closing_voucher = VoucherMasterModel()
    closing_voucher.voucher_type = "Year-End-Closing"
    closing_voucher.voucher_date = closing_date
    closing_voucher.narration = f"Year-end closing entries for FY {financial_year}-{str(financial_year+1)[-2:]}"
    closing_voucher.company_id = company_id
    closing_voucher.created_by = user_id
    
    db.add(closing_voucher)
    db.flush()
    
    entries_created = 0
    
    # Close revenue accounts to P&L Summary
    for revenue_account in profit_loss.revenue_accounts:
        if revenue_account.credit_balance > 0:
            # Debit revenue account to close it
            revenue_closing_entry = LedgerEntryModel()
            revenue_closing_entry.voucher_id = closing_voucher.voucher_id
            revenue_closing_entry.account_id = revenue_account.account_id
            revenue_closing_entry.dr_cr = 'D'
            revenue_closing_entry.amount = revenue_account.credit_balance
            revenue_closing_entry.debit = revenue_account.credit_balance
            revenue_closing_entry.credit = 0.0
            revenue_closing_entry.narration = f"Closing {revenue_account.account_name} to P&L"
            revenue_closing_entry.reference_type = 'year_end_closing'
            revenue_closing_entry.reference_id = closing_voucher.voucher_id
            revenue_closing_entry.transaction_date = closing_date
            
            db.add(revenue_closing_entry)
            entries_created += 1
    
    # Close expense accounts to P&L Summary
    for expense_account in profit_loss.expense_accounts:
        if expense_account.debit_balance > 0:
            # Credit expense account to close it
            expense_closing_entry = LedgerEntryModel()
            expense_closing_entry.voucher_id = closing_voucher.voucher_id
            expense_closing_entry.account_id = expense_account.account_id
            expense_closing_entry.dr_cr = 'C'
            expense_closing_entry.amount = expense_account.debit_balance
            expense_closing_entry.debit = 0.0
            expense_closing_entry.credit = expense_account.debit_balance
            expense_closing_entry.narration = f"Closing {expense_account.account_name} to P&L"
            expense_closing_entry.reference_type = 'year_end_closing'
            expense_closing_entry.reference_id = closing_voucher.voucher_id
            expense_closing_entry.transaction_date = closing_date
            
            db.add(expense_closing_entry)
            entries_created += 1
    
    # Create P&L Summary entry (net profit/loss to Retained Earnings)
    if profit_loss.net_profit != 0:
        # Find or create Retained Earnings account
        retained_earnings = db.query(MasterAccountModel).filter(
            MasterAccountModel.company_id == company_id,
            MasterAccountModel.account_code == "3002"  # Retained Earnings
        ).first()
        
        if not retained_earnings:
            # Create Retained Earnings account if it doesn't exist
            retained_earnings = MasterAccountModel()
            retained_earnings.account_code = "3002"
            retained_earnings.account_name = "Retained Earnings"
            retained_earnings.account_type = "Equity"
            retained_earnings.group_name = "Equity"
            retained_earnings.company_id = company_id
            retained_earnings.is_active = True
            
            db.add(retained_earnings)
            db.flush()
        
        # Transfer net profit to retained earnings
        profit_transfer_entry = LedgerEntryModel()
        profit_transfer_entry.voucher_id = closing_voucher.voucher_id
        profit_transfer_entry.account_id = retained_earnings.account_id
        
        if profit_loss.net_profit > 0:  # Profit
            profit_transfer_entry.dr_cr = 'C'
            profit_transfer_entry.credit = profit_loss.net_profit
            profit_transfer_entry.debit = 0.0
            profit_transfer_entry.narration = f"Net Profit for FY {financial_year}-{str(financial_year+1)[-2:]} transferred to Retained Earnings"
        else:  # Loss
            profit_transfer_entry.dr_cr = 'D'
            profit_transfer_entry.debit = abs(profit_loss.net_profit)
            profit_transfer_entry.credit = 0.0
            profit_transfer_entry.narration = f"Net Loss for FY {financial_year}-{str(financial_year+1)[-2:]} transferred from Retained Earnings"
        
        profit_transfer_entry.amount = abs(profit_loss.net_profit)
        profit_transfer_entry.reference_type = 'year_end_closing'
        profit_transfer_entry.reference_id = closing_voucher.voucher_id
        profit_transfer_entry.transaction_date = closing_date
        
        db.add(profit_transfer_entry)
        entries_created += 1
    
    return closing_voucher, entries_created

# API Endpoints
@router.get("/validate-closing/{financial_year}")
async def validate_year_closing(
    financial_year: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Validate if financial year can be closed"""
    validation_result = validate_year_closing_eligibility(db, current_user.company_id, financial_year)
    return validation_result

@router.get("/trial-balance")
async def get_trial_balance(
    as_of_date: date = Query(..., description="Date for trial balance"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Generate trial balance as of specific date"""
    trial_balance = calculate_trial_balance(db, current_user.company_id, as_of_date)
    return trial_balance

@router.get("/profit-loss/{financial_year}")
async def get_profit_loss_statement(
    financial_year: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Generate Profit & Loss statement for financial year"""
    profit_loss = calculate_profit_loss(db, current_user.company_id, financial_year)
    return profit_loss

@router.get("/balance-sheet")
async def get_balance_sheet(
    as_of_date: date = Query(..., description="Date for balance sheet"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Generate Balance Sheet as of specific date"""
    
    company = get_company_info(db, current_user.company_id)
    
    # Get asset accounts
    assets_query = db.query(
        MasterAccountModel.account_id,
        MasterAccountModel.account_code,
        MasterAccountModel.account_name,
        MasterAccountModel.account_type,
        func.coalesce(func.sum(LedgerEntryModel.debit - LedgerEntryModel.credit), 0).label('net_balance')
    ).outerjoin(
        LedgerEntryModel, MasterAccountModel.account_id == LedgerEntryModel.account_id
    ).outerjoin(
        VoucherMasterModel, LedgerEntryModel.voucher_id == VoucherMasterModel.voucher_id
    ).filter(
        MasterAccountModel.company_id == current_user.company_id,
        MasterAccountModel.account_type == 'Asset'
    ).filter(
        or_(
            LedgerEntryModel.voucher_id.is_(None),
            VoucherMasterModel.voucher_date <= as_of_date
        )
    ).group_by(
        MasterAccountModel.account_id,
        MasterAccountModel.account_code,
        MasterAccountModel.account_name,
        MasterAccountModel.account_type
    ).all()
    
    # Get liability accounts
    liabilities_query = db.query(
        MasterAccountModel.account_id,
        MasterAccountModel.account_code,
        MasterAccountModel.account_name,
        MasterAccountModel.account_type,
        func.coalesce(func.sum(LedgerEntryModel.credit - LedgerEntryModel.debit), 0).label('net_balance')
    ).outerjoin(
        LedgerEntryModel, MasterAccountModel.account_id == LedgerEntryModel.account_id
    ).outerjoin(
        VoucherMasterModel, LedgerEntryModel.voucher_id == VoucherMasterModel.voucher_id
    ).filter(
        MasterAccountModel.company_id == current_user.company_id,
        MasterAccountModel.account_type == 'Liability'
    ).filter(
        or_(
            LedgerEntryModel.voucher_id.is_(None),
            VoucherMasterModel.voucher_date <= as_of_date
        )
    ).group_by(
        MasterAccountModel.account_id,
        MasterAccountModel.account_code,
        MasterAccountModel.account_name,
        MasterAccountModel.account_type
    ).all()
    
    # Get equity accounts
    equity_query = db.query(
        MasterAccountModel.account_id,
        MasterAccountModel.account_code,
        MasterAccountModel.account_name,
        MasterAccountModel.account_type,
        func.coalesce(func.sum(LedgerEntryModel.credit - LedgerEntryModel.debit), 0).label('net_balance')
    ).outerjoin(
        LedgerEntryModel, MasterAccountModel.account_id == LedgerEntryModel.account_id
    ).outerjoin(
        VoucherMasterModel, LedgerEntryModel.voucher_id == VoucherMasterModel.voucher_id
    ).filter(
        MasterAccountModel.company_id == current_user.company_id,
        MasterAccountModel.account_type == 'Equity'
    ).filter(
        or_(
            LedgerEntryModel.voucher_id.is_(None),
            VoucherMasterModel.voucher_date <= as_of_date
        )
    ).group_by(
        MasterAccountModel.account_id,
        MasterAccountModel.account_code,
        MasterAccountModel.account_name,
        MasterAccountModel.account_type
    ).all()
    
    # Process results
    assets = []
    total_assets = 0.0
    
    for asset in assets_query:
        balance = float(asset.net_balance) if asset.net_balance else 0.0
        if balance != 0:  # Only include accounts with balances
            total_assets += balance
            assets.append(AccountBalance(
                account_id=asset.account_id,
                account_code=asset.account_code,
                account_name=asset.account_name,
                account_type=asset.account_type,
                debit_balance=balance if balance > 0 else 0.0,
                credit_balance=abs(balance) if balance < 0 else 0.0,
                net_balance=balance
            ))
    
    liabilities = []
    total_liabilities = 0.0
    
    for liability in liabilities_query:
        balance = float(liability.net_balance) if liability.net_balance else 0.0
        if balance != 0:
            total_liabilities += balance
            liabilities.append(AccountBalance(
                account_id=liability.account_id,
                account_code=liability.account_code,
                account_name=liability.account_name,
                account_type=liability.account_type,
                debit_balance=abs(balance) if balance < 0 else 0.0,
                credit_balance=balance if balance > 0 else 0.0,
                net_balance=balance
            ))
    
    equity = []
    total_equity = 0.0
    
    for eq in equity_query:
        balance = float(eq.net_balance) if eq.net_balance else 0.0
        if balance != 0:
            total_equity += balance
            equity.append(AccountBalance(
                account_id=eq.account_id,
                account_code=eq.account_code,
                account_name=eq.account_name,
                account_type=eq.account_type,
                debit_balance=abs(balance) if balance < 0 else 0.0,
                credit_balance=balance if balance > 0 else 0.0,
                net_balance=balance
            ))
    
    is_balanced = abs(total_assets - (total_liabilities + total_equity)) < 0.01
    
    # Determine financial year
    if as_of_date.month >= 4:  # April onwards
        fy_year = as_of_date.year
    else:  # Jan-Mar
        fy_year = as_of_date.year - 1
    
    return BalanceSheetResponse(
        as_of_date=as_of_date,
        financial_year=f"{fy_year}-{str(fy_year+1)[-2:]}",
        assets=assets,
        liabilities=liabilities,
        equity=equity,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        total_equity=total_equity,
        is_balanced=is_balanced
    )

@router.post("/close-year", response_model=FinancialYearClosingResponse)
async def close_financial_year(
    request: FinancialYearClosingRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Close financial year and create closing entries"""
    
    if request.admin_confirmation != "CONFIRM":
        raise HTTPException(
            status_code=400, 
            detail="Admin confirmation required. Please type 'CONFIRM' to proceed."
        )
    
    process_steps = []
    
    # Step 1: Validate eligibility
    process_steps.append(ClosingProcessStatus(
        step="validation",
        status="in-progress",
        message="Validating year closing eligibility",
        timestamp=datetime.now()
    ))
    
    validation = validate_year_closing_eligibility(db, current_user.company_id, request.financial_year)
    if not validation["eligible"]:
        process_steps[-1].status = "failed"
        process_steps[-1].message = validation["reason"]
        
        raise HTTPException(status_code=400, detail=validation["reason"])
    
    process_steps[-1].status = "completed"
    process_steps[-1].message = "Validation successful"
    
    try:
        # Step 2: Calculate P&L
        process_steps.append(ClosingProcessStatus(
            step="profit_loss_calculation",
            status="in-progress",
            message="Calculating Profit & Loss",
            timestamp=datetime.now()
        ))
        
        profit_loss = calculate_profit_loss(db, current_user.company_id, request.financial_year)
        
        process_steps[-1].status = "completed"
        process_steps[-1].message = f"P&L calculated: Net Profit ₹{profit_loss.net_profit:,.2f}"
        
        # Step 3: Create closing entries
        process_steps.append(ClosingProcessStatus(
            step="closing_entries",
            status="in-progress",
            message="Creating year-end closing entries",
            timestamp=datetime.now()
        ))
        
        closing_voucher, entries_count = create_year_end_closing_entries(
            db, current_user.company_id, current_user.id, request.financial_year, profit_loss
        )
        
        # Commit the transaction
        db.commit()
        
        process_steps[-1].status = "completed"
        process_steps[-1].message = f"Created {entries_count} closing entries"
        
        return FinancialYearClosingResponse(
            financial_year=f"{request.financial_year}-{str(request.financial_year+1)[-2:]}",
            closing_date=request.closing_date,
            status="success",
            profit_loss=profit_loss,
            closing_entries_count=entries_count,
            backup_location=None,  # TODO: Implement backup
            process_steps=process_steps,
            rollback_available=True
        )
        
    except Exception as e:
        db.rollback()
        
        # Update last step as failed
        if process_steps:
            process_steps[-1].status = "failed"
            process_steps[-1].message = f"Error: {str(e)}"
        
        raise HTTPException(
            status_code=500, 
            detail=f"Year closing failed: {str(e)}"
        )

@router.post("/open-year", response_model=FinancialYearOpeningResponse)
async def open_financial_year(
    request: FinancialYearOpeningRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Open new financial year and carry forward balances"""
    
    if request.admin_confirmation != "CONFIRM":
        raise HTTPException(
            status_code=400, 
            detail="Admin confirmation required. Please type 'CONFIRM' to proceed."
        )
    
    process_steps = []
    
    try:
        # Step 1: Validate previous year closing
        process_steps.append(ClosingProcessStatus(
            step="validation",
            status="in-progress",
            message="Validating previous year closing",
            timestamp=datetime.now()
        ))
        
        previous_year = request.financial_year - 1
        prev_validation = validate_year_closing_eligibility(db, current_user.company_id, previous_year)
        
        # Check if previous year is closed
        existing_closing = db.query(VoucherMasterModel).filter(
            VoucherMasterModel.company_id == current_user.company_id,
            VoucherMasterModel.voucher_type == "Year-End-Closing",
            VoucherMasterModel.narration.like(f"%FY {previous_year}-{str(previous_year+1)[-2:]}%")
        ).first()
        
        if not existing_closing:
            process_steps[-1].status = "failed"
            process_steps[-1].message = f"Previous year {previous_year}-{str(previous_year+1)[-2:]} must be closed first"
            
            raise HTTPException(
                status_code=400, 
                detail=f"Previous financial year {previous_year}-{str(previous_year+1)[-2:]} must be closed before opening new year"
            )
        
        process_steps[-1].status = "completed"
        process_steps[-1].message = "Previous year validation successful"
        
        # Step 2: Create opening entries
        process_steps.append(ClosingProcessStatus(
            step="opening_entries",
            status="in-progress",
            message="Creating opening balance entries",
            timestamp=datetime.now()
        ))
        
        fy_start, fy_end = get_financial_year_dates(request.financial_year)
        
        # Create opening voucher
        opening_voucher = VoucherMasterModel()
        opening_voucher.voucher_type = "Year-Opening"
        opening_voucher.voucher_date = request.opening_date
        opening_voucher.narration = f"Opening balances for FY {request.financial_year}-{str(request.financial_year+1)[-2:]}"
        opening_voucher.company_id = current_user.company_id
        opening_voucher.created_by = current_user.id
        
        db.add(opening_voucher)
        db.flush()
        
        # Get previous year-end date for balance calculation
        prev_fy_start, prev_fy_end = get_financial_year_dates(previous_year)
        
        # Calculate balances to carry forward (Assets, Liabilities, Equity only)
        balance_accounts = db.query(
            MasterAccountModel.account_id,
            MasterAccountModel.account_code,
            MasterAccountModel.account_name,
            MasterAccountModel.account_type,
            func.coalesce(
                case(
                    (MasterAccountModel.account_type == 'Asset', 
                     func.sum(LedgerEntryModel.debit - LedgerEntryModel.credit)),
                    else_=func.sum(LedgerEntryModel.credit - LedgerEntryModel.debit)
                ), 0
            ).label('balance')
        ).outerjoin(
            LedgerEntryModel, MasterAccountModel.account_id == LedgerEntryModel.account_id
        ).outerjoin(
            VoucherMasterModel, LedgerEntryModel.voucher_id == VoucherMasterModel.voucher_id
        ).filter(
            MasterAccountModel.company_id == current_user.company_id,
            MasterAccountModel.account_type.in_(['Asset', 'Liability', 'Equity']),
            or_(
                VoucherMasterModel.voucher_date.is_(None),
                VoucherMasterModel.voucher_date <= prev_fy_end
            )
        ).group_by(
            MasterAccountModel.account_id,
            MasterAccountModel.account_code,
            MasterAccountModel.account_name,
            MasterAccountModel.account_type
        ).having(
            func.abs(
                case(
                    (MasterAccountModel.account_type == 'Asset', 
                     func.sum(LedgerEntryModel.debit - LedgerEntryModel.credit)),
                    else_=func.sum(LedgerEntryModel.credit - LedgerEntryModel.debit)
                )
            ) > 0.01
        ).all()
        
        entries_created = 0
        balances_carried = 0
        
        for account in balance_accounts:
            balance = float(account.balance) if account.balance else 0.0
            
            if abs(balance) > 0.01:  # Only carry forward non-zero balances
                opening_entry = LedgerEntryModel()
                opening_entry.voucher_id = opening_voucher.voucher_id
                opening_entry.account_id = account.account_id
                
                if account.account_type == 'Asset':
                    if balance > 0:
                        opening_entry.dr_cr = 'D'
                        opening_entry.debit = balance
                        opening_entry.credit = 0.0
                    else:
                        opening_entry.dr_cr = 'C'
                        opening_entry.debit = 0.0
                        opening_entry.credit = abs(balance)
                else:  # Liability or Equity
                    if balance > 0:
                        opening_entry.dr_cr = 'C'
                        opening_entry.debit = 0.0
                        opening_entry.credit = balance
                    else:
                        opening_entry.dr_cr = 'D'
                        opening_entry.debit = abs(balance)
                        opening_entry.credit = 0.0
                
                opening_entry.amount = abs(balance)
                opening_entry.narration = f"Opening balance for {account.account_name}"
                opening_entry.reference_type = 'year_opening'
                opening_entry.reference_id = opening_voucher.voucher_id
                opening_entry.transaction_date = request.opening_date
                
                db.add(opening_entry)
                entries_created += 1
                balances_carried += 1
        
        db.commit()
        
        process_steps[-1].status = "completed"
        process_steps[-1].message = f"Created {entries_created} opening entries, carried forward {balances_carried} account balances"
        
        return FinancialYearOpeningResponse(
            financial_year=f"{request.financial_year}-{str(request.financial_year+1)[-2:]}",
            opening_date=request.opening_date,
            status="success",
            opening_entries_count=entries_created,
            carried_forward_balances=balances_carried,
            process_steps=process_steps
        )
        
    except Exception as e:
        db.rollback()
        
        if process_steps:
            process_steps[-1].status = "failed"
            process_steps[-1].message = f"Error: {str(e)}"
        
        raise HTTPException(
            status_code=500, 
            detail=f"Year opening failed: {str(e)}"
        )
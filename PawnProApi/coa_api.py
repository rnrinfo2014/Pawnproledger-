"""
Chart of Accounts (COA) API Endpoints
Handles account management for pawn shop business
"""

# type: ignore
# pylint: disable=all
# mypy: ignore-errors
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm.session import Session  # type: ignore
from typing import List, Optional
from database import get_db
from models import MasterAccount, Company
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/v1/coa", tags=["Chart of Accounts"])

# Pydantic Models
class AccountBase(BaseModel):
    account_name: str
    account_code: str
    account_type: str  # Asset, Liability, Income, Expense, Equity
    group_name: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True

class AccountCreate(AccountBase):
    company_id: int

class AccountUpdate(AccountBase):
    account_name: Optional[str] = None
    account_code: Optional[str] = None
    account_type: Optional[str] = None
    is_active: Optional[bool] = None

class AccountResponse(AccountBase):
    account_id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    children: List['AccountResponse'] = []
    
    class Config:
        from_attributes = True

# Update forward reference
AccountResponse.model_rebuild()

@router.get("/accounts", response_model=List[AccountResponse])
async def get_all_accounts(
    company_id: int,
    account_type: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """Get all accounts for a company with optional filters"""
    query = db.query(MasterAccount).filter(MasterAccount.company_id == company_id)  # type: ignore
    
    if account_type:
        query = query.filter(MasterAccount.account_type == account_type)  # type: ignore
    
    if is_active is not None:
        query = query.filter(MasterAccount.is_active == is_active)  # type: ignore
    
    accounts = query.order_by(MasterAccount.account_code).all()  # type: ignore
    return accounts

@router.get("/accounts/tree", response_model=List[AccountResponse])
async def get_accounts_tree(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Get hierarchical tree structure of accounts"""
    # Get parent accounts (no parent_id)
    parent_accounts = db.query(MasterAccount).filter(  # type: ignore
        MasterAccount.company_id == company_id,
        MasterAccount.parent_id.is_(None)
    ).order_by(MasterAccount.account_code).all()  # type: ignore
    
    return parent_accounts

@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """Get specific account by ID"""
    account = db.query(MasterAccount).filter(MasterAccount.account_id == account_id).first()  # type: ignore
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return account

@router.post("/accounts", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db)
):
    """Create new account"""
    
    # Validate company exists
    company = db.query(Company).filter(Company.id == account.company_id).first()  # type: ignore
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Check if account code already exists
    existing = db.query(MasterAccount).filter(  # type: ignore
        MasterAccount.account_code == account.account_code,
        MasterAccount.company_id == account.company_id
    ).first()  # type: ignore
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account code already exists for this company"
        )
    
    # Validate parent account if provided
    if account.parent_id:
        parent = db.query(MasterAccount).filter(  # type: ignore
            MasterAccount.account_id == account.parent_id,
            MasterAccount.company_id == account.company_id
        ).first()  # type: ignore
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent account not found"
            )
    
    # Create new account
    db_account = MasterAccount(**account.dict())  # type: ignore
    db.add(db_account)  # type: ignore
    db.commit()  # type: ignore
    db.refresh(db_account)  # type: ignore
    
    return db_account

@router.put("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_update: AccountUpdate,
    db: Session = Depends(get_db)
):
    """Update existing account"""
    
    # Get account
    db_account = db.query(MasterAccount).filter(MasterAccount.account_id == account_id).first()  # type: ignore
    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Update fields
    update_data = account_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_account, field, value)
    
    db.commit()  # type: ignore
    db.refresh(db_account)  # type: ignore
    
    return db_account

@router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """Delete account (soft delete by setting is_active = False)"""
    
    db_account = db.query(MasterAccount).filter(MasterAccount.account_id == account_id).first()  # type: ignore
    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Soft delete
    db_account.is_active = False  # type: ignore
    db.commit()  # type: ignore
    
    return {"message": "Account deactivated successfully"}

@router.get("/account-types")
async def get_account_types():
    """Get list of available account types"""
    return {
        "account_types": [
            {"code": "Asset", "name": "Assets"},
            {"code": "Liability", "name": "Liabilities"},
            {"code": "Income", "name": "Income"},
            {"code": "Expense", "name": "Expenses"},
            {"code": "Equity", "name": "Equity"}
        ]
    }

@router.post("/initialize-pawn-coa")
async def initialize_pawn_coa(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Initialize complete Chart of Accounts for Pawn Shop Business"""
    
    # Validate company
    company = db.query(Company).filter(Company.id == company_id).first()  # type: ignore
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Check if accounts already exist
    existing = db.query(MasterAccount).filter(MasterAccount.company_id == company_id).first()  # type: ignore
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chart of Accounts already exists for this company"
        )
    
    # Pawn Shop Chart of Accounts
    pawn_accounts = [
        # ASSETS (1000 series)
        {"account_name": "Current Assets", "account_code": "1000", "account_type": "Asset", "group_name": "Assets"},
        {"account_name": "Cash in Hand", "account_code": "1001", "account_type": "Asset", "group_name": "Current Assets", "parent_code": "1000"},
        {"account_name": "Cash at Bank", "account_code": "1002", "account_type": "Asset", "group_name": "Current Assets", "parent_code": "1000"},
        {"account_name": "Gold Inventory", "account_code": "1003", "account_type": "Asset", "group_name": "Current Assets", "parent_code": "1000"},
        {"account_name": "Silver Inventory", "account_code": "1004", "account_type": "Asset", "group_name": "Current Assets", "parent_code": "1000"},
        {"account_name": "Pledged Ornaments", "account_code": "1005", "account_type": "Asset", "group_name": "Current Assets", "parent_code": "1000"},
        {"account_name": "Auction Inventory", "account_code": "1006", "account_type": "Asset", "group_name": "Current Assets", "parent_code": "1000"},
        
        {"account_name": "Fixed Assets", "account_code": "1100", "account_type": "Asset", "group_name": "Assets"},
        {"account_name": "Shop & Building", "account_code": "1101", "account_type": "Asset", "group_name": "Fixed Assets", "parent_code": "1100"},
        {"account_name": "Furniture & Fixtures", "account_code": "1102", "account_type": "Asset", "group_name": "Fixed Assets", "parent_code": "1100"},
        {"account_name": "Equipment", "account_code": "1103", "account_type": "Asset", "group_name": "Fixed Assets", "parent_code": "1100"},
        
        # LIABILITIES (2000 series)
        {"account_name": "Current Liabilities", "account_code": "2000", "account_type": "Liability", "group_name": "Liabilities"},
        {"account_name": "Customer Pledge Accounts", "account_code": "2001", "account_type": "Liability", "group_name": "Current Liabilities", "parent_code": "2000"},
        {"account_name": "Interest Payable", "account_code": "2002", "account_type": "Liability", "group_name": "Current Liabilities", "parent_code": "2000"},
        {"account_name": "Auction Proceeds Payable", "account_code": "2003", "account_type": "Liability", "group_name": "Current Liabilities", "parent_code": "2000"},
        
        {"account_name": "Long Term Liabilities", "account_code": "2100", "account_type": "Liability", "group_name": "Liabilities"},
        {"account_name": "Bank Loans", "account_code": "2101", "account_type": "Liability", "group_name": "Long Term Liabilities", "parent_code": "2100"},
        
        # EQUITY (3000 series)
        {"account_name": "Capital", "account_code": "3000", "account_type": "Equity", "group_name": "Equity"},
        {"account_name": "Owner's Capital", "account_code": "3001", "account_type": "Equity", "group_name": "Capital", "parent_code": "3000"},
        {"account_name": "Retained Earnings", "account_code": "3002", "account_type": "Equity", "group_name": "Capital", "parent_code": "3000"},
        
        # INCOME (4000 series)
        {"account_name": "Revenue", "account_code": "4000", "account_type": "Income", "group_name": "Income"},
        {"account_name": "Pledge Interest Income", "account_code": "4001", "account_type": "Income", "group_name": "Revenue", "parent_code": "4000"},
        {"account_name": "Auction Income", "account_code": "4002", "account_type": "Income", "group_name": "Revenue", "parent_code": "4000"},
        {"account_name": "Service Charges", "account_code": "4003", "account_type": "Income", "group_name": "Revenue", "parent_code": "4000"},
        {"account_name": "Late Payment Charges", "account_code": "4004", "account_type": "Income", "group_name": "Revenue", "parent_code": "4000"},
        
        # EXPENSES (5000 series)
        {"account_name": "Operating Expenses", "account_code": "5000", "account_type": "Expense", "group_name": "Expenses"},
        {"account_name": "Staff Salaries", "account_code": "5001", "account_type": "Expense", "group_name": "Operating Expenses", "parent_code": "5000"},
        {"account_name": "Rent Expense", "account_code": "5002", "account_type": "Expense", "group_name": "Operating Expenses", "parent_code": "5000"},
        {"account_name": "Electricity Expense", "account_code": "5003", "account_type": "Expense", "group_name": "Operating Expenses", "parent_code": "5000"},
        {"account_name": "Security Expense", "account_code": "5004", "account_type": "Expense", "group_name": "Operating Expenses", "parent_code": "5000"},
        {"account_name": "License & Registration", "account_code": "5005", "account_type": "Expense", "group_name": "Operating Expenses", "parent_code": "5000"},
        {"account_name": "Insurance Expense", "account_code": "5006", "account_type": "Expense", "group_name": "Operating Expenses", "parent_code": "5000"},
        {"account_name": "Administrative Expense", "account_code": "5007", "account_type": "Expense", "group_name": "Operating Expenses", "parent_code": "5000"}
    ]
    
    # Create accounts
    account_map = {}  # To track parent-child relationships
    
    for account_data in pawn_accounts:
        parent_id = None
        if "parent_code" in account_data:
            parent_id = account_map.get(account_data["parent_code"])
        
        account = MasterAccount(  # type: ignore
            account_name=account_data["account_name"],  # type: ignore
            account_code=account_data["account_code"],  # type: ignore
            account_type=account_data["account_type"],  # type: ignore
            group_name=account_data["group_name"],  # type: ignore
            parent_id=parent_id,  # type: ignore
            company_id=company_id,  # type: ignore
            is_active=True  # type: ignore
        )
        
        db.add(account)  # type: ignore
        db.flush()  # Get the ID  # type: ignore
        account_map[account_data["account_code"]] = account.account_id  # type: ignore
    
    db.commit()  # type: ignore
    
    return {
        "message": "Pawn Shop Chart of Accounts initialized successfully",
        "accounts_created": len(pawn_accounts)
    }
"""
Customer COA Account Management Functions
Handles automatic creation, update, and deletion of COA accounts for customers
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.core.models import MasterAccount as MasterAccountModel, Customer as CustomerModel
from typing import Optional

def create_customer_coa_account(db: Session, customer: CustomerModel, company_id: int) -> MasterAccountModel:
    """
    Create individual COA account for customer under Customer Pledge Accounts (2001)
    
    Args:
        db: Database session
        customer: Customer model instance
        company_id: Company ID
        
    Returns:
        Created MasterAccount instance
    """
    
    # Find parent account "Customer Pledge Accounts" (2001)
    parent_account = db.query(MasterAccountModel).filter(
        MasterAccountModel.account_code == "2001",
        MasterAccountModel.company_id == company_id
    ).first()
    
    if not parent_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Customer Pledge Accounts parent account (2001) not found. Please initialize COA first."
        )
    
    # Generate unique sub-account code: 2001-001, 2001-002, etc.
    existing_sub_accounts = db.query(MasterAccountModel).filter(
        MasterAccountModel.parent_id == parent_account.account_id,
        MasterAccountModel.account_code.like("2001-%"),
        MasterAccountModel.company_id == company_id
    ).all()
    
    max_sub_num = 0
    for account in existing_sub_accounts:
        try:
            code_parts = account.account_code.split("-")
            if len(code_parts) >= 2:
                sub_num = int(code_parts[1])
                if sub_num > max_sub_num:
                    max_sub_num = sub_num
        except (ValueError, IndexError):
            continue
    
    sub_account_code = f"2001-{max_sub_num + 1:03d}"
    
    # Create individual customer COA account
    customer_account = MasterAccountModel(
        account_name=f"Customer - {customer.name}",
        account_code=sub_account_code,
        account_type="Liability",
        group_name="Customer Accounts",
        parent_id=parent_account.account_id,
        company_id=company_id,
        is_active=True
    )
    
    db.add(customer_account)
    db.flush()  # Get the ID without committing
    
    # Update customer with COA account reference
    customer.coa_account_id = customer_account.account_id
    
    return customer_account

def update_customer_coa_account(db: Session, customer: CustomerModel, old_name: str) -> Optional[MasterAccountModel]:
    """
    Update customer COA account name when customer name changes
    
    Args:
        db: Database session
        customer: Updated customer model instance
        old_name: Previous customer name
        
    Returns:
        Updated MasterAccount instance or None if no COA account exists
    """
    
    if not customer.coa_account_id:
        return None
    
    # Find and update the COA account
    coa_account = db.query(MasterAccountModel).filter(
        MasterAccountModel.account_id == customer.coa_account_id
    ).first()
    
    if coa_account and customer.name != old_name:
        coa_account.account_name = f"Customer - {customer.name}"
        db.flush()
        return coa_account
    
    return coa_account

def delete_customer_coa_account(db: Session, customer: CustomerModel) -> bool:
    """
    Delete or deactivate customer COA account when customer is deleted
    
    Args:
        db: Database session
        customer: Customer model instance to be deleted
        
    Returns:
        True if account was handled successfully
    """
    
    if not customer.coa_account_id:
        return True
    
    # Find the COA account
    coa_account = db.query(MasterAccountModel).filter(
        MasterAccountModel.account_id == customer.coa_account_id
    ).first()
    
    if not coa_account:
        return True
    
    # Check if account has any transactions (ledger entries)
    from src.core.models import LedgerEntry as LedgerEntryModel
    
    has_transactions = db.query(LedgerEntryModel).filter(
        LedgerEntryModel.account_id == customer.coa_account_id
    ).first()
    
    if has_transactions:
        # If account has transactions, deactivate instead of delete
        coa_account.is_active = False
        coa_account.account_name = f"[DELETED] {coa_account.account_name}"
        print(f"⚠️ Customer COA account {coa_account.account_code} deactivated (has transactions)")
    else:
        # If no transactions, safe to delete
        db.delete(coa_account)
        print(f"🗑️ Customer COA account {coa_account.account_code} deleted (no transactions)")
    
    return True

def get_customer_balance(db: Session, customer_id: int) -> dict:
    """
    Get customer's current balance from their COA account
    
    Args:
        db: Database session
        customer_id: Customer ID
        
    Returns:
        Dictionary with customer balance information
    """
    
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if not customer.coa_account_id:
        return {
            "customer_id": customer_id,
            "customer_name": customer.name,
            "balance": 0.0,
            "account_code": None,
            "has_coa_account": False
        }
    
    # Calculate balance from ledger entries
    from src.core.models import LedgerEntry as LedgerEntryModel
    from sqlalchemy import func
    
    balance_query = db.query(
        func.sum(LedgerEntryModel.credit - LedgerEntryModel.debit).label('balance')
    ).filter(
        LedgerEntryModel.account_id == customer.coa_account_id
    ).scalar()
    
    balance = float(balance_query) if balance_query else 0.0
    
    return {
        "customer_id": customer_id,
        "customer_name": customer.name,
        "balance": balance,
        "account_code": customer.coa_account.account_code if customer.coa_account else None,
        "has_coa_account": True
    }

def migrate_existing_customers_to_coa(db: Session, company_id: int) -> dict:
    """
    Create COA accounts for existing customers who don't have them
    
    Args:
        db: Database session
        company_id: Company ID
        
    Returns:
        Migration results dictionary
    """
    
    customers_without_coa = db.query(CustomerModel).filter(
        CustomerModel.coa_account_id.is_(None),
        CustomerModel.company_id == company_id,
        CustomerModel.status == 'active'
    ).all()
    
    results = {
        "total_customers": len(customers_without_coa),
        "migrated": 0,
        "errors": []
    }
    
    for customer in customers_without_coa:
        try:
            create_customer_coa_account(db, customer, company_id)
            results["migrated"] += 1
            print(f"✅ Migrated customer: {customer.name} ({customer.acc_code})")
        except Exception as e:
            error_msg = f"Failed to migrate customer {customer.name}: {str(e)}"
            results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    if results["migrated"] > 0:
        db.commit()
        print(f"🎉 Migration completed: {results['migrated']}/{results['total_customers']} customers migrated")
    
    return results
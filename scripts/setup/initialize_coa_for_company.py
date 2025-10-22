#!/usr/bin/env python3
"""
Initialize Chart of Accounts for Company 5
"""

from database import SessionLocal
from models import MasterAccount as MasterAccountModel

def initialize_coa():
    """Initialize the default Chart of Accounts"""
    db = SessionLocal()
    
    try:
        company_id = 5
        
        # Check if accounts already exist
        existing_count = db.query(MasterAccountModel).filter(
            MasterAccountModel.company_id == company_id
        ).count()
        
        if existing_count > 0:
            print(f"COA already initialized for company {company_id} with {existing_count} accounts")
            return True
        
        print(f"Initializing Chart of Accounts for company {company_id}...")
        
        # Default Chart of Accounts structure
        accounts = [
            # Assets (1000-1999)
            {"account_code": "1001", "account_name": "Cash in Hand", "account_type": "Asset", "parent_code": None},
            {"account_code": "1002", "account_name": "Cash at Bank", "account_type": "Asset", "parent_code": None},
            {"account_code": "1005", "account_name": "Pledged Ornaments", "account_type": "Asset", "parent_code": None},
            {"account_code": "1010", "account_name": "Gold Stock", "account_type": "Asset", "parent_code": None},
            {"account_code": "1011", "account_name": "Silver Stock", "account_type": "Asset", "parent_code": None},
            
            # Liabilities (2000-2999)
            {"account_code": "2001", "account_name": "Customer Liabilities", "account_type": "Liability", "parent_code": None},
            {"account_code": "2010", "account_name": "Bank Loans", "account_type": "Liability", "parent_code": None},
            {"account_code": "2020", "account_name": "Sundry Creditors", "account_type": "Liability", "parent_code": None},
            
            # Capital (3000-3999)
            {"account_code": "3001", "account_name": "Capital Account", "account_type": "Capital", "parent_code": None},
            {"account_code": "3002", "account_name": "Reserves", "account_type": "Capital", "parent_code": None},
            {"account_code": "3003", "account_name": "Retained Earnings", "account_type": "Capital", "parent_code": None},
            
            # Income (4000-4999)
            {"account_code": "4001", "account_name": "Interest Income", "account_type": "Income", "parent_code": None},
            {"account_code": "4002", "account_name": "Document Charges Income", "account_type": "Income", "parent_code": None},
            {"account_code": "4003", "account_name": "Service Charges", "account_type": "Income", "parent_code": None},
            {"account_code": "4010", "account_name": "Auction Income", "account_type": "Income", "parent_code": None},
            {"account_code": "4020", "account_name": "Other Income", "account_type": "Income", "parent_code": None},
            
            # Expenses (5000-5999)
            {"account_code": "5001", "account_name": "Salaries and Wages", "account_type": "Expense", "parent_code": None},
            {"account_code": "5002", "account_name": "Rent Expense", "account_type": "Expense", "parent_code": None},
            {"account_code": "5003", "account_name": "Electricity Expense", "account_type": "Expense", "parent_code": None},
            {"account_code": "5004", "account_name": "Interest Expense", "account_type": "Expense", "parent_code": None},
            {"account_code": "5010", "account_name": "Office Expenses", "account_type": "Expense", "parent_code": None},
            {"account_code": "5020", "account_name": "Bank Charges", "account_type": "Expense", "parent_code": None},
            {"account_code": "5030", "account_name": "Depreciation", "account_type": "Expense", "parent_code": None},
        ]
        
        # Create accounts
        for acc in accounts:
            account = MasterAccountModel(
                account_code=acc["account_code"],
                account_name=acc["account_name"],
                account_type=acc["account_type"],
                parent_code=acc["parent_code"],
                company_id=company_id,
                status="active"
            )
            db.add(account)
        
        db.commit()
        
        final_count = db.query(MasterAccountModel).filter(
            MasterAccountModel.company_id == company_id
        ).count()
        
        print(f"Successfully created {final_count} COA accounts for company {company_id}")
        print("\nKey accounts created:")
        print("  1001 - Cash in Hand")
        print("  1005 - Pledged Ornaments")
        print("  2001 - Customer Liabilities")
        print("  4001 - Interest Income")
        print("  4002 - Document Charges Income")
        print("  4003 - Service Charges")
        
        return True
        
    except Exception as e:
        print(f"Error initializing COA: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Chart of Accounts Initialization")
    print("=" * 60)
    
    if initialize_coa():
        print("\nCOA initialization complete!")
        print("You can now create pledges with full accounting.")
    else:
        print("\nCOA initialization failed!")

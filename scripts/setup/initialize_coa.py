#!/usr/bin/env python3
"""
Initialize Chart of Accounts and test pledge creation
"""

from database import SessionLocal
from models import MasterAccount as MasterAccountModel
from auth import get_password_hash

def initialize_coa_accounts():
    """Initialize basic Chart of Accounts"""
    db = SessionLocal()
    
    try:
        print("Initializing Chart of Accounts...")
        
        # Check if accounts already exist
        existing_accounts = db.query(MasterAccountModel).count()
        if existing_accounts > 0:
            print(f"COA already has {existing_accounts} accounts")
            return True
        
        # Create basic accounts needed for pledge accounting
        basic_accounts = [
            {"account_id": 1001, "account_name": "Cash in Hand", "account_type": "Asset", "company_id": 5},
            {"account_id": 1002, "account_name": "Pledged Ornaments", "account_type": "Asset", "company_id": 5},
            {"account_id": 2001, "account_name": "Customer Accounts", "account_type": "Liability", "company_id": 5},
            {"account_id": 4001, "account_name": "Document Charges Income", "account_type": "Income", "company_id": 5},
            {"account_id": 4002, "account_name": "Interest Income", "account_type": "Income", "company_id": 5},
        ]
        
        for account_data in basic_accounts:
            account = MasterAccountModel(**account_data)
            db.add(account)
        
        db.commit()
        print(f"Created {len(basic_accounts)} basic COA accounts")
        return True
        
    except Exception as e:
        print(f"Error initializing COA: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Setting up Chart of Accounts for Pledge Accounting...")
    print("=" * 55)
    
    if initialize_coa_accounts():
        print("SUCCESS: Chart of Accounts initialized")
        print("Now ready for pledge accounting test")
    else:
        print("FAILED: Could not initialize Chart of Accounts")
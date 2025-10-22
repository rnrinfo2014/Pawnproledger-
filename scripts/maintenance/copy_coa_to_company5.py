#!/usr/bin/env python3
"""
Copy COA accounts from Company 1 to Company 5
"""

from database import SessionLocal
from models import MasterAccount as MasterAccountModel

def copy_coa_accounts():
    """Copy COA accounts from company 1 to company 5"""
    db = SessionLocal()
    
    try:
        source_company = 1
        target_company = 5
        
        # Check if target company already has accounts
        existing_count = db.query(MasterAccountModel).filter(
            MasterAccountModel.company_id == target_company
        ).count()
        
        if existing_count > 0:
            print(f"Company {target_company} already has {existing_count} accounts")
            return True
        
        # Get all accounts from source company
        source_accounts = db.query(MasterAccountModel).filter(
            MasterAccountModel.company_id == source_company
        ).all()
        
        print(f"Copying {len(source_accounts)} accounts from Company {source_company} to Company {target_company}...")
        
        # Copy each account
        for source_acc in source_accounts:
            # Skip customer-specific accounts (they have individual numbers)
            if "-" in source_acc.account_code and source_acc.account_code.startswith("2001-"):
                continue  # Skip individual customer accounts
            
            new_account = MasterAccountModel(
                account_code=source_acc.account_code,
                account_name=source_acc.account_name,
                account_type=source_acc.account_type,
                parent_code=source_acc.parent_code,
                company_id=target_company,
                status=source_acc.status or "active"
            )
            db.add(new_account)
        
        db.commit()
        
        # Verify the copy
        copied_count = db.query(MasterAccountModel).filter(
            MasterAccountModel.company_id == target_company
        ).count()
        
        print(f"Successfully copied {copied_count} COA accounts to Company {target_company}")
        
        # Show key accounts
        key_accounts = db.query(MasterAccountModel).filter(
            MasterAccountModel.company_id == target_company,
            MasterAccountModel.account_code.in_(["1001", "1005", "2001", "4001", "4003"])
        ).all()
        
        print("Key accounts in Company 5:")
        for acc in key_accounts:
            print(f"  {acc.account_code} - {acc.account_name}")
        
        return True
        
    except Exception as e:
        print(f"Error copying COA: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("COA Copy from Company 1 to Company 5")
    print("=" * 50)
    
    if copy_coa_accounts():
        print("\nCOA copy complete! Company 5 now has the same chart of accounts.")
        print("You can now create pledges with full accounting.")
    else:
        print("\nCOA copy failed!")
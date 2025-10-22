#!/usr/bin/env python3
"""
Check COA accounts and customer assignments
"""

from database import SessionLocal
from models import MasterAccount as MasterAccountModel, Customer as CustomerModel

def check_coa_status():
    """Check the status of COA accounts"""
    db = SessionLocal()
    
    try:
        # Check COA accounts by company
        print("Chart of Accounts Status:")
        print("=" * 60)
        
        companies = db.query(MasterAccountModel.company_id).distinct().all()
        for (company_id,) in companies:
            count = db.query(MasterAccountModel).filter(
                MasterAccountModel.company_id == company_id
            ).count()
            print(f"Company {company_id}: {count} accounts")
            
            # Show some key accounts
            key_accounts = db.query(MasterAccountModel).filter(
                MasterAccountModel.company_id == company_id,
                MasterAccountModel.account_code.in_(["1001", "1005", "2001", "4001", "4003"])
            ).all()
            
            if key_accounts:
                print("  Key accounts found:")
                for acc in key_accounts:
                    print(f"    {acc.account_code} - {acc.account_name}")
            else:
                print("  WARNING: Missing key accounts (1001, 1005, 2001, 4001, 4003)")
        
        # Check customers
        print("\nCustomer Status:")
        print("=" * 60)
        
        total_customers = db.query(CustomerModel).count()
        customers_with_coa = db.query(CustomerModel).filter(
            CustomerModel.coa_account_id.isnot(None)
        ).count()
        customers_without_coa = total_customers - customers_with_coa
        
        print(f"Total customers: {total_customers}")
        print(f"Customers with COA account: {customers_with_coa}")
        print(f"Customers without COA account: {customers_without_coa}")
        
        if customers_without_coa > 0:
            print("\nCustomers without COA accounts:")
            customers = db.query(CustomerModel).filter(
                CustomerModel.coa_account_id.is_(None)
            ).limit(5).all()
            for customer in customers:
                print(f"  ID: {customer.id}, Name: {customer.name}, Company: {customer.company_id}")
        
        # Show some customers with COA
        if customers_with_coa > 0:
            print("\nCustomers with COA accounts (sample):")
            customers = db.query(CustomerModel).filter(
                CustomerModel.coa_account_id.isnot(None)
            ).limit(3).all()
            for customer in customers:
                coa_account = db.query(MasterAccountModel).filter(
                    MasterAccountModel.account_id == customer.coa_account_id
                ).first()
                if coa_account:
                    print(f"  ID: {customer.id}, Name: {customer.name}, COA: {coa_account.account_code} - {coa_account.account_name}")
        
        print("\nRecommendations:")
        print("=" * 60)
        if customers_without_coa > 0:
            print("Run customer COA migration to assign COA accounts to existing customers")
        
        # Check if company 5 has accounts
        company_5_count = db.query(MasterAccountModel).filter(
            MasterAccountModel.company_id == 5
        ).count()
        
        if company_5_count == 0:
            print("Company 5 (admin's company) has no COA accounts - need to initialize or copy")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_coa_status()

"""
Selective Data Clear Script
Clears only customer-related transactional data while preserving master data
"""

from database import SessionLocal
from sqlalchemy import text

def clear_customer_transactional_data():
    """Clear only customer, pledge, and payment related data"""
    db = SessionLocal()
    
    try:
        print("🗑️ Clearing customer transactional data...")
        
        # Disable foreign key checks temporarily (PostgreSQL)
        db.execute(text("SET session_replication_role = 'replica';"))
        
        # List of tables to clear (in order to avoid foreign key constraints)
        tables_to_clear = [
            'pledge_payments',    # Clear payments first
            'pledge_items',       # Clear pledge items
            'pledges',           # Clear pledges
            'items',             # Clear items
            'customers'          # Clear customers last
        ]
        
        # Clear each table
        for table in tables_to_clear:
            try:
                result = db.execute(text(f"DELETE FROM {table}"))
                print(f"✅ Cleared {table}: {result.rowcount} rows deleted")
            except Exception as e:
                print(f"⚠️ Error clearing {table}: {str(e)}")
        
        # Re-enable foreign key checks
        db.execute(text("SET session_replication_role = 'origin';"))
        
        # Reset sequences for auto-increment columns (only for cleared tables)
        sequences_to_reset = [
            'customers_id_seq',
            'pledges_id_seq',
            'pledge_payments_id_seq',
            'items_id_seq',
            'pledge_items_id_seq'
        ]
        
        for sequence in sequences_to_reset:
            try:
                db.execute(text(f"ALTER SEQUENCE {sequence} RESTART WITH 1"))
                print(f"🔄 Reset sequence: {sequence}")
            except Exception as e:
                print(f"⚠️ Error resetting sequence {sequence}: {str(e)}")
        
        db.commit()
        print("✅ Customer transactional data cleared successfully!")
        
        # Show what's preserved
        print("\n📊 Preserved master data:")
        preserved_tables = [
            'companies',
            'users', 
            'accounts_master',
            'voucher_master',
            'areas',
            'jewell_types',
            'jewell_rates',
            'schemes',
            'jewell_designs',
            'jewell_conditions',
            'banks',
            'gold_silver_rates'
        ]
        
        for table in preserved_tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"   ✅ {table}: {count} records preserved")
            except Exception as e:
                print(f"   ⚠️ Error checking {table}: {str(e)}")
        
    except Exception as e:
        print(f"❌ Error clearing data: {str(e)}")
        db.rollback()
    finally:
        db.close()

def clear_customer_coa_accounts():
    """Clear only customer-specific COA accounts (2001-xxx)"""
    db = SessionLocal()
    
    try:
        print("\n🗑️ Clearing customer COA accounts...")
        
        # Delete customer COA sub-accounts (2001-xxx pattern)
        delete_customer_accounts = """
        DELETE FROM accounts_master 
        WHERE account_code LIKE '2001-%'
        AND parent_id IS NOT NULL
        """
        
        result = db.execute(text(delete_customer_accounts))
        print(f"✅ Cleared customer COA accounts: {result.rowcount} accounts deleted")
        
        # Check and show remaining COA structure
        remaining_accounts = """
        SELECT account_code, account_name, account_type 
        FROM accounts_master 
        WHERE account_code LIKE '2001%'
        ORDER BY account_code
        """
        
        result = db.execute(text(remaining_accounts))
        accounts = result.fetchall()
        
        print("\n📊 Remaining Customer Pledge Accounts structure:")
        for account in accounts:
            print(f"   ✅ {account[0]} - {account[1]} ({account[2]})")
        
        db.commit()
        
    except Exception as e:
        print(f"❌ Error clearing customer COA accounts: {str(e)}")
        db.rollback()
    finally:
        db.close()

def show_data_summary():
    """Show summary of remaining data"""
    db = SessionLocal()
    
    try:
        print("\n📊 Data Summary After Cleanup:")
        print("-" * 40)
        
        # Check key tables
        summary_tables = {
            'companies': 'Companies',
            'users': 'Users',
            'accounts_master': 'COA Accounts',
            'areas': 'Areas',
            'jewell_types': 'Jewellery Types',
            'schemes': 'Schemes',
            'customers': 'Customers',
            'pledges': 'Pledges',
            'pledge_payments': 'Payments'
        }
        
        for table, description in summary_tables.items():
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                status = "✅" if count > 0 else "🗑️"
                print(f"{status} {description}: {count} records")
            except Exception as e:
                print(f"❌ {description}: Error - {str(e)}")
        
    except Exception as e:
        print(f"❌ Error generating summary: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("⚠️ WARNING: This will delete customer transactional data only!")
    print("📊 Will preserve: companies, users, COA accounts, areas, schemes, etc.")
    print("🗑️ Will delete: customers, pledges, pledge_items, pledge_payments, items")
    
    confirm = input("\nType 'CLEAR CUSTOMER DATA' to confirm: ")
    
    if confirm == "CLEAR CUSTOMER DATA":
        clear_customer_transactional_data()
        clear_customer_coa_accounts()
        show_data_summary()
        print("\n🎉 Selective data cleanup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Start server: python -m uvicorn main:app --reload")
        print("2. Create customers with auto COA account creation")
        print("3. Test customer balance endpoints")
    else:
        print("❌ Operation cancelled.")
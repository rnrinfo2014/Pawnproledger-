"""
Clear All Data Script
This script will empty all tables in the database
"""

from database import SessionLocal, engine
from models import *
from sqlalchemy import text

def clear_all_data():
    """Clear all data from database tables"""
    db = SessionLocal()
    
    try:
        print("🗑️ Clearing all data from database...")
        
        # Disable foreign key checks temporarily
        db.execute(text("SET session_replication_role = 'replica';"))
        
        # List of tables to clear (in order to avoid foreign key constraints)
        tables_to_clear = [
            'ledger_entries',
            'pledge_payments',
            'pledge_items', 
            'pledges',
            'items',
            'customers',
            'accounts_master',
            'voucher_master',
            'gold_silver_rates',
            'jewell_rates',
            'schemes',
            'areas',
            'jewell_designs',
            'jewell_conditions',
            'jewell_types',
            'banks',
            'users',
            'companies'
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
        
        # Reset sequences for auto-increment columns
        sequences_to_reset = [
            'companies_id_seq',
            'users_id_seq', 
            'accounts_master_account_id_seq',
            'voucher_master_voucher_id_seq',
            'customers_id_seq',
            'pledges_id_seq',
            'pledge_payments_id_seq',
            'areas_id_seq',
            'jewell_types_id_seq',
            'jewell_rates_id_seq',
            'schemes_id_seq',
            'items_id_seq',
            'pledge_items_id_seq',
            'banks_id_seq'
        ]
        
        for sequence in sequences_to_reset:
            try:
                db.execute(text(f"ALTER SEQUENCE {sequence} RESTART WITH 1"))
                print(f"🔄 Reset sequence: {sequence}")
            except Exception as e:
                print(f"⚠️ Error resetting sequence {sequence}: {str(e)}")
        
        db.commit()
        print("✅ All data cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("⚠️ WARNING: This will delete ALL data from the database!")
    confirm = input("Type 'DELETE ALL DATA' to confirm: ")
    
    if confirm == "DELETE ALL DATA":
        clear_all_data()
        print("🎉 Database cleared successfully!")
    else:
        print("❌ Operation cancelled.")
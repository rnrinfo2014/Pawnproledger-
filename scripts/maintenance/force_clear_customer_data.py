"""
Force Clear Customer Data Script
More forceful clearing with proper constraint handling
"""

from database import SessionLocal
from sqlalchemy import text

def force_clear_customer_data():
    """Force clear all customer-related data"""
    db = SessionLocal()
    
    try:
        print("🗑️ Force clearing customer data...")
        
        # Clear each table in separate transactions
        tables = [
            'pledge_payments',
            'pledge_items', 
            'pledges',
            'items',
            'customers'
        ]
        
        for table in tables:
            try:
                # Start fresh transaction for each table
                result = db.execute(text(f"DELETE FROM {table}"))
                db.commit()
                print(f"✅ Cleared {table}: {result.rowcount} rows")
                
            except Exception as e:
                print(f"❌ Error with {table}: {str(e)}")
                db.rollback()
        
        # Clear customer COA accounts (2001-xxx pattern)
        try:
            result = db.execute(text("DELETE FROM accounts_master WHERE account_code LIKE '2001-%' AND parent_id IS NOT NULL"))
            db.commit()
            print(f"✅ Cleared customer COA accounts: {result.rowcount} accounts")
        except Exception as e:
            print(f"❌ Error clearing COA accounts: {str(e)}")
            db.rollback()
        
        # Reset sequences
        sequences = ['customers_id_seq', 'pledges_id_seq', 'pledge_payments_id_seq']
        for seq in sequences:
            try:
                db.execute(text(f"ALTER SEQUENCE {seq} RESTART WITH 1"))
                db.commit()
                print(f"🔄 Reset {seq}")
            except Exception as e:
                # Sequence might not exist, that's okay
                db.rollback()
        
        print("✅ Force clear completed!")
        
        # Verify clearing
        print("\n📊 Verification:")
        for table in tables:
            try:
                count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                status = "✅" if count == 0 else "⚠️"
                print(f"{status} {table}: {count} rows")
            except Exception as e:
                print(f"❌ {table}: {str(e)}")
        
    except Exception as e:
        print(f"❌ Force clear failed: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    force_clear_customer_data()
"""
Migration script to add pledge_payments table to existing database
Run this script to add the new payment functionality to your PawnPro database
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings
from database import Base
from models import PledgePayment

def run_migration():
    """Add pledge_payments table to the database"""
    
    # Create engine
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        # Create the new table
        print("Creating pledge_payments table...")
        PledgePayment.__table__.create(engine, checkfirst=True)
        print("✅ pledge_payments table created successfully!")
        
        # Add indexes for better performance
        print("Adding database indexes...")
        with engine.connect() as conn:
            # Index on pledge_id for faster queries
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_pledge_payments_pledge_id 
                ON pledge_payments (pledge_id);
            """))
            
            # Index on payment_date for date range queries
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_pledge_payments_date 
                ON pledge_payments (payment_date);
            """))
            
            # Index on company_id for multi-tenant filtering
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_pledge_payments_company_id 
                ON pledge_payments (company_id);
            """))
            
            # Index on payment_type for filtering
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_pledge_payments_type 
                ON pledge_payments (payment_type);
            """))
            
            # Composite index for pledge + company filtering
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_pledge_payments_pledge_company 
                ON pledge_payments (pledge_id, company_id);
            """))
            
            conn.commit()
            
        print("✅ Database indexes created successfully!")
        
        # Verify table creation
        print("Verifying table structure...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'pledge_payments' 
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            if columns:
                print("✅ Table structure verified:")
                for column in columns:
                    print(f"  - {column[0]}: {column[1]} ({'NULL' if column[2] == 'YES' else 'NOT NULL'})")
            else:
                print("❌ Could not verify table structure")
        
        print("\n🎉 Migration completed successfully!")
        print("\nNew Payment API endpoints available:")
        print("  POST   /pledge-payments/              - Create payment")
        print("  GET    /pledge-payments/              - List payments (with filters)")
        print("  GET    /pledge-payments/{payment_id}  - Get payment details")
        print("  PUT    /pledge-payments/{payment_id}  - Update payment")
        print("  DELETE /pledge-payments/{payment_id}  - Delete payment")
        print("  GET    /pledges/{pledge_id}/payments  - Get payments for pledge")
        print("  GET    /pledges/{pledge_id}/payment-summary - Get payment summary")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    print("🚀 Starting pledge payments migration...")
    print("=" * 50)
    run_migration()
    print("=" * 50)
    print("✅ Migration completed!")
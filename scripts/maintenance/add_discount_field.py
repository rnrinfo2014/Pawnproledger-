"""
Migration script to add discount_amount column to pledge_payments table
Run this script to add the discount field to your existing PawnPro database
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

def run_migration():
    """Add discount_amount column to pledge_payments table"""
    
    # Create engine
    engine = create_engine(settings.database_url)
    
    try:
        print("Adding discount_amount column to pledge_payments table...")
        
        with engine.connect() as conn:
            # Check if the column already exists
            check_column = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'pledge_payments' 
                AND column_name = 'discount_amount';
            """)
            
            result = conn.execute(check_column)
            column_exists = result.fetchone()
            
            if column_exists:
                print("⚠️  discount_amount column already exists in pledge_payments table")
                return
            
            # Add the discount_amount column
            add_column = text("""
                ALTER TABLE pledge_payments 
                ADD COLUMN discount_amount FLOAT DEFAULT 0.0;
            """)
            
            conn.execute(add_column)
            conn.commit()
            
        print("✅ discount_amount column added successfully!")
        
        # Verify column addition
        print("Verifying column addition...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, column_default, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'pledge_payments' 
                AND column_name = 'discount_amount';
            """))
            
            column_info = result.fetchone()
            if column_info:
                print("✅ Column structure verified:")
                print(f"  - Name: {column_info[0]}")
                print(f"  - Type: {column_info[1]}")
                print(f"  - Default: {column_info[2]}")
                print(f"  - Nullable: {column_info[3]}")
            else:
                print("❌ Could not verify column addition")
        
        print("\n🎉 Migration completed successfully!")
        print("\nDiscounted payments can now be created with:")
        print("  - discount_amount field in payment requests")
        print("  - Automatic discount tracking in payment records")
        print("  - Updated payment history with discount details")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("\nPossible causes:")
        print("1. Database connection issues")
        print("2. Insufficient database permissions")
        print("3. Table 'pledge_payments' does not exist")
        print("\nPlease check your database configuration and try again.")

if __name__ == "__main__":
    print("🚀 Starting discount field migration...")
    print("=" * 50)
    run_migration()
    print("=" * 50)
    print("✅ Migration script completed!")
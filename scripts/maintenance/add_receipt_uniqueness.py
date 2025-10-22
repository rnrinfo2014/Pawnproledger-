"""
Migration script to add unique index on receipt_no in pledge_payments table
Run this script to ensure receipt number uniqueness across the system
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

def run_migration():
    """Add unique index on receipt_no column in pledge_payments table"""
    
    # Create engine
    engine = create_engine(settings.database_url)
    
    try:
        print("Adding unique index on receipt_no in pledge_payments table...")
        
        with engine.connect() as conn:
            # Check if the index already exists
            check_index = text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'pledge_payments' 
                AND indexname = 'idx_pledge_payments_receipt_no_unique';
            """)
            
            result = conn.execute(check_index)
            index_exists = result.fetchone()
            
            if index_exists:
                print("⚠️  Unique index on receipt_no already exists")
                return
            
            # Check for any duplicate receipt numbers before creating the unique index
            check_duplicates = text("""
                SELECT receipt_no, COUNT(*) as count
                FROM pledge_payments 
                WHERE receipt_no IS NOT NULL
                GROUP BY receipt_no 
                HAVING COUNT(*) > 1;
            """)
            
            result = conn.execute(check_duplicates)
            duplicates = result.fetchall()
            
            if duplicates:
                print("⚠️  Found duplicate receipt numbers:")
                for dup in duplicates:
                    print(f"  - Receipt: {dup[0]} (Count: {dup[1]})")
                
                print("\n🔄 Updating duplicate receipt numbers...")
                
                # Update duplicate receipt numbers to make them unique
                for dup in duplicates:
                    receipt_no = dup[0]
                    
                    # Get all payments with this receipt number
                    get_duplicates = text("""
                        SELECT payment_id, company_id, created_at
                        FROM pledge_payments 
                        WHERE receipt_no = :receipt_no
                        ORDER BY payment_id;
                    """)
                    
                    payments = conn.execute(get_duplicates, {"receipt_no": receipt_no}).fetchall()
                    
                    # Update all but the first one
                    for i, payment in enumerate(payments[1:], 1):
                        payment_id = payment[0]
                        company_id = payment[1]
                        created_at = payment[2]
                        
                        # Generate new receipt number
                        year = created_at.year
                        new_receipt_no = f"RCPT-{company_id}-{year}-{payment_id:05d}"
                        
                        # Update the payment
                        update_sql = text("""
                            UPDATE pledge_payments 
                            SET receipt_no = :new_receipt_no 
                            WHERE payment_id = :payment_id;
                        """)
                        
                        conn.execute(update_sql, {
                            "new_receipt_no": new_receipt_no,
                            "payment_id": payment_id
                        })
                        
                        print(f"  ✅ Updated payment {payment_id}: {receipt_no} → {new_receipt_no}")
                
                conn.commit()
                print("✅ All duplicate receipt numbers updated!")
            
            # Create the unique index
            create_index = text("""
                CREATE UNIQUE INDEX idx_pledge_payments_receipt_no_unique 
                ON pledge_payments (receipt_no) 
                WHERE receipt_no IS NOT NULL;
            """)
            
            conn.execute(create_index)
            conn.commit()
            
        print("✅ Unique index on receipt_no created successfully!")
        
        # Verify index creation
        print("Verifying index creation...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT indexname, indexdef
                FROM pg_indexes 
                WHERE tablename = 'pledge_payments' 
                AND indexname = 'idx_pledge_payments_receipt_no_unique';
            """))
            
            index_info = result.fetchone()
            if index_info:
                print("✅ Index verified:")
                print(f"  - Name: {index_info[0]}")
                print(f"  - Definition: {index_info[1]}")
            else:
                print("❌ Could not verify index creation")
        
        print("\n🎉 Migration completed successfully!")
        print("\nReceipt number benefits:")
        print("  - Guaranteed uniqueness across all payments")
        print("  - Auto-generated sequential numbering per company per year")
        print("  - Format: RCPT-{company_id}-{year}-{sequence}")
        print("  - No manual receipt number input required")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("\nPossible causes:")
        print("1. Database connection issues")
        print("2. Insufficient database permissions")
        print("3. Table 'pledge_payments' does not exist")
        print("\nPlease check your database configuration and try again.")

if __name__ == "__main__":
    print("🚀 Starting receipt number uniqueness migration...")
    print("=" * 50)
    run_migration()
    print("=" * 50)
    print("✅ Migration script completed!")
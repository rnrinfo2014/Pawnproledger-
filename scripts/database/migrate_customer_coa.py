"""
Database Migration Script for Customer COA Integration
Adds coa_account_id column to customers table
"""

from database import SessionLocal, engine
from sqlalchemy import text

def add_customer_coa_column():
    """Add coa_account_id column to customers table"""
    
    db = SessionLocal()
    try:
        # Check if column already exists
        check_column = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'customers' 
        AND column_name = 'coa_account_id'
        """
        
        result = db.execute(text(check_column))
        if result.fetchone():
            print("✅ Column 'coa_account_id' already exists in customers table")
            return True
        
        # Add the column
        alter_table = """
        ALTER TABLE customers 
        ADD COLUMN coa_account_id INTEGER 
        REFERENCES accounts_master(account_id)
        """
        
        db.execute(text(alter_table))
        db.commit()
        
        print("✅ Added 'coa_account_id' column to customers table")
        return True
        
    except Exception as e:
        print(f"❌ Error adding column: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def create_index_on_coa_account():
    """Create index on coa_account_id for better performance"""
    
    db = SessionLocal()
    try:
        # Check if index already exists
        check_index = """
        SELECT indexname 
        FROM pg_indexes 
        WHERE tablename = 'customers' 
        AND indexname = 'idx_customers_coa_account_id'
        """
        
        result = db.execute(text(check_index))
        if result.fetchone():
            print("✅ Index 'idx_customers_coa_account_id' already exists")
            return True
        
        # Create index
        create_idx = """
        CREATE INDEX idx_customers_coa_account_id 
        ON customers(coa_account_id)
        """
        
        db.execute(text(create_idx))
        db.commit()
        
        print("✅ Created index on customers.coa_account_id")
        return True
        
    except Exception as e:
        print(f"❌ Error creating index: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Running Customer COA Migration...")
    
    success1 = add_customer_coa_column()
    success2 = create_index_on_coa_account()
    
    if success1 and success2:
        print("🎉 Customer COA migration completed successfully!")
    else:
        print("❌ Migration completed with errors")
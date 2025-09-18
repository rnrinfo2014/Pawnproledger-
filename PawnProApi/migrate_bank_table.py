#!/usr/bin/env python3
"""
Migration script to simplify Bank table
Removes unnecessary columns and renames account_holder_name to account_name
"""

from sqlalchemy import create_engine, text
from config import settings

def migrate_bank_table():
    """Migrate the banks table to simplified version"""
    
    # Create engine
    engine = create_engine(settings.database_url)
    
    # SQL to migrate banks table
    migration_sql = """
    -- First, add the new account_name column if it doesn't exist
    ALTER TABLE banks ADD COLUMN IF NOT EXISTS account_name VARCHAR(200);
    
    -- Copy data from account_holder_name to account_name if account_holder_name exists
    UPDATE banks SET account_name = account_holder_name WHERE account_holder_name IS NOT NULL AND account_name IS NULL;
    
    -- Drop unnecessary columns (use IF EXISTS to avoid errors if already dropped)
    ALTER TABLE banks DROP COLUMN IF EXISTS ifsc_code;
    ALTER TABLE banks DROP COLUMN IF EXISTS account_number;
    ALTER TABLE banks DROP COLUMN IF EXISTS account_holder_name;
    ALTER TABLE banks DROP COLUMN IF EXISTS address;
    ALTER TABLE banks DROP COLUMN IF EXISTS city;
    ALTER TABLE banks DROP COLUMN IF EXISTS state;
    ALTER TABLE banks DROP COLUMN IF EXISTS pincode;
    ALTER TABLE banks DROP COLUMN IF EXISTS phone;
    ALTER TABLE banks DROP COLUMN IF EXISTS email;
    ALTER TABLE banks DROP COLUMN IF EXISTS manager_name;
    ALTER TABLE banks DROP COLUMN IF EXISTS manager_phone;
    ALTER TABLE banks DROP COLUMN IF EXISTS remarks;
    
    -- Update the unique constraint to remove bank+branch requirement (optional)
    ALTER TABLE banks DROP CONSTRAINT IF EXISTS banks_company_bank_branch_unique;
    
    -- Add new simplified unique constraint (optional - only if you want to prevent duplicates)
    ALTER TABLE banks ADD CONSTRAINT banks_company_bank_unique UNIQUE (company_id, bank_name);
    """
    
    try:
        with engine.connect() as connection:
            # Execute the migration
            for statement in migration_sql.split(';'):
                statement = statement.strip()
                if statement:
                    connection.execute(text(statement))
            connection.commit()
            
            print("✅ Bank table migration completed successfully!")
            print("📊 Simplified table structure:")
            print("   - bank_name (required)")
            print("   - branch_name (optional)")
            print("   - account_name (optional)")
            print("   - status (default: active)")
            print("   - company_id (required)")
            print("   - created_at, updated_at (timestamps)")
            print("🗑️ Removed unnecessary columns:")
            print("   - ifsc_code, account_number, address, city, state")
            print("   - pincode, phone, email, manager details, remarks")
            
    except Exception as e:
        print(f"❌ Error migrating banks table: {e}")
        raise

def verify_migration():
    """Verify the migration was successful"""
    engine = create_engine(settings.database_url)
    
    try:
        with engine.connect() as connection:
            # Check table structure
            result = connection.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'banks' 
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            print("\n📋 Current Bank table structure:")
            for column in columns:
                nullable = "NULL" if column[2] == "YES" else "NOT NULL"
                print(f"   - {column[0]}: {column[1]} ({nullable})")
                
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")

if __name__ == "__main__":
    print("🔄 Starting Bank table migration...")
    print("⚠️  This will remove unnecessary columns from the banks table")
    
    response = input("Do you want to continue? (y/N): ")
    if response.lower() in ['y', 'yes']:
        migrate_bank_table()
        verify_migration()
        print("🎉 Migration complete!")
    else:
        print("❌ Migration cancelled")
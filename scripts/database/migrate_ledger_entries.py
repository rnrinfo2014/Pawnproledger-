"""
Database Migration for Enhanced Ledger Entries
Adds new columns for pledge accounting integration
"""

from database import SessionLocal
from sqlalchemy import text

def migrate_ledger_entries_table():
    """Add new columns to ledger_entries table for pledge accounting"""
    
    db = SessionLocal()
    
    try:
        print("🔧 Migrating ledger_entries table...")
        
        # Check and add new columns
        columns_to_add = [
            ("debit", "DECIMAL(15,2) DEFAULT 0.0"),
            ("credit", "DECIMAL(15,2) DEFAULT 0.0"), 
            ("description", "TEXT"),
            ("reference_type", "VARCHAR(20)"),
            ("reference_id", "INTEGER"),
            ("transaction_date", "DATE DEFAULT CURRENT_DATE"),
            ("company_id", "INTEGER REFERENCES companies(id)")
        ]
        
        for column_name, column_def in columns_to_add:
            try:
                # Check if column exists
                check_column = f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'ledger_entries' 
                AND column_name = '{column_name}'
                """
                
                result = db.execute(text(check_column))
                if result.fetchone():
                    print(f"✅ Column '{column_name}' already exists")
                    continue
                
                # Add the column
                alter_sql = f"ALTER TABLE ledger_entries ADD COLUMN {column_name} {column_def}"
                db.execute(text(alter_sql))
                db.commit()
                print(f"✅ Added column '{column_name}'")
                
            except Exception as e:
                print(f"❌ Error adding column '{column_name}': {str(e)}")
                db.rollback()
        
        # Create indexes for performance
        indexes_to_create = [
            ("idx_ledger_entries_reference", "ledger_entries", ["reference_type", "reference_id"]),
            ("idx_ledger_entries_transaction_date", "ledger_entries", ["transaction_date"]),
            ("idx_ledger_entries_company", "ledger_entries", ["company_id"])
        ]
        
        for index_name, table_name, columns in indexes_to_create:
            try:
                # Check if index exists
                check_index = f"""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = '{table_name}' 
                AND indexname = '{index_name}'
                """
                
                result = db.execute(text(check_index))
                if result.fetchone():
                    print(f"✅ Index '{index_name}' already exists")
                    continue
                
                # Create index
                columns_str = ", ".join(columns)
                create_index = f"CREATE INDEX {index_name} ON {table_name}({columns_str})"
                db.execute(text(create_index))
                db.commit()
                print(f"✅ Created index '{index_name}'")
                
            except Exception as e:
                print(f"❌ Error creating index '{index_name}': {str(e)}")
                db.rollback()
        
        # Update existing records to populate new debit/credit columns
        try:
            update_sql = """
            UPDATE ledger_entries 
            SET 
                debit = CASE WHEN dr_cr = 'D' THEN amount ELSE 0 END,
                credit = CASE WHEN dr_cr = 'C' THEN amount ELSE 0 END,
                description = COALESCE(narration, 'Legacy entry'),
                transaction_date = COALESCE(entry_date, CURRENT_DATE),
                company_id = 1
            WHERE debit IS NULL OR credit IS NULL
            """
            
            result = db.execute(text(update_sql))
            db.commit()
            print(f"✅ Updated {result.rowcount} existing records with new column values")
            
        except Exception as e:
            print(f"❌ Error updating existing records: {str(e)}")
            db.rollback()
        
        print("✅ Ledger entries migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Running Ledger Entries Migration...")
    success = migrate_ledger_entries_table()
    
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("❌ Migration failed!")
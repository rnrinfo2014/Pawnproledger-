#!/usr/bin/env python3
"""
Clean existing database tables for fresh testing
"""

import psycopg2

def clean_database_tables():
    """Clean all data from existing tables for fresh testing"""
    
    try:
        # Connect to database
        conn = psycopg2.connect('postgresql://postgres:rnrinfo@localhost:5432/pawnpro')
        cur = conn.cursor()
        
        print("🧹 Cleaning Database for Fresh Testing")
        print("=" * 50)
        
        # List of tables to clean (in dependency order)
        tables_to_clean = [
            'ledger_entries',      # Has foreign keys to voucher_master, accounts_master
            'pledge_payments',     # Has foreign keys to pledges
            'pledge_items',        # Has foreign keys to pledges
            'pledges',            # Has foreign keys to customers
            'voucher_master',     # Has foreign keys to companies
            'customers',          # Has foreign keys to users, companies
            # Keep these tables with data:
            # 'accounts_master',  # Chart of accounts - keep
            # 'companies',        # Company data - keep
            # 'users',           # User accounts - keep
            # 'areas',           # Master data - keep
            # 'banks',           # Master data - keep
        ]
        
        print("🗑️ Tables to be cleaned:")
        for table in tables_to_clean:
            print(f"   • {table}")
        
        # Get current record counts
        print(f"\n📊 Current Record Counts:")
        for table in tables_to_clean:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"   {table}: {count} records")
        
        # Confirm before deletion
        print(f"\n⚠️ WARNING: This will delete all data from the above tables!")
        print(f"📋 The following will be preserved:")
        print(f"   • Chart of Accounts (accounts_master)")
        print(f"   • Companies")
        print(f"   • Users") 
        print(f"   • Master data (areas, banks, etc.)")
        
        confirmation = input(f"\n🤔 Do you want to proceed? (type 'YES' to confirm): ")
        
        if confirmation == 'YES':
            print(f"\n🧹 Cleaning tables...")
            
            # Disable foreign key checks temporarily
            cur.execute("SET session_replication_role = 'replica';")
            
            # Clean tables in reverse dependency order
            for table in reversed(tables_to_clean):
                try:
                    cur.execute(f"DELETE FROM {table}")
                    rows_deleted = cur.rowcount
                    print(f"   ✅ {table}: {rows_deleted} records deleted")
                except Exception as e:
                    print(f"   ❌ {table}: Error - {e}")
            
            # Re-enable foreign key checks
            cur.execute("SET session_replication_role = 'origin';")
            
            # Reset sequences to start from 1
            sequences_to_reset = [
                'voucher_master_voucher_id_seq',
                'ledger_entries_entry_id_seq',
                'customers_customer_id_seq',
                'pledges_pledge_id_seq',
                'pledge_payments_payment_id_seq'
            ]
            
            print(f"\n🔄 Resetting ID sequences...")
            for seq in sequences_to_reset:
                try:
                    cur.execute(f"ALTER SEQUENCE {seq} RESTART WITH 1")
                    print(f"   ✅ {seq} reset to 1")
                except Exception as e:
                    print(f"   ⚠️ {seq}: {e}")
            
            # Commit all changes
            conn.commit()
            
            # Verify cleanup
            print(f"\n✅ Verification - New Record Counts:")
            for table in tables_to_clean:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"   {table}: {count} records")
            
            # Show preserved data
            print(f"\n📋 Preserved Data:")
            preserved_tables = ['accounts_master', 'companies', 'users']
            for table in preserved_tables:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]
                    print(f"   {table}: {count} records")
                except:
                    pass
            
            print(f"\n🎉 Database cleaned successfully!")
            print(f"💡 You can now run fresh tests with clean data")
            
        else:
            print(f"\n❌ Cleanup cancelled")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    clean_database_tables()
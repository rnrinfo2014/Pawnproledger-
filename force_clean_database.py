#!/usr/bin/env python3
"""
Force clean database - Use direct SQL to ensure clean state
"""

import psycopg2
import sys

def force_clean_database():
    """Force clean all transaction tables"""
    
    print("🧹 Force Cleaning Database")
    print("=" * 50)
    
    try:
        # Connect with autocommit for each operation
        conn = psycopg2.connect('postgresql://postgres:rnrinfo@localhost:5432/pawnpro')
        conn.autocommit = True
        cur = conn.cursor()
        
        # Tables to clean in dependency order
        tables_to_clean = [
            'ledger_entries',
            'pledge_payments', 
            'pledge_items',
            'pledges',
            'voucher_master',
            'customers'
        ]
        
        # Check current counts
        print("📊 Current Record Counts:")
        for table in tables_to_clean:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"   {table}: {count} records")
            except Exception as e:
                print(f"   {table}: Error - {e}")
        
        print(f"\n🗑️ Cleaning tables...")
        
        # Clean each table
        for table in tables_to_clean:
            try:
                cur.execute(f"TRUNCATE {table} RESTART IDENTITY CASCADE")
                print(f"   ✅ {table}: Truncated successfully")
            except Exception as e:
                # If truncate fails, try delete
                try:
                    cur.execute(f"DELETE FROM {table}")
                    print(f"   ✅ {table}: Deleted all records")
                except Exception as e2:
                    print(f"   ❌ {table}: Failed - {e2}")
        
        # Verify cleaning
        print(f"\n✅ Verification - New Record Counts:")
        all_clean = True
        for table in tables_to_clean:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                status = "✅ Clean" if count == 0 else f"⚠️ Still has {count} records"
                print(f"   {table}: {status}")
                if count > 0:
                    all_clean = False
            except Exception as e:
                print(f"   {table}: Error - {e}")
        
        # Check preserved data
        print(f"\n📋 Preserved Master Data:")
        master_tables = ['accounts_master', 'companies', 'users']
        for table in master_tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"   {table}: {count} records")
            except Exception as e:
                print(f"   {table}: Error - {e}")
        
        cur.close()
        conn.close()
        
        if all_clean:
            print(f"\n🎉 Database is now completely clean!")
            return True
        else:
            print(f"\n⚠️ Some tables still have data")
            return False
        
    except Exception as e:
        print(f"❌ Database cleaning error: {e}")
        return False

if __name__ == "__main__":
    force_clean_database()
#!/usr/bin/env python3
"""
Check database table names
"""

import psycopg2

def check_tables():
    """Check database table names"""
    
    try:
        conn = psycopg2.connect('postgresql://postgres:rnrinfo@localhost:5432/pawnpro')
        cur = conn.cursor()
        
        # Get all table names
        cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        
        print("📋 Database Tables:")
        account_tables = []
        ledger_tables = []
        voucher_tables = []
        
        for table in tables:
            table_name = table[0]
            print(f"   {table_name}")
            
            if 'account' in table_name.lower():
                account_tables.append(table_name)
            elif 'ledger' in table_name.lower():
                ledger_tables.append(table_name)
            elif 'voucher' in table_name.lower():
                voucher_tables.append(table_name)
        
        print(f"\n🏦 Account Tables: {account_tables}")
        print(f"📖 Ledger Tables: {ledger_tables}")
        print(f"🧾 Voucher Tables: {voucher_tables}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_tables()
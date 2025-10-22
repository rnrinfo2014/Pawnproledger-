#!/usr/bin/env python3
"""
Direct database query to debug balance calculation
"""

import psycopg2
from datetime import date

def debug_database_balance():
    """Debug balance calculation directly from database"""
    
    try:
        # Connect to database
        conn = psycopg2.connect('postgresql://postgres:rnrinfo@localhost:5432/pawnpro')
        cur = conn.cursor()
        
        today = date.today()
        
        print("🔍 Direct Database Balance Debug")
        print("=" * 50)
        
        # Check all ledger entries for today
        cur.execute("""
        SELECT 
            le.entry_id,
            le.voucher_id,
            le.account_id,
            le.dr_cr,
            le.amount,
            le.narration,
            am.account_code,
            am.account_name,
            vm.voucher_type,
            vm.voucher_date
        FROM ledger_entries le
        JOIN accounts_master am ON le.account_id = am.account_id
        JOIN voucher_master vm ON le.voucher_id = vm.voucher_id
        WHERE vm.voucher_date = %s
        AND vm.company_id = 1
        ORDER BY le.entry_id
        """, (today,))
        
        entries = cur.fetchall()
        
        print(f"📋 All Ledger Entries for {today} ({len(entries)} entries):")
        
        cash_balance = 0.0
        total_debits = 0.0
        total_credits = 0.0
        
        for entry in entries:
            entry_id, voucher_id, account_id, dr_cr, amount, narration, account_code, account_name, voucher_type, voucher_date = entry
            
            amount = float(amount)  # Convert Decimal to float
            
            if dr_cr == 'D':
                total_debits += amount
                debit_str = f"₹{amount:.2f}"
                credit_str = "₹0.00"
            else:
                total_credits += amount
                debit_str = "₹0.00"
                credit_str = f"₹{amount:.2f}"
            
            print(f"   {account_code} ({account_name}): Dr: {debit_str}, Cr: {credit_str}")
            print(f"      📝 {narration} ({voucher_type})")
            
            # Track cash account movements (1001, 1002)
            if account_code in ['1001', '1002']:
                if dr_cr == 'D':
                    cash_balance += amount
                    print(f"      💰 Cash +₹{amount:.2f} = ₹{cash_balance:.2f}")
                else:
                    cash_balance -= amount
                    print(f"      💰 Cash -₹{amount:.2f} = ₹{cash_balance:.2f}")
            print()
        
        print(f"🎯 Summary:")
        print(f"   Total Debits: ₹{total_debits:.2f}")
        print(f"   Total Credits: ₹{total_credits:.2f}")
        print(f"   Balance Check: ₹{total_debits - total_credits:.2f}")
        print(f"   Cash Balance: ₹{cash_balance:.2f}")
        
        # Check previous day cash balance
        yesterday = date.today().replace(day=date.today().day - 1) if date.today().day > 1 else date.today()
        
        cur.execute("""
        SELECT 
            SUM(CASE 
                WHEN le.dr_cr = 'D' AND am.account_code IN ('1001', '1002') THEN le.amount
                WHEN le.dr_cr = 'C' AND am.account_code IN ('1001', '1002') THEN -le.amount
                ELSE 0 
            END) as previous_cash_balance
        FROM ledger_entries le
        JOIN accounts_master am ON le.account_id = am.account_id
        JOIN voucher_master vm ON le.voucher_id = vm.voucher_id
        WHERE vm.voucher_date < %s
        AND vm.company_id = 1
        """, (today,))
        
        result = cur.fetchone()
        previous_balance = float(result[0]) if result and result[0] else 0.0
        
        print(f"\n🔄 Previous Days:")
        print(f"   Opening Balance: ₹{previous_balance:.2f}")
        print(f"   Today's Movement: ₹{cash_balance:.2f}")
        print(f"   Expected Closing: ₹{previous_balance + cash_balance:.2f}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    debug_database_balance()
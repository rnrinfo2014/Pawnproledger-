#!/usr/bin/env python3
"""
Debug opening/closing balance calculation
"""

import requests
import json
from datetime import date

BASE_URL = "http://localhost:8000"

def get_auth_headers():
    """Get authentication headers"""
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(f"{BASE_URL}/token", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def debug_balance_calculation():
    """Debug the balance calculation"""
    
    headers = get_auth_headers()
    if not headers:
        return
    
    today = date.today()
    company_id = 1
    
    print("🔍 Debug Balance Calculation")
    print("=" * 50)
    
    # Get all cash account transactions for today
    try:
        response = requests.get(f"{BASE_URL}/ledger-entries", headers=headers)
        if response.status_code == 200:
            all_entries = response.json()
            
            # Filter cash account entries for today
            cash_entries_today = []
            for entry in all_entries:
                # Need to check voucher date - get voucher details
                voucher_response = requests.get(f"{BASE_URL}/vouchers/{entry['voucher_id']}", headers=headers)
                if voucher_response.status_code == 200:
                    voucher = voucher_response.json()
                    if voucher['voucher_date'] == str(today):
                        # Check if it's cash account (1001)
                        account_response = requests.get(f"{BASE_URL}/accounts/{entry['account_id']}", headers=headers)
                        if account_response.status_code == 200:
                            account = account_response.json()
                            if account['account_code'] in ['1001', '1002']:
                                cash_entries_today.append({
                                    'entry': entry,
                                    'account': account,
                                    'voucher': voucher
                                })
            
            print(f"💰 Cash Account Transactions Today ({len(cash_entries_today)} entries):")
            
            total_cash_movement = 0.0
            for item in cash_entries_today:
                entry = item['entry']
                account = item['account']
                voucher = item['voucher']
                
                if entry['dr_cr'] == 'D':
                    movement = +entry['amount']
                    sign = "+"
                else:
                    movement = -entry['amount']
                    sign = ""
                
                total_cash_movement += movement
                
                print(f"   {account['account_code']} ({account['account_name']}): {sign}₹{abs(movement):.2f}")
                print(f"      📝 {entry['narration']} ({voucher['voucher_type']})")
                print(f"      💼 Running: ₹{total_cash_movement:.2f}")
                print()
            
            print(f"🎯 Expected Closing Balance: ₹{total_cash_movement:.2f}")
            
            # Compare with API response
            daybook_response = requests.get(
                f"{BASE_URL}/api/v1/daybook/daily-summary?transaction_date={today}&company_id={company_id}",
                headers=headers
            )
            
            if daybook_response.status_code == 200:
                daybook = daybook_response.json()
                api_opening = daybook.get('opening_balance', 0)
                api_closing = daybook.get('closing_balance', 0)
                
                print(f"📊 API Opening Balance: ₹{api_opening:.2f}")
                print(f"📊 API Closing Balance: ₹{api_closing:.2f}")
                
                if abs(api_closing - total_cash_movement) < 0.01:
                    print("✅ Balance calculation matches!")
                else:
                    print("❌ Balance calculation mismatch!")
                    print(f"   Expected: ₹{total_cash_movement:.2f}")
                    print(f"   API Says: ₹{api_closing:.2f}")
                    print(f"   Difference: ₹{abs(api_closing - total_cash_movement):.2f}")
            
        else:
            print(f"❌ Failed to get ledger entries: {response.text}")
    
    except Exception as e:
        print(f"❌ Debug error: {e}")

if __name__ == "__main__":
    debug_balance_calculation()
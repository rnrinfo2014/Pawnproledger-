#!/usr/bin/env python3
"""
Enhanced manual income/expense test with balance verification
"""

import requests
import json
from datetime import date, datetime, timedelta

BASE_URL = "http://localhost:8000"

def get_auth_headers():
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

def enhanced_balance_test():
    """Enhanced test with proper balance calculation verification"""
    
    print("💰 Enhanced Manual Entry Balance Test")
    print("=" * 50)
    
    headers = get_auth_headers()
    if not headers:
        return
    
    today = date.today()
    company_id = 1
    
    # First, get current cash balance from database query approach
    print("🏦 Cash Balance Verification")
    
    # Get daybook data
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/daybook/daily-summary?transaction_date={today}&company_id={company_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            daybook = response.json()
            
            print(f"📊 Daybook Summary:")
            print(f"   📅 Date: {today}")
            print(f"   📄 Total Vouchers: {daybook['summary']['total_vouchers']}")
            print(f"   💰 Total Debits: ₹{daybook['summary']['total_debit']:,.2f}")
            print(f"   💰 Total Credits: ₹{daybook['summary']['total_credit']:,.2f}")
            print(f"   ⚖️ Balance Difference: ₹{daybook['summary']['balance_difference']:,.2f}")
            
            # Manually calculate cash movements from entries
            cash_balance_change = 0.0
            cash_entries = []
            
            for entry in daybook.get('entries', []):
                if entry.get('account_code') == '1001':  # Cash account
                    movement = entry.get('debit', 0) - entry.get('credit', 0)
                    cash_balance_change += movement
                    cash_entries.append({
                        'narration': entry.get('narration'),
                        'movement': movement,
                        'voucher_type': entry.get('voucher_type')
                    })
            
            print(f"\n💰 Cash Account Analysis:")
            print(f"   🔢 Cash Entries: {len(cash_entries)}")
            for entry in cash_entries:
                sign = "+" if entry['movement'] >= 0 else ""
                print(f"   • {sign}₹{entry['movement']:,.2f} - {entry['narration']} ({entry['voucher_type']})")
            
            print(f"\n📈 Balance Calculations:")
            print(f"   🏦 API Opening Balance: ₹{daybook.get('opening_balance', 0):,.2f}")
            print(f"   💸 Today's Cash Movement: ₹{cash_balance_change:,.2f}")
            print(f"   🏦 API Closing Balance: ₹{daybook.get('closing_balance', 0):,.2f}")
            
            # Expected closing balance
            expected_closing = daybook.get('opening_balance', 0) + cash_balance_change
            actual_closing = daybook.get('closing_balance', 0)
            
            print(f"\n🎯 Balance Verification:")
            print(f"   📊 Expected: ₹{daybook.get('opening_balance', 0):,.2f} + ₹{cash_balance_change:,.2f} = ₹{expected_closing:,.2f}")
            print(f"   📊 Actual API: ₹{actual_closing:,.2f}")
            
            if abs(expected_closing - actual_closing) < 0.01:
                print("   ✅ Balance calculation is correct!")
            else:
                print("   ❌ Balance calculation mismatch!")
                difference = abs(expected_closing - actual_closing)
                print(f"   🔍 Difference: ₹{difference:,.2f}")
                
                # Show what the closing balance should be based on cash movements
                print(f"\n🔧 Suggested Fix:")
                print(f"   The closing balance should be ₹{expected_closing:,.2f}")
                print(f"   This represents opening balance + today's net cash flow")
            
            # Show voucher types breakdown
            if 'voucher_types' in daybook['summary']:
                print(f"\n📋 Voucher Types Today:")
                for vtype, count in daybook['summary']['voucher_types'].items():
                    print(f"   • {vtype}: {count} vouchers")
        
        else:
            print(f"❌ Failed to get daybook: {response.text}")
    
    except Exception as e:
        print(f"❌ Daybook test error: {e}")
    
    print(f"\n✨ Test Complete!")
    print(f"💡 Note: If opening/closing balance shows ₹0.00, the calculation logic may need adjustment")
    print(f"📝 Expected behavior: Opening balance should carry forward from previous days")

if __name__ == "__main__":
    enhanced_balance_test()
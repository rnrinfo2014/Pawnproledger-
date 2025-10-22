#!/usr/bin/env python3
"""
Test daybook API calculation directly
"""

import requests
from datetime import date

def test_daybook_api():
    """Test daybook API and debug the balance calculation"""
    
    # Login and get token
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post("http://localhost:8000/token", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Login failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    today = date.today()
    
    print("🔍 Testing Daybook API Balance Calculation")
    print("=" * 50)
    
    # Test daybook API
    try:
        response = requests.get(
            f"http://localhost:8000/api/v1/daybook/daily-summary?transaction_date={today}&company_id=1",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("📊 API Response:")
            print(f"   Opening Balance: ₹{data.get('opening_balance', 0):.2f}")
            print(f"   Closing Balance: ₹{data.get('closing_balance', 0):.2f}")
            
            summary = data.get('summary', {})
            print(f"   Total Debits: ₹{summary.get('total_debit', 0):.2f}")
            print(f"   Total Credits: ₹{summary.get('total_credit', 0):.2f}")
            
            entries = data.get('entries', [])
            print(f"\n📋 Entries ({len(entries)}):")
            
            cash_movements = []
            for entry in entries:
                if entry.get('account_code') in ['1001', '1002']:
                    cash_movements.append(entry)
                    movement = entry.get('debit', 0) - entry.get('credit', 0)
                    print(f"   💰 {entry.get('account_name')}: {'+' if movement >= 0 else ''}₹{movement:.2f}")
                    print(f"      📝 {entry.get('narration')}")
            
            total_cash_movement = sum(e.get('debit', 0) - e.get('credit', 0) for e in cash_movements)
            print(f"\n🎯 Total Cash Movement: ₹{total_cash_movement:.2f}")
            
            # Expected: Opening + Cash Movement = Closing
            expected_closing = data.get('opening_balance', 0) + total_cash_movement
            actual_closing = data.get('closing_balance', 0)
            
            print(f"🧮 Calculation Check:")
            print(f"   Opening (₹{data.get('opening_balance', 0):.2f}) + Movement (₹{total_cash_movement:.2f}) = ₹{expected_closing:.2f}")
            print(f"   API Closing: ₹{actual_closing:.2f}")
            
            if abs(expected_closing - actual_closing) < 0.01:
                print("   ✅ Balance calculation correct!")
            else:
                print("   ❌ Balance calculation mismatch!")
                print(f"   🔍 Expected: ₹{expected_closing:.2f}, Got: ₹{actual_closing:.2f}")
        
        else:
            print(f"❌ API Error ({response.status_code}): {response.text}")
    
    except Exception as e:
        print(f"❌ API Test Error: {e}")

if __name__ == "__main__":
    test_daybook_api()
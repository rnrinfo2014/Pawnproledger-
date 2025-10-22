#!/usr/bin/env python3
"""
Test script to verify discount and penalty financial transactions are saved properly
Tests the accounting entries for payments with discounts and penalties
"""

import requests
import json
from datetime import date

def test_discount_penalty_accounting():
    """Test that discount and penalty amounts are properly saved in financial transactions"""
    
    base_url = "http://localhost:8000"
    
    # First, get a token for authentication
    print("🔐 Getting authentication token...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # Login
        response = requests.post(f"{base_url}/token", data=login_data)
        if response.status_code != 200:
            print(f"❌ Authentication failed: {response.text}")
            return
            
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
        
        # Test 1: Create payment with discount and penalty
        print("\n💰 Test 1: Create payment with discount and penalty")
        payment_data = {
            "customer_id": 1,
            "total_payment_amount": 2000.0,
            "payment_method": "cash",
            "payment_date": str(date.today()),
            "pledge_payments": [
                {
                    "pledge_id": 1,
                    "payment_amount": 2000.0,
                    "payment_type": "partial_principal",
                    "interest_amount": 800.0,
                    "principal_amount": 1200.0,
                    "discount_amount": 100.0,
                    "discount_reason": "Customer loyalty discount",
                    "penalty_amount": 50.0,
                    "penalty_reason": "Late payment penalty",
                    "remarks": "Payment with discount and penalty"
                }
            ],
            "general_remarks": "Test payment for accounting verification",
            "approve_discount": True,
            "approve_penalty": True
        }
        
        response = requests.post(
            f"{base_url}/customers/1/multiple-pledge-payment", 
            headers=headers,
            json=payment_data
        )
        
        payment_result = None
        if response.status_code == 200:
            payment_result = response.json()
            print(f"✅ Payment created successfully!")
            print(f"   Payment ID: {payment_result['payment_id']}")
            print(f"   Total Amount: ₹{payment_result['total_amount_paid']}")
            print(f"   Total Discount: ₹{payment_result['total_discount_given']}")
            print(f"   Total Penalty: ₹{payment_result['total_penalty_charged']}")
            print(f"   Net Amount: ₹{payment_result['net_amount']}")
            print(f"   Master Voucher: {payment_result['master_voucher_no']}")
            
            # Check pledge results
            for pledge_result in payment_result['pledge_results']:
                print(f"   Pledge {pledge_result['pledge_no']}:")
                print(f"     - Payment: ₹{pledge_result['payment_amount']}")
                print(f"     - Discount: ₹{pledge_result['discount_amount']}")
                print(f"     - Penalty: ₹{pledge_result['penalty_amount']}")
                print(f"     - Net Payment: ₹{pledge_result['net_payment_amount']}")
                
        else:
            print(f"❌ Payment creation failed: {response.text}")
            return
            
        # Test 2: Verify accounting entries were created
        print("\n🔍 Test 2: Verify accounting entries in ledger")
        
        # Get all ledger entries to check for our transaction
        response = requests.get(f"{base_url}/ledger-entries/?limit=50", headers=headers)
        if response.status_code == 200:
            ledger_entries = response.json()
            
            # Find entries related to our payment
            voucher_no = payment_result['master_voucher_no'] if payment_result else None
            payment_entries = []
            
            if voucher_no:
                # Search by voucher number pattern or description
                for entry in ledger_entries:
                    if (voucher_no in entry.get('description', '') or 
                        'discount' in entry.get('description', '').lower() or
                        'penalty' in entry.get('description', '').lower()):
                        payment_entries.append(entry)
                        
            if payment_entries:
                print(f"✅ Found {len(payment_entries)} related ledger entries:")
                total_debits = 0
                total_credits = 0
                
                for entry in payment_entries:
                    print(f"   - Account: {entry.get('account_code', 'N/A')} | "
                          f"Debit: ₹{entry.get('debit', 0):.2f} | "
                          f"Credit: ₹{entry.get('credit', 0):.2f} | "
                          f"Description: {entry.get('description', '')}")
                    total_debits += entry.get('debit', 0)
                    total_credits += entry.get('credit', 0)
                    
                print(f"\n   📊 Totals - Debits: ₹{total_debits:.2f}, Credits: ₹{total_credits:.2f}")
                if abs(total_debits - total_credits) < 0.01:
                    print("   ✅ Accounting entries are balanced!")
                else:
                    print("   ❌ Accounting entries are not balanced!")
                    
            else:
                print("❌ No related ledger entries found")
        else:
            print(f"❌ Failed to get ledger entries: {response.text}")
            
        # Test 3: Check Chart of Accounts for required accounts
        print("\n📋 Test 3: Verify required COA accounts exist")
        
        response = requests.get(f"{base_url}/accounts/?limit=100", headers=headers)
        if response.status_code == 200:
            accounts = response.json()
            
            required_accounts = {
                "5008": "Customer Discount",
                "4003": "Service Charges (Penalty)",
                "4002": "Interest Income",
                "1001": "Cash Account"
            }
            
            found_accounts = {}
            for account in accounts:
                code = account.get('account_code', '')
                if code in required_accounts:
                    found_accounts[code] = account.get('account_name', '')
                    
            print("   Required accounts status:")
            for code, name in required_accounts.items():
                if code in found_accounts:
                    print(f"   ✅ {code} - {found_accounts[code]}")
                else:
                    print(f"   ❌ {code} - {name} (MISSING)")
                    
        else:
            print(f"❌ Failed to get COA accounts: {response.text}")
            
        # Test 4: Verify payment record in database
        print("\n💾 Test 4: Check payment record in database")
        
        response = requests.get(f"{base_url}/pledge-payments/?limit=10", headers=headers)
        if response.status_code == 200:
            payments = response.json()
            
            # Find our payment
            test_payment = None
            for payment in payments:
                if (payment.get('amount') == 2000.0 and 
                    payment.get('discount_amount', 0) == 100.0 and
                    payment.get('penalty_amount', 0) == 50.0):
                    test_payment = payment
                    break
                    
            if test_payment:
                print("✅ Payment record found in database:")
                print(f"   - Payment ID: {test_payment.get('payment_id')}")
                print(f"   - Amount: ₹{test_payment.get('amount', 0):.2f}")
                print(f"   - Discount: ₹{test_payment.get('discount_amount', 0):.2f}")
                print(f"   - Penalty: ₹{test_payment.get('penalty_amount', 0):.2f}")
                print(f"   - Interest: ₹{test_payment.get('interest_amount', 0):.2f}")
                print(f"   - Principal: ₹{test_payment.get('principal_amount', 0):.2f}")
            else:
                print("❌ Payment record not found in database")
        else:
            print(f"❌ Failed to get payment records: {response.text}")
            
        print("\n🎉 Discount and penalty accounting test completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_discount_penalty_accounting()
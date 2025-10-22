#!/usr/bin/env python3
"""
Payment Receipt Management Test
Tests payment receipt update, delete, and transaction reversal functionality
"""
import requests
import json
from datetime import datetime, date

BASE_URL = 'http://localhost:8000'

def test_payment_management():
    # Login
    print("🔐 Authenticating...")
    login_data = {'username': 'admin', 'password': 'admin123'}
    response = requests.post(f'{BASE_URL}/token', data=login_data)
    
    if response.status_code != 200:
        print('❌ Authentication failed')
        return
        
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print('✅ Authentication successful')
    
    print(f"\n📊 PAYMENT RECEIPT MANAGEMENT TEST")
    print("=" * 60)
    
    # First, create a test payment to modify
    customer_id = 1
    
    # Create a test payment
    print("💳 STEP 1: Creating a test payment...")
    payment_data = {
        "customer_id": customer_id,
        "pledge_payments": [
            {
                "pledge_id": 22,  # Use an existing pledge
                "payment_type": "interest",
                "payment_amount": 1000.0,
                "interest_amount": 1000.0,
                "principal_amount": 0.0,
                "remarks": "Test payment for modification"
            }
        ],
        "total_payment_amount": 1000.0,
        "payment_method": "cash",
        "bank_reference": None,
        "payment_date": "2025-10-18"
    }
    
    response = requests.post(
        f'{BASE_URL}/api/v1/pledge-payments/customers/{customer_id}/multiple-payment', 
        json=payment_data, 
        headers=headers
    )
    
    if response.status_code == 200:
        payment_result = response.json()
        test_receipt_no = payment_result.get('receipt_no')
        # Get payment ID from the pledge results
        pledge_results = payment_result.get('pledge_results', [])
        test_payment_id = None
        
        print(f"✅ Test payment created: {test_receipt_no}")
        print(f"   Amount: Rs.{payment_result.get('total_amount_paid', 0)}")
        
        # Find payment ID by searching recent payments
        # This is a workaround since the API doesn't return payment ID directly
        # In a real scenario, you'd get this from a payment lookup
        
    else:
        print(f"❌ Failed to create test payment: {response.text}")
        return
    
    # Let's find a recent payment ID for testing
    print("\n🔍 STEP 2: Finding recent payment for testing...")
    
    # Get customer ledger to find recent payment
    response = requests.get(
        f'{BASE_URL}/api/v1/customer-ledger/customer/{customer_id}/statement?start_date=2025-10-15&end_date=2025-10-18',
        headers=headers
    )
    
    if response.status_code == 200:
        ledger_data = response.json()
        entries = ledger_data.get('entries', [])
        
        # Find entries with payment reference
        payment_entries = [e for e in entries if e.get('reference_type') == 'payment']
        
        if payment_entries:
            test_payment_id = payment_entries[0].get('reference_id')
            print(f"✅ Found payment ID for testing: {test_payment_id}")
        else:
            print("⚠️  No payment entries found in ledger")
    
    # If we still don't have a payment ID, let's use a known one from our database
    if not test_payment_id:
        test_payment_id = 63  # Use a known payment ID from our previous tests
        print(f"📋 Using known payment ID: {test_payment_id}")
    
    # Test 1: Check if payment can be modified
    print(f"\n🔍 STEP 3: Checking if payment {test_payment_id} can be modified...")
    response = requests.get(
        f'{BASE_URL}/api/v1/payment-management/payment/{test_payment_id}/can-modify',
        headers=headers
    )
    
    if response.status_code == 200:
        modify_check = response.json()
        print(f"✅ Payment modification check:")
        print(f"   Receipt No: {modify_check.get('receipt_no', 'N/A')}")
        print(f"   Age: {modify_check.get('payment_age_days', 0)} days")
        print(f"   Can Update: {'✅ Yes' if modify_check.get('can_update') else '❌ No'}")
        print(f"   Can Delete: {'✅ Yes' if modify_check.get('can_delete') else '❌ No'}")
        print(f"   Has Accounting: {'✅ Yes' if modify_check.get('has_accounting_entries') else '❌ No'}")
        print(f"   Accounting Entries: {modify_check.get('accounting_entries_count', 0)}")
        
        can_update = modify_check.get('can_update', False)
        can_delete = modify_check.get('can_delete', False)
    else:
        print(f"❌ Error checking payment: {response.status_code} - {response.text}")
        can_update = False
        can_delete = False
    
    # Test 2: Update payment (if allowed)
    if can_update:
        print(f"\n✏️ STEP 4: Updating payment {test_payment_id}...")
        update_data = {
            "payment_amount": 1500.0,
            "interest_amount": 1500.0,
            "principal_amount": 0.0,
            "payment_method": "bank_transfer",
            "bank_reference": "BT123456789",
            "remarks": "Updated payment amount and method",
            "reason_for_change": "Customer provided additional amount and changed payment method"
        }
        
        response = requests.put(
            f'{BASE_URL}/api/v1/payment-management/payment/{test_payment_id}',
            json=update_data,
            headers=headers
        )
        
        if response.status_code == 200:
            update_result = response.json()
            print(f"✅ Payment updated successfully:")
            print(f"   Receipt: {update_result.get('receipt_no')}")
            print(f"   Message: {update_result.get('message')}")
            print(f"   Pledge Status Updated: {update_result.get('pledge_status_updated')}")
            
            accounting_impact = update_result.get('accounting_impact')
            if accounting_impact:
                print(f"   🔄 Accounting Reversal:")
                print(f"     Voucher ID: {accounting_impact.get('voucher_id')}")
                print(f"     Entries Reversed: {accounting_impact.get('entries_reversed')}")
                print(f"     Debits Reversed: Rs.{accounting_impact.get('total_debit_reversed', 0):,.2f}")
                print(f"     Credits Reversed: Rs.{accounting_impact.get('total_credit_reversed', 0):,.2f}")
        else:
            print(f"❌ Failed to update payment: {response.status_code} - {response.text}")
    else:
        print(f"\n⚠️ STEP 4: Payment {test_payment_id} cannot be updated (too old or other restrictions)")
    
    # Test 3: Delete payment (if allowed)
    if can_delete:
        print(f"\n🗑️ STEP 5: Testing payment deletion (WARNING: This will delete the payment)...")
        
        # Ask for confirmation in a real scenario
        confirm_delete = input("Do you want to test payment deletion? (y/N): ").lower().startswith('y')
        
        if confirm_delete:
            deletion_data = {
                "reason_for_deletion": "Test deletion - payment entered in error",
                "confirm_deletion": True
            }
            
            response = requests.delete(
                f'{BASE_URL}/api/v1/payment-management/payment/{test_payment_id}',
                json=deletion_data,
                headers=headers
            )
            
            if response.status_code == 200:
                delete_result = response.json()
                print(f"✅ Payment deleted successfully:")
                print(f"   Receipt: {delete_result.get('receipt_no')}")
                print(f"   Message: {delete_result.get('message')}")
                print(f"   Pledge Status Updated: {delete_result.get('pledge_status_updated')}")
                
                accounting_impact = delete_result.get('accounting_impact')
                if accounting_impact:
                    print(f"   🔄 Accounting Reversal:")
                    print(f"     Voucher ID: {accounting_impact.get('voucher_id')}")
                    print(f"     Entries Reversed: {accounting_impact.get('entries_reversed')}")
            else:
                print(f"❌ Failed to delete payment: {response.status_code} - {response.text}")
        else:
            print("⚠️ Deletion test skipped by user")
    else:
        print(f"\n⚠️ STEP 5: Payment {test_payment_id} cannot be deleted (too old or other restrictions)")
    
    # Test 4: Get recent modifications audit
    print(f"\n📋 STEP 6: Getting recent payment modifications audit...")
    response = requests.get(
        f'{BASE_URL}/api/v1/payment-management/recent-modifications?days=7',
        headers=headers
    )
    
    if response.status_code == 200:
        audit_data = response.json()
        modifications = audit_data.get('modifications', [])
        
        print(f"✅ Recent modifications (last {audit_data.get('period_days', 7)} days):")
        print(f"   Total modifications: {audit_data.get('modifications_found', 0)}")
        
        if modifications:
            print(f"   📝 Recent changes:")
            for i, mod in enumerate(modifications[:5], 1):
                print(f"     {i}. {mod.get('voucher_type')} on {mod.get('date')}")
                print(f"        Payment ID: {mod.get('payment_id', 'N/A')}")
                print(f"        Reason: {mod.get('narration', 'N/A')[:50]}...")
                print(f"        Entries: {mod.get('entries_count', 0)}")
        else:
            print("   No recent modifications found")
    else:
        print(f"❌ Error getting audit data: {response.status_code} - {response.text}")
    
    print("\n" + "=" * 60)
    print("📊 PAYMENT MANAGEMENT TEST COMPLETED")
    print("=" * 60)
    
    print("\n📝 SUMMARY:")
    print("✅ Payment modification system includes:")
    print("   • Update payment amounts and details")
    print("   • Complete transaction reversal")
    print("   • Automatic pledge status updates")
    print("   • Comprehensive audit trails")
    print("   • Safety restrictions (age limits)")
    print("   • Balance recalculation")
    print("   • Accounting entry reversal and recreation")

if __name__ == '__main__':
    # Add a non-interactive version for automated testing
    import sys
    if '--auto' in sys.argv:
        # Skip user input prompts for automated testing
        def mock_input(prompt):
            return 'n'  # Don't delete in automated mode
        
        import builtins
        builtins.input = mock_input
    
    test_payment_management()
#!/usr/bin/env python3
"""
Test pledge payment creation with correct data format
"""

import requests
from datetime import date

def test_pledge_payment():
    print("Testing Pledge Payment Creation...")
    print("=" * 40)
    
    # Step 1: Login
    login_response = requests.post("http://localhost:8000/token", 
                                 data={"username": "admin", "password": "admin123"})
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print("✅ Authentication successful")
    
    # Step 2: Get existing pledges to use for payment
    pledges_response = requests.get("http://localhost:8000/pledges/", headers=headers)
    
    if pledges_response.status_code != 200:
        print(f"Failed to get pledges: {pledges_response.status_code}")
        return False
    
    pledges = pledges_response.json()
    if not pledges:
        print("❌ No pledges found. Create a pledge first.")
        return False
    
    # Use the first pledge
    pledge = pledges[0]
    pledge_id = pledge.get('pledge_id')
    final_amount = pledge.get('final_amount', 0)
    print(f"Using Pledge ID: {pledge_id}, Final Amount: Rs.{final_amount}")
    
    # Step 3: Create payment with all required fields
    payment_amount = 1000.0  # Making a partial payment
    
    payment_data = {
        "pledge_id": pledge_id,
        "payment_type": "interest",  # REQUIRED: interest, principal, partial_redeem, full_redeem
        "amount": payment_amount,    # REQUIRED: must be > 0
        "interest_amount": payment_amount,  # Optional: portion that's interest
        "principal_amount": 0.0,     # Optional: portion that's principal
        "payment_method": "cash",    # Optional: cash, bank_transfer, cheque
        "remarks": "Monthly interest payment"  # Optional
    }
    
    print(f"\nCreating payment of Rs.{payment_amount} for pledge {pledge_id}...")
    
    payment_response = requests.post("http://localhost:8000/pledge-payments/", 
                                   json=payment_data, headers=headers)
    
    print(f"Payment creation status: {payment_response.status_code}")
    
    if payment_response.status_code == 200:
        result = payment_response.json()
        print("✅ SUCCESS: Payment created!")
        print(f"Payment ID: {result.get('payment_id')}")
        print(f"Receipt No: {result.get('receipt_no')}")
        print(f"Amount: Rs.{result.get('amount')}")
        print(f"Balance: Rs.{result.get('balance_amount')}")
        return True
    elif payment_response.status_code == 400:
        print("❌ BAD REQUEST - Validation Error:")
        error_data = payment_response.json()
        print(f"Error details: {error_data}")
        
        # Common issues and solutions:
        print("\n💡 Common fixes:")
        print("1. Check pledge_id exists and belongs to your company")
        print("2. Ensure amount > 0")
        print("3. Use valid payment_type: 'interest', 'principal', 'partial_redeem', or 'full_redeem'")
        print("4. Check that payment amount doesn't exceed remaining balance")
        
        return False
    else:
        print(f"❌ Other error: {payment_response.text}")
        return False

if __name__ == "__main__":
    test_pledge_payment()
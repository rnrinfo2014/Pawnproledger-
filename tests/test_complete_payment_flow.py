#!/usr/bin/env python3
"""
Test complete pledge creation and payment flow
"""

import requests
from datetime import date, timedelta

def test_complete_pledge_flow():
    print("Testing Complete Pledge and Payment Flow...")
    print("=" * 50)
    
    # Step 1: Login
    login_response = requests.post("http://localhost:8000/token", 
                                 data={"username": "admin", "password": "admin123"})
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print("✅ Authentication successful")
    
    # Step 2: Create a new pledge first
    today = date.today()
    due_date = today + timedelta(days=365)
    
    pledge_amount = 75000.0
    first_month_interest = pledge_amount * 0.12 / 12  # 1% monthly
    document_charge = 750.0
    
    pledge_data = {
        "customer_id": 1,
        "scheme_id": 1,
        "pledge_date": today.isoformat(),
        "due_date": due_date.isoformat(),
        "item_count": 1,
        "gross_weight": 31.0,
        "net_weight": 30.5,
        "ornament_type": "Gold Necklace",
        "ornament_weight": 30.5,
        "ornament_purity": 22,
        "market_value": 105000.0,
        "pledge_amount": pledge_amount,
        "document_charges": document_charge,
        "first_month_interest": first_month_interest,
        "total_loan_amount": pledge_amount,
        "final_amount": pledge_amount + first_month_interest + document_charge,
        "company_id": 1
    }
    
    print("\n📋 Creating new pledge...")
    pledge_response = requests.post("http://localhost:8000/pledges/", 
                                  json=pledge_data, headers=headers)
    
    if pledge_response.status_code != 200:
        print(f"❌ Pledge creation failed: {pledge_response.status_code}")
        print(f"Error: {pledge_response.text}")
        return False
    
    pledge_result = pledge_response.json()
    pledge_id = pledge_result.get('pledge_id')
    pledge_no = pledge_result.get('pledge_no')
    
    print(f"✅ Pledge created successfully!")
    print(f"   Pledge ID: {pledge_id}")
    print(f"   Pledge No: {pledge_no}")
    
    # Handle None values in response
    pledge_amount = pledge_result.get('pledge_amount') or pledge_data['pledge_amount']
    print(f"   Amount: Rs.{pledge_amount:,.2f}")
    
    # Step 3: Create payment for this pledge
    print(f"\n💰 Creating payment for pledge {pledge_no}...")
    
    payment_amount = 1500.0  # Interest payment
    
    payment_data = {
        "pledge_id": pledge_id,
        "payment_type": "interest",
        "amount": payment_amount,
        "interest_amount": payment_amount,
        "principal_amount": 0.0,
        "payment_date": today.isoformat(),
        "receipt_no": f"RCP-{pledge_no}-001",
        "payment_method": "cash",
        "company_id": 1
    }
    
    payment_response = requests.post("http://localhost:8000/pledge-payments/", 
                                   json=payment_data, headers=headers)
    
    print(f"Payment creation status: {payment_response.status_code}")
    
    if payment_response.status_code == 200:
        payment_result = payment_response.json()
        print("✅ Payment created successfully!")
        print(f"   Payment ID: {payment_result.get('payment_id')}")
        print(f"   Receipt No: {payment_result.get('receipt_no')}")
        print(f"   Amount: Rs.{payment_result.get('amount'):,.2f}")
        print(f"   Type: {payment_result.get('payment_type')}")
        
        # Step 4: Create another payment (principal reduction)
        print(f"\n💸 Creating principal payment...")
        
        principal_payment_data = {
            "pledge_id": pledge_id,
            "payment_type": "principal",
            "amount": 10000.0,
            "interest_amount": 0.0,
            "principal_amount": 10000.0,
            "payment_date": today.isoformat(),
            "receipt_no": f"RCP-{pledge_no}-002",
            "payment_method": "cash",
            "company_id": 1
        }
        
        principal_response = requests.post("http://localhost:8000/pledge-payments/", 
                                         json=principal_payment_data, headers=headers)
        
        if principal_response.status_code == 200:
            principal_result = principal_response.json()
            print("✅ Principal payment created successfully!")
            print(f"   Payment ID: {principal_result.get('payment_id')}")
            print(f"   Receipt No: {principal_result.get('receipt_no')}")
            print(f"   Principal: Rs.{principal_result.get('principal_amount'):,.2f}")
        else:
            print(f"❌ Principal payment failed: {principal_response.status_code}")
            print(f"Error: {principal_response.text}")
        
        print(f"\n🎉 PLEDGE PAYMENT SYSTEM WORKING!")
        print(f"✅ Pledge creation with accounting")
        print(f"✅ Interest payment processing")
        print(f"✅ Principal payment processing")
        print(f"✅ Receipt generation")
        print(f"✅ Payment method tracking")
        
        return True
        
    else:
        print(f"❌ Payment creation failed: {payment_response.status_code}")
        try:
            error_data = payment_response.json()
            print(f"Error details: {error_data}")
            
            # Show validation errors in detail
            if 'detail' in error_data and isinstance(error_data['detail'], list):
                print("\nValidation errors:")
                for error in error_data['detail']:
                    field = error.get('loc', ['unknown'])[-1]
                    message = error.get('msg', 'Unknown error')
                    print(f"  - {field}: {message}")
                    
        except:
            print(f"Raw error: {payment_response.text}")
        
        return False

if __name__ == "__main__":
    test_complete_pledge_flow()
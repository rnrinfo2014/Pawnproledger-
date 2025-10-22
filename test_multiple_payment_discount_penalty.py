#!/usr/bin/env python3
"""
Test script for multiple pledge payment with discount and penalty functionality
Tests the enhanced multiple pledge payment API with discount/penalty features
"""

import requests
import json
from datetime import date

def test_multiple_pledge_payment_with_discount_penalty():
    """Test the multiple pledge payment with discount and penalty functionality"""
    
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
        
        # Test 1: Multiple payment with discount only
        print("\n💰 Test 1: Multiple pledge payment with discount")
        payment_data_with_discount = {
            "customer_id": 1,
            "total_payment_amount": 5000.0,
            "payment_method": "cash",
            "payment_date": str(date.today()),
            "pledge_payments": [
                {
                    "pledge_id": 1,
                    "payment_amount": 3000.0,
                    "payment_type": "partial_principal",
                    "interest_amount": 1000.0,
                    "principal_amount": 2000.0,
                    "discount_amount": 100.0,
                    "discount_reason": "Good customer discount",
                    "penalty_amount": 0.0,
                    "remarks": "Partial payment with discount"
                },
                {
                    "pledge_id": 2,
                    "payment_amount": 2000.0,
                    "payment_type": "interest",
                    "interest_amount": 2000.0,
                    "principal_amount": 0.0,
                    "discount_amount": 50.0,
                    "discount_reason": "Early payment discount",
                    "penalty_amount": 0.0,
                    "remarks": "Interest payment with discount"
                }
            ],
            "general_remarks": "Payment with customer loyalty discount",
            "total_discount_amount": 0.0,  # Additional overall discount
            "total_penalty_amount": 0.0,
            "discount_reason": "Customer loyalty program",
            "approve_discount": True,  # Manager approval required
            "approve_penalty": False
        }
        
        response = requests.post(
            f"{base_url}/customers/1/multiple-pledge-payment", 
            headers=headers,
            json=payment_data_with_discount
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Discount payment successful!")
            print(f"   Payment ID: {result['payment_id']}")
            print(f"   Total Amount: ₹{result['total_amount_paid']}")
            print(f"   Total Discount: ₹{result['total_discount_given']}")
            print(f"   Net Amount: ₹{result['net_amount']}")
        else:
            print(f"❌ Discount payment failed: {response.text}")
            
        # Test 2: Multiple payment with penalty only
        print("\n⚠️ Test 2: Multiple pledge payment with penalty")
        payment_data_with_penalty = {
            "customer_id": 1,
            "total_payment_amount": 3000.0,
            "payment_method": "cash",
            "payment_date": str(date.today()),
            "pledge_payments": [
                {
                    "pledge_id": 3,
                    "payment_amount": 3000.0,
                    "payment_type": "full_settlement",
                    "interest_amount": 1500.0,
                    "principal_amount": 1500.0,
                    "discount_amount": 0.0,
                    "penalty_amount": 200.0,
                    "penalty_reason": "Late payment penalty",
                    "remarks": "Full settlement with penalty"
                }
            ],
            "general_remarks": "Late payment with penalty",
            "total_discount_amount": 0.0,
            "total_penalty_amount": 50.0,  # Additional overall penalty
            "penalty_reason": "Processing delay penalty",
            "approve_discount": False,
            "approve_penalty": True  # Manager approval required
        }
        
        response = requests.post(
            f"{base_url}/customers/1/multiple-pledge-payment", 
            headers=headers,
            json=payment_data_with_penalty
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Penalty payment successful!")
            print(f"   Payment ID: {result['payment_id']}")
            print(f"   Total Amount: ₹{result['total_amount_paid']}")
            print(f"   Total Penalty: ₹{result['total_penalty_charged']}")
            print(f"   Net Amount: ₹{result['net_amount']}")
        else:
            print(f"❌ Penalty payment failed: {response.text}")
            
        # Test 3: Multiple payment with both discount and penalty
        print("\n💰⚠️ Test 3: Multiple pledge payment with both discount and penalty")
        payment_data_mixed = {
            "customer_id": 1,
            "total_payment_amount": 4000.0,
            "payment_method": "bank_transfer",
            "bank_reference": "TXN123456789",
            "payment_date": str(date.today()),
            "pledge_payments": [
                {
                    "pledge_id": 4,
                    "payment_amount": 2500.0,
                    "payment_type": "partial_principal",
                    "interest_amount": 1000.0,
                    "principal_amount": 1500.0,
                    "discount_amount": 75.0,
                    "discount_reason": "Volume discount",
                    "penalty_amount": 25.0,
                    "penalty_reason": "Processing fee",
                    "remarks": "Mixed discount and penalty"
                },
                {
                    "pledge_id": 5,
                    "payment_amount": 1500.0,
                    "payment_type": "interest",
                    "interest_amount": 1500.0,
                    "principal_amount": 0.0,
                    "discount_amount": 25.0,
                    "discount_reason": "Prompt payment discount",
                    "penalty_amount": 0.0,
                    "remarks": "Interest payment with discount"
                }
            ],
            "general_remarks": "Mixed payment with both discount and penalty",
            "total_discount_amount": 50.0,  # Additional overall discount
            "total_penalty_amount": 30.0,   # Additional overall penalty
            "discount_reason": "Overall customer discount",
            "penalty_reason": "Overall processing penalty",
            "approve_discount": True,
            "approve_penalty": True
        }
        
        response = requests.post(
            f"{base_url}/customers/1/multiple-pledge-payment", 
            headers=headers,
            json=payment_data_mixed
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Mixed payment successful!")
            print(f"   Payment ID: {result['payment_id']}")
            print(f"   Total Amount: ₹{result['total_amount_paid']}")
            print(f"   Total Discount: ₹{result['total_discount_given']}")
            print(f"   Total Penalty: ₹{result['total_penalty_charged']}")
            print(f"   Net Amount: ₹{result['net_amount']}")
            print(f"   Message: {result['message']}")
        else:
            print(f"❌ Mixed payment failed: {response.text}")
            
        # Test 4: Test validation - discount without approval
        print("\n🚫 Test 4: Validation test - discount without approval")
        invalid_discount_data = {
            "customer_id": 1,
            "total_payment_amount": 1000.0,
            "payment_method": "cash",
            "pledge_payments": [
                {
                    "pledge_id": 1,
                    "payment_amount": 1000.0,
                    "payment_type": "interest",
                    "interest_amount": 1000.0,
                    "principal_amount": 0.0,
                    "discount_amount": 100.0,
                    "discount_reason": "Test discount",
                    "penalty_amount": 0.0
                }
            ],
            "approve_discount": False  # Should fail
        }
        
        response = requests.post(
            f"{base_url}/customers/1/multiple-pledge-payment", 
            headers=headers,
            json=invalid_discount_data
        )
        if response.status_code == 400:
            print(f"✅ Validation working - discount approval required: {response.json()['detail']}")
        else:
            print(f"❌ Validation failed - should have rejected unauthorized discount")
            
        print("\n🎉 All multiple pledge payment discount/penalty tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_multiple_pledge_payment_with_discount_penalty()
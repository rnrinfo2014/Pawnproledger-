#!/usr/bin/env python3
"""
Complete PawnSoft Test Workflow
===============================

Test workflow to verify all functionality:
1. Create new customer
2. Create pledges on different dates  
3. Fetch pending pledges
4. Make partial payments with receipts
5. Verify balances
6. Full pledge closure
"""

import requests
import json
from datetime import date, timedelta
import time

# Configuration
BASE_URL = "http://localhost:8000"

def get_auth_headers():
    """Get authentication headers"""
    login_data = {
        "username": "admin", 
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/token", data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        return {
            "Authorization": f"Bearer {token_data['access_token']}",
            "Content-Type": "application/json"
        }
    else:
        raise Exception(f"Login failed: {response.text}")

def print_step(step_num, title):
    """Print formatted step header"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*60}")

def print_result(success, message, data=None):
    """Print formatted result"""
    status = "SUCCESS" if success else "ERROR"
    print(f"{status}: {message}")
    if data:
        print(f"Data: {json.dumps(data, indent=2)}")

def main():
    print("COMPLETE PAWNSOFT TEST WORKFLOW")
    print("="*80)
    
    try:
        # Get authentication
        headers = get_auth_headers()
        print("Authentication successful!")
        
        # Test variables
        customer_id = 3
        pledge_ids = []
        
        # STEP 1: CREATE NEW CUSTOMER
      #print_step(1, "Create New Customer")
      #
      #customer_data = {
      #    "name": "Test Customer ruban Kumar",
      #    "phone": "9876543240",
      #    "address": "Test Address, T.Nagar, Chennai",
      #    "city": "Chennai", 
      #    "area_id": 1,
      #    "id_proof_type": "Aadhaar Card",
      #    "company_id": 1,
      #    "created_by": 1  # Admin user ID
      #}
      #
      #response = requests.post(f"{BASE_URL}/customers/", json=customer_data, headers=headers)
      #
      #if response.status_code == 200:
      #    customer = response.json()
      #    customer_id = customer["id"]
      #    print_result(True, f"Customer created with ID: {customer_id}")
      #    print(f"Name: {customer['name']}")
      #    print(f"Phone: {customer['phone']}")
      #else:
      #    print_result(False, f"Customer creation failed: {response.text}")
      #    return
            
        # STEP 2: CREATE PLEDGES ON DIFFERENT DATES
        print_step(2, "Create Multiple Pledges on Different Dates")
        
        # Create 3 pledges on different dates
     #edge_dates = [
     #  "2025-10-10",  # 5 days ago
     #  "2025-10-12",  # 3 days ago  
     #  "2025-10-14"   # 1 day ago
     #
     #
     #r i, pledge_date in enumerate(pledge_dates, 1):
     #  print(f"\nCreating Pledge {i} for date: {pledge_date}")
     #  
     #  pledge_data = {
     #      "customer_id": customer_id,
     #      "scheme_id": 1,
     #      "pledge_date": pledge_date,
     #      "due_date": "2025-12-31",
     #      "item_count": 2,
     #      "gross_weight": 50.0,
     #      "net_weight": 45.0,
     #      "document_charges": 100.0,
     #      "first_month_interest": 500.0,
     #      "total_loan_amount": 50000.0,
     #      "final_amount": 50000.0,
     #      "pledge_items": [
     #          {
     #              "jewell_design_id": 1,
     #              "jewell_condition": "Good",
     #              "gross_weight": 25.0,
     #              "net_weight": 22.5,
     #              "net_value": 25000.0,
     #              "remarks": f"Test item {i}.1"
     #          },
     #          {
     #              "jewell_design_id": 1,
     #              "jewell_condition": "Good", 
     #              "gross_weight": 25.0,
     #              "net_weight": 22.5,
     #              "net_value": 25000.0,
     #              "remarks": f"Test item {i}.2"
     #          }
     #      ],
     #      "company_id": 1
     #  }
     #  
     #  response = requests.post(f"{BASE_URL}/pledges/", json=pledge_data, headers=headers)
     #  
     #  if response.status_code == 200:
     #      pledge = response.json()
     #      pledge_ids.append(pledge["pledge_id"])
     #      print_result(True, f"Pledge created with ID: {pledge['pledge_id']}")
     #      print(f"Pledge No: {pledge['pledge_no']}")
     #      print(f"Amount: Rs.{pledge['total_loan_amount']}")
     #  else:
     #      print_result(False, f"Pledge creation failed: {response.text}")
     #
        # STEP 3: FETCH CUSTOMER PENDING PLEDGES
        print_step(3, "Fetch Customer Pending Pledges")
        
        response = requests.get(f"{BASE_URL}/api/v1/pledge-payments/customers/{customer_id}/pending", headers=headers)
        
        if response.status_code == 200:
            pending_data = response.json()
            print_result(True, f"Found {len(pending_data['pledges'])} pending pledges")
            
            total_pending = 0
            for pledge in pending_data['pledges']:
                print(f"Pledge {pledge['pledge_no']}: Rs.{pledge['current_outstanding']} pending")
                pledge_ids.append(pledge['pledge_id'])
                total_pending += pledge['current_outstanding']
            
            print(f"Total pending amount: Rs.{total_pending}")
        else:
            print_result(False, f"Failed to fetch pending pledges: {response.text}")
            return
            
        # STEP 4: MAKE PARTIAL PAYMENTS
        print_step(4, "Make Partial Payments with Receipts")
        
        if pledge_ids:
            # Make partial payment for first pledge
            first_pledge_id = pledge_ids[0]
            
            payment_data = {
                "customer_id": customer_id,
                "pledge_payments": [
                    {
                        "pledge_id": first_pledge_id,
                        "payment_type": "interest",
                        "payment_amount": 2000.0,
                        "interest_amount": 2000.0,
                        "principal_amount": 0.0,
                        "remarks": "Partial interest payment"
                    }
                ],
                "total_payment_amount": 2000.0,
                "payment_method": "cash",
                "bank_reference": None,
                "payment_date": "2025-10-15"
            }
            
            response = requests.post(f"{BASE_URL}/api/v1/pledge-payments/customers/{customer_id}/multiple-payment", 
                                   json=payment_data, headers=headers)
            
            if response.status_code == 200:
                payment_result = response.json()
                print_result(True, f"Partial payment completed!")
                print(f"Payment ID: {payment_result['payment_id']}")
                print(f"Receipt No: {payment_result['receipt_no']}")
                print(f"Amount: Rs.{payment_result['total_amount_paid']}")
            else:
                print_result(False, f"Partial payment failed: {response.text}")
        
        # STEP 5: VERIFY BALANCES AFTER PARTIAL PAYMENT
        print_step(5, "Verify Balances After Partial Payment")
        
        response = requests.get(f"{BASE_URL}/api/v1/pledge-payments/customers/{customer_id}/pending", headers=headers)
        
        if response.status_code == 200:
            updated_pending = response.json()
            print_result(True, f"Balance verification completed")
            
            for pledge in updated_pending['pledges']:
                print(f"Pledge {pledge['pledge_no']}: Rs.{pledge['current_outstanding']} (after payment)")
        else:
            print_result(False, f"Balance verification failed: {response.text}")
            
        # STEP 6: FULL PLEDGE CLOSURE
        print_step(6, "Full Pledge Closure on Current Date")
        
        if pledge_ids:
            # Close the first pledge completely
            response = requests.get(f"{BASE_URL}/api/v1/pledge-payments/customers/{customer_id}/pending", headers=headers)
            
            if response.status_code == 200:
                current_pending = response.json()
                if current_pending['pledges']:
                    first_pledge = current_pending['pledges'][0]
                    remaining_amount = first_pledge['current_outstanding']
                    
                    full_payment_data = {
                        "customer_id": customer_id,
                        "pledge_payments": [
                            {
                                "pledge_id": first_pledge['pledge_id'],
                                "payment_type": "full_redeem",
                                "payment_amount": remaining_amount,
                                "interest_amount": 0.0,
                                "principal_amount": remaining_amount,
                                "remarks": "Full pledge closure"
                            }
                        ],
                        "total_payment_amount": remaining_amount,
                        "payment_method": "cash",
                        "bank_reference": None,
                        "payment_date": date.today().isoformat()
                    }
                    
                    response = requests.post(f"{BASE_URL}/api/v1/pledge-payments/customers/{customer_id}/multiple-payment", 
                                           json=full_payment_data, headers=headers)
                    
                    if response.status_code == 200:
                        closure_result = response.json()
                        print_result(True, f"Pledge fully closed!")
                        print(f"Final Payment ID: {closure_result['payment_id']}")
                        print(f"Final Receipt No: {closure_result['receipt_no']}")
                        print(f"Closure Amount: Rs.{closure_result['total_amount_paid']}")
                    else:
                        print_result(False, f"Full closure failed: {response.text}")
        
        # FINAL VERIFICATION
        print_step("FINAL", "Final Verification - Check Remaining Pending Pledges")
        
        response = requests.get(f"{BASE_URL}/api/v1/pledge-payments/customers/{customer_id}/pending", headers=headers)
        
        if response.status_code == 200:
            final_pending = response.json()
            print_result(True, f"Final verification completed")
            print(f"Remaining pending pledges: {len(final_pending['pledges'])}")
            
            for pledge in final_pending['pledges']:
                print(f"Pledge {pledge['pledge_no']}: Rs.{pledge['current_outstanding']} still pending")
                
        print("\n" + "="*80)
        print("COMPLETE TEST WORKFLOW FINISHED SUCCESSFULLY!")
        print("="*80)
        
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
        print("Test workflow aborted.")

if __name__ == "__main__":
    main()
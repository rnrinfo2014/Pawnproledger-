import requests
import json
from datetime import datetime, date

# Configuration
BASE_URL = "http://localhost:8000"
CUSTOMER_ID = 8  # Use existing customer ID (change this to your customer ID)

def authenticate():
    """Authenticate and get token"""
    auth_response = requests.post(f"{BASE_URL}/token", data={
        "username": "admin",
        "password": "admin123"
    })
    
    if auth_response.status_code == 200:
        token = auth_response.json()["access_token"]
        print("✅ Authentication successful!")
        return {"Authorization": f"Bearer {token}"}
    else:
        print(f"❌ Authentication failed: {auth_response.status_code}")
        print(auth_response.text)
        return None

def test_payment_workflow():
    """Test only payment workflow starting from pending pledges"""
    
    print("PAYMENT TEST WORKFLOW")
    print("=" * 80)
    
    # Authenticate
    headers = authenticate()
    if not headers:
        return
    
    print(f"\n{'='*60}")
    print("STEP 1: Fetch Customer Pending Pledges")
    print(f"{'='*60}")
    
    # Fetch pending pledges
    response = requests.get(
        f"{BASE_URL}/api/v1/pledge-payments/customers/{CUSTOMER_ID}/pending",
        headers=headers
    )
    
    if response.status_code == 200:
        pending_data = response.json()
        print(f"SUCCESS: Found {len(pending_data['pending_pledges'])} pending pledges")
        for pledge in pending_data['pending_pledges']:
            print(f"Pledge {pledge['pledge_no']}: Rs.{pledge['current_outstanding']} pending")
        print(f"Total pending amount: Rs.{pending_data['total_pending_amount']}")
        
        if len(pending_data['pending_pledges']) == 0:
            print("❌ No pending pledges found. Please create some pledges first.")
            return
            
    else:
        print(f"ERROR: Failed to fetch pending pledges: {response.json()}")
        return
    
    print(f"\n{'='*60}")
    print("STEP 2: Make Partial Payment with Receipt")
    print(f"{'='*60}")
    
    # Make partial payment for first pledge
    first_pledge = pending_data['pending_pledges'][0]
    payment_data = {
        "customer_id": CUSTOMER_ID,
        "pledge_payments": [
            {
                "pledge_id": first_pledge['pledge_id'],
                "payment_type": "interest",
                "payment_amount": 1000.0,
                "interest_amount": 1000.0,
                "principal_amount": 0.0,
                "remarks": "Test partial interest payment"
            }
        ],
        "total_payment_amount": 1000.0,
        "payment_method": "cash",
        "payment_date": date.today().isoformat()
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/pledge-payments/customers/{CUSTOMER_ID}/multiple-payment",
        json=payment_data,
        headers=headers
    )
    
    if response.status_code == 200:
        payment_result = response.json()
        print("SUCCESS: Partial payment completed!")
        print(f"Payment ID: {payment_result['payment_id']}")
        print(f"Receipt No: {payment_result['receipt_no']}")
        print(f"Amount: Rs.{payment_result['total_amount_paid']}")
    else:
        print(f"ERROR: Partial payment failed: {response.json()}")
        return
    
    print(f"\n{'='*60}")
    print("STEP 3: Verify Balances After Payment")
    print(f"{'='*60}")
    
    # Fetch updated pending pledges
    response = requests.get(
        f"{BASE_URL}/api/v1/pledge-payments/customers/{CUSTOMER_ID}/pending",
        headers=headers
    )
    
    if response.status_code == 200:
        updated_data = response.json()
        print("SUCCESS: Balance verification completed")
        for pledge in updated_data['pending_pledges']:
            print(f"Pledge {pledge['pledge_no']}: Rs.{pledge['current_outstanding']} (after payment)")
    else:
        print(f"ERROR: Balance verification failed: {response.json()}")
        return
    
    print(f"\n{'='*60}")
    print("STEP 4: Full Pledge Closure")
    print(f"{'='*60}")
    
    # Make full payment for one pledge
    pledge_to_close = updated_data['pending_pledges'][0]
    closure_amount = pledge_to_close['current_outstanding']
    
    closure_data = {
        "customer_id": CUSTOMER_ID,
        "pledge_payments": [
            {
                "pledge_id": pledge_to_close['pledge_id'],
                "payment_type": "full_redeem",
                "payment_amount": closure_amount,
                "interest_amount": 0.0,
                "principal_amount": closure_amount,
                "remarks": "Full pledge closure test"
            }
        ],
        "total_payment_amount": closure_amount,
        "payment_method": "cash",
        "payment_date": date.today().isoformat()
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/pledge-payments/customers/{CUSTOMER_ID}/multiple-payment",
        json=closure_data,
        headers=headers
    )
    
    if response.status_code == 200:
        closure_result = response.json()
        print("SUCCESS: Pledge fully closed!")
        print(f"Final Payment ID: {closure_result['payment_id']}")
        print(f"Final Receipt No: {closure_result['receipt_no']}")
        print(f"Closure Amount: Rs.{closure_result['total_amount_paid']}")
    else:
        print(f"ERROR: Full closure failed: {response.json()}")
        return
    
    print(f"\n{'='*60}")
    print("STEP 5: Final Verification")
    print(f"{'='*60}")
    
    # Final verification
    response = requests.get(
        f"{BASE_URL}/api/v1/pledge-payments/customers/{CUSTOMER_ID}/pending",
        headers=headers
    )
    
    if response.status_code == 200:
        final_data = response.json()
        print("SUCCESS: Final verification completed")
        print(f"Remaining pending pledges: {len(final_data['pending_pledges'])}")
        for pledge in final_data['pending_pledges']:
            print(f"Pledge {pledge['pledge_no']}: Rs.{pledge['current_outstanding']} still pending")
    else:
        print(f"ERROR: Final verification failed: {response.json()}")
        return
    
    print(f"\n{'='*80}")
    print("PAYMENT TEST WORKFLOW COMPLETED!")
    print(f"{'='*80}")

if __name__ == "__main__":
    test_payment_workflow()
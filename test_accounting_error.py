import requests
import json

# Test authentication
BASE_URL = "http://localhost:8000"

# First, authenticate to get token
auth_response = requests.post(f"{BASE_URL}/token", data={
    "username": "admin",
    "password": "admin123"
})

if auth_response.status_code == 200:
    token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful!")
    
    # Test a simple payment to see the detailed error
    payment_data = {
        "customer_id": 7,  # Existing customer
        "pledge_payments": [
            {
                "pledge_id": 36,  # Existing pledge
                "payment_type": "interest",
                "payment_amount": 500.0,
                "interest_amount": 500.0,
                "principal_amount": 0.0,
                "remarks": "Test payment to see accounting error"
            }
        ],
        "total_payment_amount": 500.0,
        "payment_method": "cash",
        "payment_date": "2025-10-15"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/pledge-payments/customers/7/multiple-payment",
        json=payment_data,
        headers=headers
    )
    
    print(f"Payment response status: {response.status_code}")
    print(f"Payment response: {response.json()}")
    
else:
    print(f"Authentication failed: {auth_response.status_code}")
    print(auth_response.text)
import requests
from datetime import date, timedelta

# Test data
BASE_URL = "http://localhost:8000"

# First, let's login to get a token (you'll need to replace with actual credentials)
login_data = {
    "username": "admin",
    "password": "admin123"
}

# Login to get token
response = requests.post(f"{BASE_URL}/token", data=login_data)
if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("✅ Login successful")

    # Test creating a pledge
    pledge_data = {
        "customer_id": 1,
        "scheme_id": 1,
        "pledge_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=30)),
        "item_count": 2,
        "gross_weight": 10.5,
        "net_weight": 9.8,
        "document_charges": 100.0,
        "first_month_interest": 50.0,
        "total_loan_amount": 5000.0,
        "final_amount": 5150.0,
        "company_id": 1,
        "remarks": "Test pledge"
    }

    response = requests.post(f"{BASE_URL}/pledges/", json=pledge_data, headers=headers)
    if response.status_code == 200:
        pledge = response.json()
        print(f"✅ Pledge created: {pledge['pledge_no']}")

        # Test creating pledge items
        pledge_item_data = {
            "pledge_id": pledge["pledge_id"],
            "jewell_design_id": 1,
            "jewell_condition": "Good",
            "gross_weight": 5.5,
            "net_weight": 5.0,
            "net_value": 2500.0,
            "remarks": "Gold necklace"
        }

        response = requests.post(f"{BASE_URL}/pledge-items/", json=pledge_item_data, headers=headers)
        if response.status_code == 200:
            print("✅ Pledge item created")
        else:
            print(f"❌ Failed to create pledge item: {response.text}")

        # Test getting pledges
        response = requests.get(f"{BASE_URL}/pledges/", headers=headers)
        if response.status_code == 200:
            pledges = response.json()
            print(f"✅ Retrieved {len(pledges)} pledges")
        else:
            print(f"❌ Failed to get pledges: {response.text}")

    else:
        print(f"❌ Failed to create pledge: {response.text}")

else:
    print(f"❌ Login failed: {response.text}")
    print("Please ensure the server is running and you have valid credentials")

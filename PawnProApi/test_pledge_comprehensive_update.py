"""
Test script for comprehensive pledge update functionality
"""
import requests
import json
from datetime import date, datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_PLEDGE_ID = 1  # Replace with actual pledge ID

# Sample test data for comprehensive update
test_update_data = {
    # Basic pledge updates
    "pledge_date": "2024-01-15",
    "due_date": "2024-12-15", 
    "document_charges": 150.0,
    "remarks": "Updated pledge with comprehensive changes",
    "status": "active",
    
    # Customer updates
    "customer_updates": {
        "address": "Updated Address 123",
        "city": "Updated City"
    },
    
    # Pledge item operations
    "item_operations": [
        {
            "operation": "add",
            "jewell_design_id": 1,
            "jewell_condition": "Good",
            "gross_weight": 10.5,
            "net_weight": 9.8,
            "net_value": 45000.0,
            "remarks": "New gold ring added"
        },
        {
            "operation": "update", 
            "pledge_item_id": 1,  # Replace with actual item ID
            "gross_weight": 12.0,
            "net_weight": 11.2,
            "remarks": "Updated weight after re-measurement"
        }
    ],
    
    # Recalculation flags
    "recalculate_weights": True,
    "recalculate_item_count": True,
    "recalculate_financials": False
}

def test_comprehensive_pledge_update():
    """Test the comprehensive pledge update endpoint"""
    
    # First, let's get a valid token (you'll need to implement login)
    # For now, we'll assume we have a token
    headers = {
        "Authorization": "Bearer YOUR_TOKEN_HERE",  # Replace with actual token
        "Content-Type": "application/json"
    }
    
    # Make the update request
    response = requests.put(
        f"{BASE_URL}/pledges/{TEST_PLEDGE_ID}/comprehensive-update",
        headers=headers,
        json=test_update_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n=== UPDATE SUCCESS ===")
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Items Added: {result.get('items_added')}")
        print(f"Items Updated: {result.get('items_updated')}")
        print(f"Items Removed: {result.get('items_removed')}")
        print(f"Warnings: {result.get('warnings')}")
        print(f"Changes Summary: {json.dumps(result.get('changes_summary'), indent=2)}")
        
        # Print updated pledge details
        updated_pledge = result.get('updated_pledge')
        if updated_pledge:
            print(f"\n=== UPDATED PLEDGE DETAILS ===")
            print(f"Pledge ID: {updated_pledge.get('pledge_id')}")
            print(f"Pledge No: {updated_pledge.get('pledge_no')}")
            print(f"Customer: {updated_pledge.get('customer', {}).get('name')}")
            print(f"Total Items: {updated_pledge.get('item_count')}")
            print(f"Gross Weight: {updated_pledge.get('gross_weight')}")
            print(f"Net Weight: {updated_pledge.get('net_weight')}")
            print(f"Status: {updated_pledge.get('status')}")
            print(f"Items in pledge: {len(updated_pledge.get('pledge_items', []))}")
    
    elif response.status_code == 404:
        print("ERROR: Pledge not found")
    elif response.status_code == 400:
        error_detail = response.json().get('detail', 'Bad request')
        print(f"ERROR: {error_detail}")
    elif response.status_code == 401:
        print("ERROR: Unauthorized - check your token")
    else:
        print(f"ERROR: {response.text}")

def test_various_scenarios():
    """Test different update scenarios"""
    
    scenarios = [
        {
            "name": "Customer Transfer",
            "data": {"change_customer_id": 2}  # Transfer to different customer
        },
        {
            "name": "Scheme Change", 
            "data": {"scheme_id": 2, "recalculate_financials": True}
        },
        {
            "name": "Date Updates",
            "data": {
                "pledge_date": "2024-02-01", 
                "due_date": "2025-02-01"
            }
        },
        {
            "name": "Remove Item",
            "data": {
                "item_operations": [
                    {"operation": "remove", "pledge_item_id": 1}
                ],
                "recalculate_weights": True,
                "recalculate_item_count": True
            }
        },
        {
            "name": "Status Change",
            "data": {"status": "redeemed"}
        }
    ]
    
    for scenario in scenarios:
        print(f"\n=== Testing: {scenario['name']} ===")
        # Here you would make the API call with scenario['data']
        # Similar to test_comprehensive_pledge_update() but with scenario data
        print(f"Would test with data: {json.dumps(scenario['data'], indent=2)}")

if __name__ == "__main__":
    print("=== COMPREHENSIVE PLEDGE UPDATE TESTS ===")
    print("\nNote: Before running these tests:")
    print("1. Start your FastAPI server")
    print("2. Replace TEST_PLEDGE_ID with a valid pledge ID")
    print("3. Replace YOUR_TOKEN_HERE with a valid JWT token")
    print("4. Ensure you have valid jewell_design_id and pledge_item_id values")
    
    # Uncomment these lines to run actual tests
    # test_comprehensive_pledge_update()
    # test_various_scenarios()
    
    print("\nTest scenarios defined. Update the configuration and uncomment test calls to run.")
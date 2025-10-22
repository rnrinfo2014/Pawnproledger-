#!/usr/bin/env python3
"""
Test script for Pledge with Items CRUD endpoints
Tests comprehensive pledge creation and update with items in single transactions.
"""

import requests
import json
from datetime import datetime, date

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "admin"  # Replace with your username
PASSWORD = "admin123"  # Replace with your password

class PledgeWithItemsAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.headers = {}
        self.created_pledge_id = None
        self.customer_id = None
        self.scheme_id = None
        self.jewell_design_ids = []

    def authenticate(self):
        """Authenticate and get access token"""
        auth_data = {
            "username": USERNAME,
            "password": PASSWORD
        }
        
        response = requests.post(f"{self.base_url}/token", data=auth_data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return False

    def setup_test_data(self):
        """Get required test data (customers, schemes, designs)"""
        print("\n📋 Setting up test data...")
        
        # Get customers
        response = requests.get(f"{self.base_url}/customers/?limit=1", headers=self.headers)
        if response.status_code == 200:
            customers = response.json()
            if customers:
                self.customer_id = customers[0]["id"]
                print(f"✅ Using customer ID: {self.customer_id}")
            else:
                print("❌ No customers found. Create a customer first.")
                return False
        else:
            print(f"❌ Failed to get customers: {response.status_code}")
            return False

        # Get schemes
        response = requests.get(f"{self.base_url}/schemes/?limit=1", headers=self.headers)
        if response.status_code == 200:
            schemes = response.json()
            if schemes:
                self.scheme_id = schemes[0]["id"]
                print(f"✅ Using scheme ID: {self.scheme_id}")
            else:
                print("❌ No schemes found. Create a scheme first.")
                return False
        else:
            print(f"❌ Failed to get schemes: {response.status_code}")
            return False

        # Get jewell designs
        response = requests.get(f"{self.base_url}/jewell-designs/?limit=3", headers=self.headers)
        if response.status_code == 200:
            designs = response.json()
            if len(designs) >= 2:
                self.jewell_design_ids = [design["id"] for design in designs[:3]]
                print(f"✅ Using jewell design IDs: {self.jewell_design_ids}")
            else:
                print("❌ Need at least 2 jewell designs. Create more designs first.")
                return False
        else:
            print(f"❌ Failed to get jewell designs: {response.status_code}")
            return False

        return True

    def test_create_pledge_with_items(self):
        """Test creating a new pledge with multiple items"""
        print("\n🏦 Testing Pledge Creation with Items...")
        
        pledge_data = {
            "customer_id": self.customer_id,
            "scheme_id": self.scheme_id,
            "pledge_date": "2025-09-15",
            "due_date": "2025-12-15",
            "document_charges": 100.0,
            "first_month_interest": 500.0,
            "total_loan_amount": 50000.0,
            "final_amount": 50500.0,
            "status": "active",
            "is_move_to_bank": False,
            "remarks": "Test pledge with multiple items",
            "auto_calculate_weights": True,
            "auto_calculate_item_count": True,
            "items": [
                {
                    "jewell_design_id": self.jewell_design_ids[0],
                    "jewell_condition": "Excellent",
                    "gross_weight": 25.5,
                    "net_weight": 24.0,
                    "net_value": 25000.0,
                    "remarks": "Gold ring with diamonds"
                },
                {
                    "jewell_design_id": self.jewell_design_ids[1],
                    "jewell_condition": "Good",
                    "gross_weight": 15.2,
                    "net_weight": 14.8,
                    "net_value": 15000.0,
                    "remarks": "Gold chain"
                },
                {
                    "jewell_design_id": self.jewell_design_ids[0],
                    "jewell_condition": "Very Good",
                    "gross_weight": 12.3,
                    "net_weight": 11.9,
                    "net_value": 12000.0,
                    "remarks": "Gold earrings"
                }
            ]
        }
        
        response = requests.post(f"{self.base_url}/pledges/with-items", 
                               json=pledge_data, 
                               headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            self.created_pledge_id = result["pledge"]["pledge_id"]
            print(f"✅ Pledge created successfully!")
            print(f"   Pledge ID: {self.created_pledge_id}")
            print(f"   Pledge No: {result['pledge']['pledge_no']}")
            print(f"   Items Created: {result['items_created']}")
            print(f"   Total Weight: {result['pledge']['gross_weight']}g (gross), {result['pledge']['net_weight']}g (net)")
            print(f"   Item Count: {result['pledge']['item_count']}")
            return True
        else:
            print(f"❌ Pledge creation failed: {response.status_code} - {response.text}")
            return False

    def test_update_pledge_add_items(self):
        """Test updating pledge by adding new items"""
        if not self.created_pledge_id:
            print("⚠️ Skipping add items test - no pledge created")
            return False
            
        print(f"\n➕ Testing Add Items to Pledge ({self.created_pledge_id})...")
        
        update_data = {
            "remarks": "Updated with additional items",
            "auto_calculate_weights": True,
            "auto_calculate_item_count": True,
            "items": [
                {
                    "jewell_design_id": self.jewell_design_ids[1],
                    "jewell_condition": "Excellent",
                    "gross_weight": 8.5,
                    "net_weight": 8.2,
                    "net_value": 8500.0,
                    "remarks": "Additional gold bracelet",
                    "action": "add"
                },
                {
                    "jewell_design_id": self.jewell_design_ids[0],
                    "jewell_condition": "Good",
                    "gross_weight": 5.0,
                    "net_weight": 4.8,
                    "net_value": 5000.0,
                    "remarks": "Small gold pendant",
                    "action": "add"
                }
            ]
        }
        
        response = requests.put(f"{self.base_url}/pledges/{self.created_pledge_id}/with-items",
                              json=update_data,
                              headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Items added successfully!")
            print(f"   Items Added: {result['items_created']}")
            print(f"   New Total Weight: {result['pledge']['gross_weight']}g (gross), {result['pledge']['net_weight']}g (net)")
            print(f"   New Item Count: {result['pledge']['item_count']}")
            return True
        else:
            print(f"❌ Add items failed: {response.status_code} - {response.text}")
            return False

    def test_update_pledge_modify_items(self):
        """Test updating existing pledge items"""
        if not self.created_pledge_id:
            print("⚠️ Skipping modify items test - no pledge created")
            return False
            
        print(f"\n✏️ Testing Modify Existing Items ({self.created_pledge_id})...")
        
        # First get current pledge items
        response = requests.get(f"{self.base_url}/pledges/{self.created_pledge_id}/items", 
                              headers=self.headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to get current items: {response.status_code}")
            return False
        
        current_items = response.json()
        if not current_items:
            print("❌ No items found to modify")
            return False
        
        # Update the first item
        first_item = current_items[0]
        update_data = {
            "auto_calculate_weights": True,
            "auto_calculate_item_count": True,
            "items": [
                {
                    "pledge_item_id": first_item["pledge_item_id"],
                    "jewell_design_id": first_item["jewell_design_id"],
                    "jewell_condition": "Modified - Excellent Plus",
                    "gross_weight": first_item["gross_weight"] + 2.0,  # Increase weight
                    "net_weight": first_item["net_weight"] + 1.8,
                    "net_value": first_item["net_value"] + 2000.0,  # Increase value
                    "remarks": "Updated item with higher valuation",
                    "action": "update"
                }
            ]
        }
        
        response = requests.put(f"{self.base_url}/pledges/{self.created_pledge_id}/with-items",
                              json=update_data,
                              headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Items updated successfully!")
            print(f"   Items Updated: {result['items_updated']}")
            print(f"   Updated Total Weight: {result['pledge']['gross_weight']}g (gross), {result['pledge']['net_weight']}g (net)")
            return True
        else:
            print(f"❌ Update items failed: {response.status_code} - {response.text}")
            return False

    def test_update_pledge_delete_items(self):
        """Test deleting pledge items"""
        if not self.created_pledge_id:
            print("⚠️ Skipping delete items test - no pledge created")
            return False
            
        print(f"\n🗑️ Testing Delete Items from Pledge ({self.created_pledge_id})...")
        
        # Get current pledge items
        response = requests.get(f"{self.base_url}/pledges/{self.created_pledge_id}/items", 
                              headers=self.headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to get current items: {response.status_code}")
            return False
        
        current_items = response.json()
        if len(current_items) < 2:
            print("❌ Need at least 2 items to test deletion")
            return False
        
        # Delete the last item using delete_item_ids
        last_item_id = current_items[-1]["pledge_item_id"]
        update_data = {
            "auto_calculate_weights": True,
            "auto_calculate_item_count": True,
            "delete_item_ids": [last_item_id]
        }
        
        response = requests.put(f"{self.base_url}/pledges/{self.created_pledge_id}/with-items",
                              json=update_data,
                              headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Items deleted successfully!")
            print(f"   Items Deleted: {result['items_deleted']}")
            print(f"   Updated Total Weight: {result['pledge']['gross_weight']}g (gross), {result['pledge']['net_weight']}g (net)")
            print(f"   Updated Item Count: {result['pledge']['item_count']}")
            return True
        else:
            print(f"❌ Delete items failed: {response.status_code} - {response.text}")
            return False

    def test_comprehensive_update(self):
        """Test comprehensive update: modify pledge + add/update/delete items"""
        if not self.created_pledge_id:
            print("⚠️ Skipping comprehensive update test - no pledge created")
            return False
            
        print(f"\n🔄 Testing Comprehensive Update ({self.created_pledge_id})...")
        
        # Get current items first
        response = requests.get(f"{self.base_url}/pledges/{self.created_pledge_id}/items", 
                              headers=self.headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to get current items: {response.status_code}")
            return False
        
        current_items = response.json()
        
        update_data = {
            # Update pledge information
            "total_loan_amount": 60000.0,
            "final_amount": 60600.0,
            "remarks": "Comprehensively updated pledge with mixed item operations",
            "auto_calculate_weights": True,
            "auto_calculate_item_count": True,
            
            # Mixed item operations
            "items": [
                # Add new item
                {
                    "jewell_design_id": self.jewell_design_ids[1],
                    "jewell_condition": "New Addition - Excellent",
                    "gross_weight": 10.0,
                    "net_weight": 9.5,
                    "net_value": 10000.0,
                    "remarks": "Newly added item in comprehensive update",
                    "action": "add"
                }
            ]
        }
        
        # If we have items, update one of them
        if current_items:
            update_data["items"].append({
                "pledge_item_id": current_items[0]["pledge_item_id"],
                "jewell_design_id": current_items[0]["jewell_design_id"],
                "jewell_condition": "Comprehensive Update - Premium",
                "gross_weight": current_items[0]["gross_weight"] + 1.0,
                "net_weight": current_items[0]["net_weight"] + 0.9,
                "net_value": current_items[0]["net_value"] + 1000.0,
                "remarks": "Updated in comprehensive update",
                "action": "update"
            })
        
        response = requests.put(f"{self.base_url}/pledges/{self.created_pledge_id}/with-items",
                              json=update_data,
                              headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Comprehensive update successful!")
            print(f"   Items Added: {result['items_created']}")
            print(f"   Items Updated: {result['items_updated']}")
            print(f"   Items Deleted: {result['items_deleted']}")
            print(f"   Final Total Weight: {result['pledge']['gross_weight']}g (gross), {result['pledge']['net_weight']}g (net)")
            print(f"   Final Item Count: {result['pledge']['item_count']}")
            print(f"   Final Loan Amount: {result['pledge']['total_loan_amount']}")
            
            if result['warnings']:
                print(f"   Warnings: {result['warnings']}")
            
            return True
        else:
            print(f"❌ Comprehensive update failed: {response.status_code} - {response.text}")
            return False

    def test_error_scenarios(self):
        """Test various error scenarios"""
        print("\n🛡️ Testing Error Scenarios...")
        
        # Test creating pledge without items
        pledge_data = {
            "customer_id": self.customer_id,
            "scheme_id": self.scheme_id,
            "pledge_date": "2025-09-15",
            "due_date": "2025-12-15",
            "total_loan_amount": 10000.0,
            "final_amount": 10500.0,
            "items": []  # Empty items
        }
        
        response = requests.post(f"{self.base_url}/pledges/with-items", 
                               json=pledge_data, 
                               headers=self.headers)
        
        if response.status_code == 400:
            print("✅ Correctly rejected empty items list")
        else:
            print(f"❌ Should have rejected empty items: {response.status_code}")
        
        # Test with invalid customer ID
        pledge_data["customer_id"] = 99999
        pledge_data["items"] = [{
            "jewell_design_id": self.jewell_design_ids[0],
            "jewell_condition": "Good",
            "gross_weight": 10.0,
            "net_weight": 9.5,
            "net_value": 10000.0
        }]
        
        response = requests.post(f"{self.base_url}/pledges/with-items", 
                               json=pledge_data, 
                               headers=self.headers)
        
        if response.status_code == 400:
            print("✅ Correctly rejected invalid customer ID")
        else:
            print(f"❌ Should have rejected invalid customer: {response.status_code}")
        
        return True

    def run_all_tests(self):
        """Run all Pledge with Items API tests"""
        print("🚀 Starting Pledge with Items API Tests")
        print("=" * 60)
        
        if not self.authenticate():
            return
        
        if not self.setup_test_data():
            return
        
        tests = [
            self.test_create_pledge_with_items,
            self.test_update_pledge_add_items,
            self.test_update_pledge_modify_items,
            self.test_update_pledge_delete_items,
            self.test_comprehensive_update,
            self.test_error_scenarios
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        print("\n" + "=" * 60)
        print(f"🎯 Test Summary: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All Pledge with Items API tests completed successfully!")
            if self.created_pledge_id:
                print(f"💡 Created pledge ID {self.created_pledge_id} for further testing")
        else:
            print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    tester = PledgeWithItemsAPITester()
    tester.run_all_tests()
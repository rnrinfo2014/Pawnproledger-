"""
Test script for Pledge Listing APIs
Tests the new customer and scheme pledge listing endpoints

Run with: python test_pledge_listing_api.py
"""

import requests
import json
from datetime import date, datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

class TestPledgeListingAPI:
    """Test suite for Pledge Listing APIs"""
    
    def __init__(self):
        self.token = self.get_auth_token()
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.test_customer_id = None
        self.test_scheme_id = None
    
    def get_auth_token(self):
        """Get authentication token for tests"""
        login_data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/token", data=login_data)
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            raise Exception(f"Failed to authenticate: {response.text}")
    
    def setup_test_data(self):
        """Get test customer and scheme IDs"""
        # Get first customer
        response = requests.get(f"{BASE_URL}/customers", headers=self.headers)
        if response.status_code == 200:
            customers = response.json()
            if customers:
                self.test_customer_id = customers[0]["id"]
                print(f"✅ Using test customer ID: {self.test_customer_id}")
        
        # Get first scheme
        response = requests.get(f"{BASE_URL}/schemes", headers=self.headers)
        if response.status_code == 200:
            schemes = response.json()
            if schemes:
                self.test_scheme_id = schemes[0]["id"]
                print(f"✅ Using test scheme ID: {self.test_scheme_id}")
    
    def test_customer_active_pledges(self):
        """Test GET /customers/{customer_id}/pledges/active"""
        if not self.test_customer_id:
            print("❌ No test customer available")
            return False
        
        print(f"\\n🧪 Testing customer active pledges for customer {self.test_customer_id}...")
        
        response = requests.get(
            f"{BASE_URL}/customers/{self.test_customer_id}/pledges/active",
            headers=self.headers
        )
        
        if response.status_code == 200:
            pledges = response.json()
            print(f"✅ Retrieved {len(pledges)} active pledges")
            
            if pledges:
                pledge = pledges[0]
                required_fields = [
                    "id", "customer_id", "scheme_id", "principal_amount", 
                    "interest_rate", "start_date", "maturity_date", 
                    "remaining_principal", "status", "created_at"
                ]
                
                missing_fields = [field for field in required_fields if field not in pledge]
                if missing_fields:
                    print(f"❌ Missing fields: {missing_fields}")
                    return False
                
                # Verify status is ACTIVE
                if pledge["status"] not in ["ACTIVE"]:
                    print(f"❌ Expected ACTIVE status, got: {pledge['status']}")
                    return False
                
                print(f"✅ Sample pledge: ID={pledge['id']}, Principal=${pledge['principal_amount']}, Status={pledge['status']}")
            else:
                print("ℹ️  No active pledges found for this customer")
            
            return True
        else:
            print(f"❌ Request failed: {response.status_code} - {response.text}")
            return False
    
    def test_customer_all_pledges(self):
        """Test GET /customers/{customer_id}/pledges"""
        if not self.test_customer_id:
            print("❌ No test customer available")
            return False
        
        print(f"\\n🧪 Testing all customer pledges for customer {self.test_customer_id}...")
        
        response = requests.get(
            f"{BASE_URL}/customers/{self.test_customer_id}/pledges",
            headers=self.headers
        )
        
        if response.status_code == 200:
            pledges = response.json()
            print(f"✅ Retrieved {len(pledges)} total pledges")
            
            if pledges:
                # Check status variety
                statuses = set(pledge["status"] for pledge in pledges)
                print(f"✅ Found statuses: {list(statuses)}")
                
                # Verify schema
                pledge = pledges[0]
                if "closed_at" not in pledge:
                    print("❌ Missing closed_at field")
                    return False
                
                print(f"✅ Sample pledge: ID={pledge['id']}, Status={pledge['status']}")
            else:
                print("ℹ️  No pledges found for this customer")
            
            return True
        else:
            print(f"❌ Request failed: {response.status_code} - {response.text}")
            return False
    
    def test_scheme_active_pledges(self):
        """Test GET /schemes/{scheme_id}/pledges/active"""
        if not self.test_scheme_id:
            print("❌ No test scheme available")
            return False
        
        print(f"\\n🧪 Testing scheme active pledges for scheme {self.test_scheme_id}...")
        
        response = requests.get(
            f"{BASE_URL}/schemes/{self.test_scheme_id}/pledges/active",
            headers=self.headers
        )
        
        if response.status_code == 200:
            pledges = response.json()
            print(f"✅ Retrieved {len(pledges)} active pledges for scheme")
            
            if pledges:
                # Verify all pledges belong to the scheme
                for pledge in pledges:
                    if pledge["scheme_id"] != self.test_scheme_id:
                        print(f"❌ Pledge {pledge['id']} has wrong scheme_id: {pledge['scheme_id']}")
                        return False
                
                print(f"✅ All pledges belong to scheme {self.test_scheme_id}")
            else:
                print("ℹ️  No active pledges found for this scheme")
            
            return True
        else:
            print(f"❌ Request failed: {response.status_code} - {response.text}")
            return False
    
    def test_pagination(self):
        """Test pagination parameters"""
        if not self.test_customer_id:
            print("❌ No test customer available")
            return False
        
        print(f"\\n🧪 Testing pagination...")
        
        # Test with limit
        response = requests.get(
            f"{BASE_URL}/customers/{self.test_customer_id}/pledges?limit=5",
            headers=self.headers
        )
        
        if response.status_code == 200:
            pledges = response.json()
            print(f"✅ Pagination test: Retrieved {len(pledges)} pledges (limit=5)")
            
            if len(pledges) <= 5:
                print("✅ Pagination limit respected")
                return True
            else:
                print("❌ Pagination limit not respected")
                return False
        else:
            print(f"❌ Pagination test failed: {response.status_code}")
            return False
    
    def test_unauthorized_access(self):
        """Test access without proper authentication"""
        print(f"\\n🧪 Testing unauthorized access...")
        
        # Test without token
        response = requests.get(f"{BASE_URL}/customers/1/pledges/active")
        if response.status_code == 401:
            print("✅ Unauthorized access properly blocked")
            return True
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            return False
    
    def test_not_found_scenarios(self):
        """Test with non-existent customer/scheme IDs"""
        print(f"\\n🧪 Testing not found scenarios...")
        
        # Test with non-existent customer
        response = requests.get(
            f"{BASE_URL}/customers/99999/pledges/active",
            headers=self.headers
        )
        
        if response.status_code == 404:
            print("✅ Non-existent customer properly handled")
            return True
        else:
            print(f"❌ Expected 404 for non-existent customer, got {response.status_code}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Pledge Listing API Tests...")
        print("=" * 60)
        
        # Setup
        self.setup_test_data()
        
        # Run tests
        tests = [
            ("Customer Active Pledges", self.test_customer_active_pledges),
            ("Customer All Pledges", self.test_customer_all_pledges),
            ("Scheme Active Pledges", self.test_scheme_active_pledges),
            ("Pagination", self.test_pagination),
            ("Unauthorized Access", self.test_unauthorized_access),
            ("Not Found Scenarios", self.test_not_found_scenarios),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {str(e)}")
        
        print("=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Pledge listing APIs are working correctly.")
        else:
            print(f"⚠️  {total - passed} tests failed. Please check the implementation.")
        
        return passed == total

def main():
    """Main test execution"""
    print("Pledge Listing API Test Suite")
    print("Make sure the API server is running on http://localhost:8000")
    print("=" * 60)
    
    try:
        # Quick connectivity test
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ API server is not responding. Please start the server first.")
            return False
        
        print("✅ API server is running")
        
        # Run tests
        tester = TestPledgeListingAPI()
        return tester.run_all_tests()
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Please start the server first.")
        return False
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
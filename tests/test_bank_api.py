#!/usr/bin/env python3
"""
Test script for Bank CRUD endpoints
Tests all Bank API operations including create, read, update, delete, and search functionality.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "admin"  # Replace with your username
PASSWORD = "admin123"  # Replace with your password

class BankAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.headers = {}
        self.created_bank_id = None

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

    def test_create_bank(self):
        """Test creating a new bank"""
        print("\n🏦 Testing Bank Creation...")
        
        bank_data = {
            "bank_name": "State Bank of India",
            "branch_name": "Main Branch",
            "account_name": "PawnPro Company Ltd",
            "status": "active"
        }
        
        response = requests.post(f"{self.base_url}/banks/", 
                               json=bank_data, 
                               headers=self.headers)
        
        if response.status_code == 200:
            bank = response.json()
            self.created_bank_id = bank["id"]
            print(f"✅ Bank created successfully with ID: {self.created_bank_id}")
            print(f"   Bank Name: {bank['bank_name']}")
            print(f"   Branch: {bank['branch_name']}")
            print(f"   Account Name: {bank['account_name']}")
            print(f"   Status: {bank['status']}")
            return True
        else:
            print(f"❌ Bank creation failed: {response.status_code} - {response.text}")
            return False

    def test_get_all_banks(self):
        """Test getting all banks"""
        print("\n📋 Testing Get All Banks...")
        
        response = requests.get(f"{self.base_url}/banks/", headers=self.headers)
        
        if response.status_code == 200:
            banks = response.json()
            print(f"✅ Retrieved {len(banks)} bank(s)")
            for bank in banks:
                print(f"   - {bank['bank_name']} ({bank['branch_name']}) - Status: {bank['status']}")
            return True
        else:
            print(f"❌ Get banks failed: {response.status_code} - {response.text}")
            return False

    def test_get_bank_by_id(self):
        """Test getting a specific bank by ID"""
        if not self.created_bank_id:
            print("⚠️ Skipping get bank by ID test - no bank created")
            return False
            
        print(f"\n🔍 Testing Get Bank by ID ({self.created_bank_id})...")
        
        response = requests.get(f"{self.base_url}/banks/{self.created_bank_id}", 
                              headers=self.headers)
        
        if response.status_code == 200:
            bank = response.json()
            print(f"✅ Bank retrieved successfully")
            print(f"   Bank: {bank['bank_name']} - {bank['branch_name']}")
            print(f"   Account Name: {bank['account_name']}")
            print(f"   Status: {bank['status']}")
            return True
        else:
            print(f"❌ Get bank by ID failed: {response.status_code} - {response.text}")
            return False

    def test_update_bank(self):
        """Test updating a bank"""
        if not self.created_bank_id:
            print("⚠️ Skipping update bank test - no bank created")
            return False
            
        print(f"\n✏️ Testing Bank Update ({self.created_bank_id})...")
        
        update_data = {
            "account_name": "PawnPro Solutions Ltd",
            "status": "active"
        }
        
        response = requests.put(f"{self.base_url}/banks/{self.created_bank_id}",
                              json=update_data,
                              headers=self.headers)
        
        if response.status_code == 200:
            bank = response.json()
            print(f"✅ Bank updated successfully")
            print(f"   Updated Account Name: {bank['account_name']}")
            print(f"   Status: {bank['status']}")
            return True
        else:
            print(f"❌ Update bank failed: {response.status_code} - {response.text}")
            return False

    def test_search_banks(self):
        """Test searching banks"""
        print("\n🔎 Testing Bank Search...")
        
        # Test search by bank name
        response = requests.get(f"{self.base_url}/banks/?search=State Bank", 
                              headers=self.headers)
        
        if response.status_code == 200:
            banks = response.json()
            print(f"✅ Search by 'State Bank' found {len(banks)} result(s)")
            
            # Test search by status
            response = requests.get(f"{self.base_url}/banks/?status=active", 
                                  headers=self.headers)
            
            if response.status_code == 200:
                active_banks = response.json()
                print(f"✅ Active banks found: {len(active_banks)}")
                return True
            else:
                print(f"❌ Status filter failed: {response.status_code}")
                return False
        else:
            print(f"❌ Search failed: {response.status_code} - {response.text}")
            return False

    def test_deactivate_bank(self):
        """Test deactivating a bank (soft delete)"""
        if not self.created_bank_id:
            print("⚠️ Skipping deactivate bank test - no bank created")
            return False
            
        print(f"\n🚫 Testing Bank Deactivation ({self.created_bank_id})...")
        
        response = requests.delete(f"{self.base_url}/banks/{self.created_bank_id}",
                                 headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Bank deactivated: {result['message']}")
            return True
        else:
            print(f"❌ Deactivate bank failed: {response.status_code} - {response.text}")
            return False

    def test_activate_bank(self):
        """Test reactivating a bank"""
        if not self.created_bank_id:
            print("⚠️ Skipping activate bank test - no bank created")
            return False
            
        print(f"\n✅ Testing Bank Activation ({self.created_bank_id})...")
        
        response = requests.post(f"{self.base_url}/banks/{self.created_bank_id}/activate",
                               headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Bank activated: {result['message']}")
            return True
        else:
            print(f"❌ Activate bank failed: {response.status_code} - {response.text}")
            return False

    def test_duplicate_prevention(self):
        """Test duplicate bank prevention"""
        print("\n🛡️ Testing Duplicate Prevention...")
        
        # Try to create the same bank again
        duplicate_data = {
            "bank_name": "State Bank of India",
            "branch_name": "Main Branch",
            "account_name": "Different Account"
        }
        
        response = requests.post(f"{self.base_url}/banks/", 
                               json=duplicate_data, 
                               headers=self.headers)
        
        if response.status_code == 400:
            print("✅ Duplicate prevention working correctly")
            print(f"   Expected error: {response.json()['detail']}")
            return True
        else:
            print(f"❌ Duplicate prevention failed - should have returned 400 but got {response.status_code}")
            return False

    def run_all_tests(self):
        """Run all Bank API tests"""
        print("🚀 Starting Bank API Tests")
        print("=" * 50)
        
        if not self.authenticate():
            return
        
        tests = [
            self.test_create_bank,
            self.test_get_all_banks,
            self.test_get_bank_by_id,
            self.test_update_bank,
            self.test_search_banks,
            self.test_duplicate_prevention,
            self.test_deactivate_bank,
            self.test_activate_bank
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        print("\n" + "=" * 50)
        print(f"🎯 Test Summary: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All Bank API tests completed successfully!")
        else:
            print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    tester = BankAPITester()
    tester.run_all_tests()
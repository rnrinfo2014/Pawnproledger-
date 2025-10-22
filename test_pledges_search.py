#!/usr/bin/env python3
"""
Test script for pledges search functionality
Tests the new search parameter in /pledges/ endpoint
"""

import requests
import json

def test_pledges_search():
    """Test the pledges search functionality"""
    
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
        
        # Test 1: Get all pledges without search
        print("\n📋 Test 1: Get all pledges (no search)")
        response = requests.get(f"{base_url}/pledges/", headers=headers)
        if response.status_code == 200:
            pledges = response.json()
            print(f"✅ Found {len(pledges)} total pledges")
        else:
            print(f"❌ Failed to get pledges: {response.text}")
            return
            
        # Test 2: Search by pledge number
        print("\n🔍 Test 2: Search by pledge number")
        response = requests.get(f"{base_url}/pledges/?search=PL", headers=headers)
        if response.status_code == 200:
            search_results = response.json()
            print(f"✅ Found {len(search_results)} pledges matching 'PL'")
            if search_results:
                print(f"   First result: {search_results[0]['pledge_no']}")
        else:
            print(f"❌ Search failed: {response.text}")
            
        # Test 3: Search by status
        print("\n📊 Test 3: Search by status")
        response = requests.get(f"{base_url}/pledges/?search=active", headers=headers)
        if response.status_code == 200:
            search_results = response.json()
            print(f"✅ Found {len(search_results)} active pledges")
        else:
            print(f"❌ Status search failed: {response.text}")
            
        # Test 4: Search with pagination
        print("\n📄 Test 4: Search with pagination")
        response = requests.get(f"{base_url}/pledges/?search=PL&limit=5", headers=headers)
        if response.status_code == 200:
            search_results = response.json()
            print(f"✅ Found {len(search_results)} pledges (limited to 5)")
        else:
            print(f"❌ Pagination search failed: {response.text}")
            
        print("\n🎉 All pledge search tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_pledges_search()
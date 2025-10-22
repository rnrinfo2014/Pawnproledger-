#!/usr/bin/env python3
"""
Simple pledge creation test to verify complete accounting system
"""

import requests
from datetime import date, timedelta

def test_pledge_creation():
    print("Testing Pledge Creation with Complete Accounting...")
    
    # Step 1: Login
    login_response = requests.post("http://localhost:8000/token", 
                                 data={"username": "admin", "password": "admin123"})
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Create pledge
    today = date.today()
    due_date = today + timedelta(days=365)
    
    pledge_data = {
        "customer_id": 1,
        "scheme_id": 1,
        "pledge_date": today.isoformat(),
        "due_date": due_date.isoformat(),
        "item_count": 1,
        "gross_weight": 21.0,
        "net_weight": 20.5,
        "ornament_type": "Gold Ring",
        "ornament_weight": 20.5,
        "ornament_purity": 22,
        "market_value": 75000.0,
        "pledge_amount": 50000.0,
        "document_charges": 500.0,
        "first_month_interest": 500.0,
        "total_loan_amount": 50000.0,
        "final_amount": 51000.0,
        "company_id": 1  # Use company 1 where you have the data
    }
    
    pledge_response = requests.post("http://localhost:8000/pledges/", 
                                  json=pledge_data, headers=headers)
    
    print(f"Pledge creation status: {pledge_response.status_code}")
    
    if pledge_response.status_code == 200:
        result = pledge_response.json()
        print("SUCCESS: Pledge created with complete accounting!")
        print(f"Pledge ID: {result.get('pledge_id')}")
        print(f"Pledge No: {result.get('pledge_no')}")
        print(f"Amount: Rs.{result.get('pledge_amount')}")
        print("COMPLETE ACCOUNTING SYSTEM IS WORKING!")
        return True
    else:
        print(f"Error: {pledge_response.text}")
        print("\nFull response details:")
        try:
            error_data = pledge_response.json()
            print(f"Error detail: {error_data}")
        except:
            print(f"Raw response: {pledge_response.text}")
        return False

if __name__ == "__main__":
    test_pledge_creation()
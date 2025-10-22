#!/usr/bin/env python3
"""
Simple API test with curl-like functionality
"""

import requests
from datetime import date

# Simple test
login_response = requests.post("http://localhost:8000/token", 
                              data={"username": "admin", "password": "admin123"})

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test daybook API
    today = date.today()
    api_response = requests.get(
        f"http://localhost:8000/api/v1/daybook/daily-summary?transaction_date={today}&company_id=1",
        headers=headers
    )
    
    if api_response.status_code == 200:
        data = api_response.json()
        print("✅ API Call Successful")
        print(f"Opening: ₹{data.get('opening_balance', 0):.2f}")
        print(f"Closing: ₹{data.get('closing_balance', 0):.2f}")
    else:
        print(f"❌ API Error: {api_response.text}")
else:
    print(f"❌ Login Error: {login_response.text}")
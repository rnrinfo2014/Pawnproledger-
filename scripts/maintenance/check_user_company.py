#!/usr/bin/env python3
"""
Check user and company details
"""

import requests

def check_user_details():
    """Check the current user's company"""
    
    # Login
    login_response = requests.post("http://localhost:8000/token", 
                                 data={"username": "admin", "password": "admin123"})
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        return
    
    token = login_response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Check user profile/info
    try:
        # Check what company the current user belongs to by trying to get users list
        users_response = requests.get("http://localhost:8000/users/", headers=headers)
        if users_response.status_code == 200:
            users = users_response.json()
            for user in users:
                if user.get('username') == 'admin':
                    print(f"Admin user details:")
                    print(f"  User ID: {user.get('id')}")
                    print(f"  Username: {user.get('username')}")
                    print(f"  Company ID: {user.get('company_id')}")
                    break
        
        # Check recent pledges to see what company they belong to
        pledges_response = requests.get("http://localhost:8000/pledges/", headers=headers)
        if pledges_response.status_code == 200:
            pledges = pledges_response.json()
            print(f"\nRecent pledges:")
            for pledge in pledges[-3:]:  # Last 3 pledges
                print(f"  Pledge {pledge.get('pledge_id')}: {pledge.get('pledge_no')} (Company: {pledge.get('company_id')})")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_user_details()
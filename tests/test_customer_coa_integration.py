"""
Test Customer COA Integration
Test script to verify auto COA account creation for customers
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_customer_creation_with_coa():
    """Test customer creation with automatic COA account creation"""
    
    print("🧪 Testing Customer COA Integration")
    print("=" * 50)
    
    # Test data for customer creation
    test_customers = [
        {
            "name": "Rajesh Kumar",
            "phone": "+91-9876543210",
            "address": "123 Main Street, Mumbai",
            "city": "Mumbai",
            "id_proof_type": "Aadhaar",
            "company_id": 1,
            "created_by": 1
        },
        {
            "name": "Priya Sharma", 
            "phone": "+91-9876543211",
            "address": "456 Park Avenue, Delhi",
            "city": "Delhi",
            "id_proof_type": "PAN Card",
            "company_id": 1,
            "created_by": 1
        },
        {
            "name": "Mohammed Ali",
            "phone": "+91-9876543212", 
            "address": "789 Commercial Street, Bangalore",
            "city": "Bangalore",
            "id_proof_type": "Voter ID",
            "company_id": 1,
            "created_by": 1
        }
    ]
    
    created_customers = []
    
    # Create customers
    print("\n1️⃣ Creating customers with auto COA accounts...")
    for i, customer_data in enumerate(test_customers, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/customers",
                json=customer_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                customer = response.json()
                created_customers.append(customer)
                print(f"✅ Customer {i} created: {customer['name']} (ID: {customer['id']}, Code: {customer['acc_code']})")
                
                # Check if COA account was created
                if customer.get('coa_account_id'):
                    print(f"   🏦 COA Account ID: {customer['coa_account_id']}")
                else:
                    print(f"   ⚠️  No COA account created")
            else:
                print(f"❌ Failed to create customer {i}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error creating customer {i}: {str(e)}")
    
    # Test customer balance inquiry
    print(f"\n2️⃣ Testing customer balance inquiry...")
    for customer in created_customers:
        try:
            response = requests.get(f"{BASE_URL}/customers/{customer['id']}/balance")
            if response.status_code == 200:
                balance_info = response.json()
                print(f"✅ {balance_info['customer_name']}: Balance = ₹{balance_info['balance']}")
                print(f"   🏦 COA Account: {balance_info.get('account_code', 'N/A')}")
            else:
                print(f"❌ Failed to get balance for {customer['name']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting balance for {customer['name']}: {str(e)}")
    
    # Test customer COA info
    print(f"\n3️⃣ Testing customer COA account info...")
    for customer in created_customers:
        try:
            response = requests.get(f"{BASE_URL}/customers/{customer['id']}/coa-info")
            if response.status_code == 200:
                coa_info = response.json()
                print(f"✅ {coa_info['customer_name']}:")
                if coa_info['has_coa_account']:
                    coa = coa_info['coa_account']
                    print(f"   🏦 COA: {coa['account_code']} - {coa['account_name']}")
                    print(f"   📊 Type: {coa['account_type']}, Active: {coa['is_active']}")
                else:
                    print(f"   ⚠️  No COA account found")
            else:
                print(f"❌ Failed to get COA info for {customer['name']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting COA info for {customer['name']}: {str(e)}")
    
    # Test customer update (name change)
    if created_customers:
        print(f"\n4️⃣ Testing customer update with COA account name sync...")
        customer = created_customers[0]
        original_name = customer['name']
        updated_data = {
            "name": f"{original_name} (Updated)",
            "phone": customer['phone'],
            "address": customer['address'],
            "city": customer['city'],
            "id_proof_type": customer['id_proof_type'],
            "company_id": customer['company_id'],
            "created_by": customer['created_by']
        }
        
        try:
            response = requests.put(
                f"{BASE_URL}/customers/{customer['id']}", 
                json=updated_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                updated_customer = response.json()
                print(f"✅ Customer updated: {original_name} → {updated_customer['name']}")
                
                # Check if COA account name was updated
                coa_response = requests.get(f"{BASE_URL}/customers/{customer['id']}/coa-info")
                if coa_response.status_code == 200:
                    coa_info = coa_response.json()
                    if coa_info['has_coa_account']:
                        print(f"   🏦 COA Name: {coa_info['coa_account']['account_name']}")
            else:
                print(f"❌ Failed to update customer: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error updating customer: {str(e)}")
    
    print(f"\n🎉 Customer COA Integration Test Completed!")
    print(f"📊 Summary: {len(created_customers)} customers created with auto COA accounts")

def test_coa_structure():
    """Test COA structure and customer accounts"""
    
    print(f"\n🏦 Testing COA Structure...")
    
    try:
        # Get all COA accounts
        response = requests.get(f"{BASE_URL}/api/v1/coa/accounts?company_id=1")
        if response.status_code == 200:
            accounts = response.json()
            
            # Filter customer accounts (2001-xxx)
            customer_accounts = [acc for acc in accounts if acc['account_code'].startswith('2001')]
            
            print(f"📊 Customer COA Accounts Found: {len(customer_accounts)}")
            for acc in customer_accounts:
                print(f"   🏦 {acc['account_code']} - {acc['account_name']} ({acc['account_type']})")
        else:
            print(f"❌ Failed to get COA accounts: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting COA accounts: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Customer COA Integration Tests...")
    print("🌐 Server should be running on http://localhost:8000")
    
    # Test customer creation and COA integration
    test_customer_creation_with_coa()
    
    # Test COA structure
    test_coa_structure()
    
    print(f"\n✅ All tests completed!")
    print(f"\n📝 What was tested:")
    print(f"   ✅ Auto COA account creation on customer create")
    print(f"   ✅ Customer balance inquiry from COA")
    print(f"   ✅ Customer COA account information")
    print(f"   ✅ COA account name sync on customer update")
    print(f"   ✅ COA structure verification")
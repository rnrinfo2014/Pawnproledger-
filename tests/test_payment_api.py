"""
Simple payment test script
"""
import requests
import json
from datetime import date

def test_payment_accounting():
    # Test payment data
    payment_data = {
        "pledge_id": 22,
        "payment_date": date.today().isoformat(),
        "payment_type": "interest",
        "amount": 100.0,
        "interest_amount": 30.0,
        "principal_amount": 70.0,
        "payment_method": "cash",
        "remarks": "Test payment to verify accounting"
    }

    print("🧪 Testing Payment with Accounting")
    print("=" * 40)
    print(f"Payment data: {json.dumps(payment_data, indent=2)}")
    print()

    # Make the API call
    try:
        response = requests.post(
            "http://localhost:8000/pledge-payments/",
            json=payment_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Payment created successfully!")
            print(f"Payment ID: {result.get('payment_id')}")
            print(f"Receipt No: {result.get('receipt_no')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server first.")
        print("Run: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_payment_accounting()
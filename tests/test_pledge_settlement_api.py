"""
Test suite for Pledge Settlement API endpoint
Tests interest calculation logic, payment tracking, and settlement details

Run with: python test_pledge_settlement_api.py
"""

import requests
from datetime import date, datetime, timedelta
import json

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

class TestPledgeSettlementAPI:
    """Test suite for Pledge Settlement API"""
    
    def __init__(self):
        self.token = self.get_auth_token()
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
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
    
    def get_test_pledge_id(self):
        """Get a test pledge ID from existing pledges"""
        response = requests.get(f"{BASE_URL}/pledges/", headers=self.headers)
        if response.status_code == 200:
            pledges = response.json()
            if pledges:
                return pledges[0]["pledge_id"]
        return None
    
    def test_settlement_endpoint_success(self):
        """Test successful settlement calculation"""
        pledge_id = self.get_test_pledge_id()
        if not pledge_id:
            print("❌ No test pledges available. Skipping test.")
            return False
        
        print(f"🧪 Testing settlement for pledge ID: {pledge_id}")
        
        response = requests.get(
            f"{BASE_URL}/api/pledges/{pledge_id}/settlement",
            headers=self.headers
        )
        
        if response.status_code == 200:
            settlement = response.json()
            print("✅ Settlement endpoint successful!")
            
            # Validate response structure
            required_fields = [
                "pledge_id", "pledge_no", "customer_name", "pledge_date",
                "calculation_date", "status", "loan_amount", "scheme_interest_rate",
                "total_interest", "first_month_interest", "accrued_interest",
                "interest_calculation_details", "paid_interest", "paid_principal",
                "total_paid_amount", "final_amount", "remaining_interest", "remaining_principal"
            ]
            
            missing_fields = [field for field in required_fields if field not in settlement]
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            print("✅ All required fields present")
            
            # Validate calculation logic
            expected_final = settlement["remaining_interest"] + settlement["remaining_principal"]
            actual_final = settlement["final_amount"]
            
            if abs(expected_final - actual_final) < 0.01:  # Allow for floating point precision
                print("✅ Settlement calculation logic is correct")
            else:
                print(f"❌ Settlement calculation error: expected {expected_final}, got {actual_final}")
                return False
            
            # Display settlement details
            print("\n📊 Settlement Details:")
            print(f"   Pledge No: {settlement['pledge_no']}")
            print(f"   Customer: {settlement['customer_name']}")
            print(f"   Loan Amount: ${settlement['loan_amount']:,.2f}")
            print(f"   Total Interest: ${settlement['total_interest']:,.2f}")
            print(f"   First Month Interest: ${settlement['first_month_interest']:,.2f}")
            print(f"   Paid Interest: ${settlement['paid_interest']:,.2f}")
            print(f"   Paid Principal: ${settlement['paid_principal']:,.2f}")
            print(f"   Final Settlement: ${settlement['final_amount']:,.2f}")
            
            # Display interest calculation breakdown
            print("\n📈 Interest Calculation Details:")
            for detail in settlement["interest_calculation_details"]:
                print(f"   {detail['period']}: ${detail['interest_amount']:,.2f} "
                      f"({detail['days']} days, {detail['rate_percent']}%)")
            
            return True
        else:
            print(f"❌ Settlement endpoint failed: {response.status_code} - {response.text}")
            return False
    
    def test_settlement_endpoint_not_found(self):
        """Test settlement with invalid pledge ID"""
        print("🧪 Testing settlement with invalid pledge ID")
        
        response = requests.get(
            f"{BASE_URL}/api/pledges/99999/settlement",
            headers=self.headers
        )
        
        if response.status_code == 404:
            print("✅ Correctly returned 404 for invalid pledge ID")
            return True
        else:
            print(f"❌ Expected 404, got {response.status_code}")
            return False
    
    def test_settlement_without_auth(self):
        """Test settlement endpoint without authentication"""
        print("🧪 Testing settlement without authentication")
        
        pledge_id = self.get_test_pledge_id()
        if not pledge_id:
            print("❌ No test pledges available. Skipping test.")
            return False
        
        response = requests.get(f"{BASE_URL}/api/pledges/{pledge_id}/settlement")
        
        if response.status_code == 401:
            print("✅ Correctly requires authentication")
            return True
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            return False
    
    def test_interest_calculation_scenarios(self):
        """Test various interest calculation scenarios"""
        print("🧪 Testing interest calculation scenarios")
        
        # This would require creating test pledges with different dates
        # For now, we'll just validate that the endpoint handles edge cases
        
        pledge_id = self.get_test_pledge_id()
        if not pledge_id:
            print("❌ No test pledges available. Skipping test.")
            return False
        
        response = requests.get(
            f"{BASE_URL}/api/pledges/{pledge_id}/settlement",
            headers=self.headers
        )
        
        if response.status_code == 200:
            settlement = response.json()
            
            # Test that first month interest is always present
            first_month_found = False
            for detail in settlement["interest_calculation_details"]:
                if detail["is_mandatory"]:
                    first_month_found = True
                    if detail["interest_amount"] != settlement["first_month_interest"]:
                        print(f"❌ First month interest mismatch in details")
                        return False
            
            if not first_month_found:
                print("❌ First month mandatory interest not found in details")
                return False
            
            print("✅ Interest calculation scenarios validated")
            return True
        
        return False
    
    def run_all_tests(self):
        """Run all settlement API tests"""
        print("🚀 Starting Pledge Settlement API Tests")
        print("=" * 60)
        
        tests = [
            ("Settlement Endpoint Success", self.test_settlement_endpoint_success),
            ("Settlement Not Found", self.test_settlement_endpoint_not_found),
            ("Settlement Without Auth", self.test_settlement_without_auth),
            ("Interest Calculation Scenarios", self.test_interest_calculation_scenarios)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} ERROR: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print(f"⚠️  {total - passed} tests failed")
        
        return passed == total

def demo_settlement_calculation():
    """Demonstrate settlement calculation with detailed output"""
    print("🎯 Settlement Calculation Demo")
    print("=" * 60)
    
    try:
        tester = TestPledgeSettlementAPI()
        pledge_id = tester.get_test_pledge_id()
        
        if not pledge_id:
            print("❌ No test pledges available for demo")
            return
        
        response = requests.get(
            f"{BASE_URL}/api/pledges/{pledge_id}/settlement",
            headers=tester.headers
        )
        
        if response.status_code == 200:
            settlement = response.json()
            
            print(f"🏷️  Pledge Information:")
            print(f"   Pledge No: {settlement['pledge_no']}")
            print(f"   Customer: {settlement['customer_name']}")
            print(f"   Pledge Date: {settlement['pledge_date']}")
            print(f"   Calculation Date: {settlement['calculation_date']}")
            print(f"   Status: {settlement['status']}")
            print(f"   Monthly Interest Rate: {settlement['scheme_interest_rate']}%")
            
            print(f"\n💰 Financial Summary:")
            print(f"   Original Loan Amount: ${settlement['loan_amount']:,.2f}")
            print(f"   First Month Interest (Mandatory): ${settlement['first_month_interest']:,.2f}")
            print(f"   Additional Accrued Interest: ${settlement['accrued_interest']:,.2f}")
            print(f"   Total Interest Due: ${settlement['total_interest']:,.2f}")
            
            print(f"\n💳 Payment Summary:")
            print(f"   Interest Paid: ${settlement['paid_interest']:,.2f}")
            print(f"   Principal Paid: ${settlement['paid_principal']:,.2f}")
            print(f"   Total Paid: ${settlement['total_paid_amount']:,.2f}")
            
            print(f"\n🎯 Settlement Details:")
            print(f"   Remaining Interest: ${settlement['remaining_interest']:,.2f}")
            print(f"   Remaining Principal: ${settlement['remaining_principal']:,.2f}")
            print(f"   Final Settlement Amount: ${settlement['final_amount']:,.2f}")
            
            print(f"\n📈 Interest Calculation Breakdown:")
            for i, detail in enumerate(settlement["interest_calculation_details"], 1):
                status = "MANDATORY" if detail["is_mandatory"] else "CALCULATED"
                partial = " (PARTIAL)" if detail["is_partial"] else ""
                print(f"   {i}. {detail['period']}{partial}")
                print(f"      Period: {detail['from_date']} to {detail['to_date']} ({detail['days']} days)")
                print(f"      Rate: {detail['rate_percent']}% on ${detail['principal_amount']:,.2f}")
                print(f"      Interest: ${detail['interest_amount']:,.2f} [{status}]")
            
            print(f"\n✅ Settlement calculation completed successfully!")
            
        else:
            print(f"❌ Failed to get settlement: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")

if __name__ == "__main__":
    print("Pledge Settlement API Test Suite")
    print("Make sure the API server is running on http://localhost:8000")
    print("=" * 60)
    
    try:
        # Quick connectivity test
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ API server is not responding. Please start the server first.")
            exit(1)
        
        print("✅ API server is running")
        
        # Run demonstration
        demo_settlement_calculation()
        
        print("\n" + "=" * 60)
        
        # Run tests
        tester = TestPledgeSettlementAPI()
        success = tester.run_all_tests()
        
        exit(0 if success else 1)
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Please start the server first.")
        exit(1)
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        exit(1)
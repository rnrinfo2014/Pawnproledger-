"""
Test script for the corrected pledge settlement calculation logic.
This script tests various scenarios to ensure the interest calculation follows the corrected business rules.
"""

import requests
import json
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_TOKEN = "your_admin_token_here"  # Replace with actual admin token

headers = {
    "Authorization": f"Bearer {ADMIN_TOKEN}",
    "Content-Type": "application/json"
}

def test_settlement_calculation():
    """Test the corrected settlement calculation logic with various scenarios"""
    
    print("=" * 80)
    print("TESTING CORRECTED PLEDGE SETTLEMENT CALCULATION LOGIC")
    print("=" * 80)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Same Month - 10 days (should be half month)",
            "pledge_id": 1,
            "expected_logic": "Half month interest (≤15 days same month)"
        },
        {
            "name": "Same Month - 20 days (should be full month)", 
            "pledge_id": 2,
            "expected_logic": "Full month interest (>15 days same month)"
        },
        {
            "name": "Multi-month - 2 complete months",
            "pledge_id": 3, 
            "expected_logic": "First month mandatory + second month full"
        },
        {
            "name": "Multi-month with partial final month",
            "pledge_id": 4,
            "expected_logic": "First month mandatory + partial second month"
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n{'=' * 60}")
        print(f"TEST SCENARIO: {scenario['name']}")
        print(f"Expected Logic: {scenario['expected_logic']}")
        print(f"{'=' * 60}")
        
        try:
            # Make API call to get settlement details
            response = requests.get(
                f"{BASE_URL}/api/pledges/{scenario['pledge_id']}/settlement",
                headers=headers
            )
            
            if response.status_code == 200:
                settlement_data = response.json()
                print_settlement_analysis(settlement_data)
            elif response.status_code == 404:
                print(f"❌ Pledge ID {scenario['pledge_id']} not found")
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the server is running on localhost:8000")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n{'=' * 80}")
    print("TESTING COMPLETED")
    print("=" * 80)

def print_settlement_analysis(settlement_data):
    """Print detailed analysis of settlement calculation"""
    
    print(f"\n📋 PLEDGE DETAILS:")
    print(f"   Pledge ID: {settlement_data['pledge_id']}")
    print(f"   Pledge No: {settlement_data['pledge_no']}")
    print(f"   Customer: {settlement_data['customer_name']}")
    print(f"   Pledge Date: {settlement_data['pledge_date']}")
    print(f"   Calculation Date: {settlement_data['calculation_date']}")
    print(f"   Status: {settlement_data['status']}")
    
    print(f"\n💰 FINANCIAL SUMMARY:")
    print(f"   Loan Amount: ₹{settlement_data['loan_amount']:,.2f}")
    print(f"   Interest Rate: {settlement_data['scheme_interest_rate']:.2f}% per month")
    print(f"   Total Interest: ₹{settlement_data['total_interest']:,.2f}")
    print(f"   First Month Interest: ₹{settlement_data['first_month_interest']:,.2f}")
    print(f"   Accrued Interest: ₹{settlement_data['accrued_interest']:,.2f}")
    
    print(f"\n💳 PAYMENT DETAILS:")
    print(f"   Paid Interest: ₹{settlement_data['paid_interest']:,.2f}")
    print(f"   Paid Principal: ₹{settlement_data['paid_principal']:,.2f}")
    print(f"   Total Paid: ₹{settlement_data['total_paid_amount']:,.2f}")
    
    print(f"\n🧮 SETTLEMENT CALCULATION:")
    print(f"   Final Settlement Amount: ₹{settlement_data['final_amount']:,.2f}")
    print(f"   Remaining Interest: ₹{settlement_data['remaining_interest']:,.2f}")
    print(f"   Remaining Principal: ₹{settlement_data['remaining_principal']:,.2f}")
    
    print(f"\n📊 INTEREST CALCULATION BREAKDOWN:")
    for i, detail in enumerate(settlement_data['interest_calculation_details'], 1):
        print(f"   Period {i}: {detail['period']}")
        print(f"     └─ Date Range: {detail['from_date']} to {detail['to_date']}")
        print(f"     └─ Days: {detail['days']}")
        print(f"     └─ Rate: {detail['rate_percent']:.2f}%")
        print(f"     └─ Principal: ₹{detail['principal_amount']:,.2f}")
        print(f"     └─ Interest: ₹{detail['interest_amount']:,.2f}")
        print(f"     └─ Mandatory: {'Yes' if detail['is_mandatory'] else 'No'}")
        print(f"     └─ Partial: {'Yes' if detail['is_partial'] else 'No'}")
    
    # Analysis of calculation logic
    print(f"\n🔍 LOGIC ANALYSIS:")
    pledge_date = date.fromisoformat(settlement_data['pledge_date'])
    calc_date = date.fromisoformat(settlement_data['calculation_date'])
    
    same_month = (pledge_date.year == calc_date.year and pledge_date.month == calc_date.month)
    days_diff = (calc_date - pledge_date).days + 1
    
    if same_month:
        if days_diff <= 15:
            expected_logic = "Same calendar month, ≤15 days → Half month interest"
        else:
            expected_logic = "Same calendar month, >15 days → Full month (mandatory first month)"
    else:
        expected_logic = "Multiple calendar months → First month mandatory + subsequent months"
    
    print(f"   Expected Logic: {expected_logic}")
    print(f"   Days in Period: {days_diff}")
    print(f"   Same Calendar Month: {'Yes' if same_month else 'No'}")
    
    # Validation
    details = settlement_data['interest_calculation_details']
    if same_month and len(details) == 1:
        if days_diff <= 15 and details[0]['is_partial']:
            print("   ✅ CORRECT: Half month interest applied for ≤15 days")
        elif days_diff > 15 and details[0]['is_mandatory']:
            print("   ✅ CORRECT: Full month (mandatory) interest applied for >15 days")
        else:
            print("   ❌ INCORRECT: Logic doesn't match expected behavior")
    elif not same_month and len(details) >= 2:
        if details[0]['is_mandatory']:
            print("   ✅ CORRECT: First month marked as mandatory")
        else:
            print("   ❌ INCORRECT: First month should be mandatory")
    else:
        print("   ⚠️  REVIEW: Check calculation logic")

def create_test_pledge_data():
    """Create test pledge data for different scenarios"""
    
    print("\n📝 CREATING TEST PLEDGE DATA...")
    
    today = date.today()
    
    test_pledges = [
        {
            "name": "Same Month - 10 days",
            "pledge_date": today - timedelta(days=10),
            "loan_amount": 50000,
            "scheme_id": 1
        },
        {
            "name": "Same Month - 20 days", 
            "pledge_date": today - timedelta(days=20),
            "loan_amount": 75000,
            "scheme_id": 1
        },
        {
            "name": "Multi-month - 2 complete months",
            "pledge_date": today - relativedelta(months=2),
            "loan_amount": 100000,
            "scheme_id": 1
        },
        {
            "name": "Multi-month with partial final month",
            "pledge_date": today - relativedelta(months=1, days=15),
            "loan_amount": 120000,
            "scheme_id": 1
        }
    ]
    
    for pledge in test_pledges:
        print(f"   Test Pledge: {pledge['name']}")
        print(f"     └─ Pledge Date: {pledge['pledge_date']}")
        print(f"     └─ Loan Amount: ₹{pledge['loan_amount']:,}")
        print(f"     └─ Days from today: {(today - pledge['pledge_date']).days}")
        
        # Note: In a real scenario, you would create these pledges via API
        # For this test, we assume pledges with IDs 1-4 exist with these characteristics

if __name__ == "__main__":
    print("🔧 PLEDGE SETTLEMENT CALCULATION TEST SUITE")
    print("=" * 80)
    
    # Show test data structure
    create_test_pledge_data()
    
    # Run settlement calculation tests
    test_settlement_calculation()
    
    print("\n📋 MANUAL TESTING NOTES:")
    print("1. Ensure pledges with IDs 1-4 exist in your database")
    print("2. Update ADMIN_TOKEN with a valid authentication token")
    print("3. Verify server is running on localhost:8000")
    print("4. Check that the interest calculation logic matches expected business rules")
    print("\n🎯 KEY VALIDATION POINTS:")
    print("✓ Same month ≤15 days → Half month interest")
    print("✓ Same month >15 days → Full month (mandatory) interest") 
    print("✓ Multi-month → First month mandatory + subsequent months")
    print("✓ Partial final month → Proportional interest")
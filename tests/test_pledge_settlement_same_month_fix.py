"""
Test script for the CORRECTED pledge settlement calculation logic.
This script specifically tests the fix for settlement within the same first month.
"""

import requests
import json
from datetime import date, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_TOKEN = "your_admin_token_here"  # Replace with actual admin token

headers = {
    "Authorization": f"Bearer {ADMIN_TOKEN}",
    "Content-Type": "application/json"
}

def test_same_month_settlement_fix():
    """Test the CORRECTED settlement calculation for same month scenarios"""
    
    print("=" * 80)
    print("TESTING CORRECTED SAME MONTH SETTLEMENT CALCULATION")
    print("=" * 80)
    
    # Test the specific scenario that was broken
    test_scenario = {
        "name": "Same Month Settlement (CORRECTED)",
        "pledge_id": 1,  # Replace with actual pledge ID that has same month settlement
        "description": "Settlement within first month should only use mandatory first_month_interest, NO additional interest"
    }
    
    print(f"\n{'=' * 60}")
    print(f"TEST SCENARIO: {test_scenario['name']}")
    print(f"Description: {test_scenario['description']}")
    print(f"{'=' * 60}")
    
    try:
        # Make API call to get settlement details
        response = requests.get(
            f"{BASE_URL}/api/pledges/{test_scenario['pledge_id']}/settlement",
            headers=headers
        )
        
        if response.status_code == 200:
            settlement_data = response.json()
            analyze_corrected_settlement(settlement_data)
        elif response.status_code == 404:
            print(f"❌ Pledge ID {test_scenario['pledge_id']} not found")
            print("💡 Create a test pledge or update the pledge_id in this script")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on localhost:8000")
        print("💡 Start the server with: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print(f"\n{'=' * 80}")
    print("CORRECTED LOGIC TESTING COMPLETED")
    print("=" * 80)

def analyze_corrected_settlement(settlement_data):
    """Analyze if the corrected settlement calculation is working properly"""
    
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
    
    # CORRECTED LOGIC VALIDATION
    print(f"\n🔍 CORRECTED LOGIC VALIDATION:")
    pledge_date = date.fromisoformat(settlement_data['pledge_date'])
    calc_date = date.fromisoformat(settlement_data['calculation_date'])
    
    same_month = (pledge_date.year == calc_date.year and pledge_date.month == calc_date.month)
    days_diff = (calc_date - pledge_date).days + 1
    
    print(f"   Same Calendar Month: {'Yes' if same_month else 'No'}")
    print(f"   Days in Period: {days_diff}")
    
    if same_month:
        print(f"   Expected Behavior: Same month settlement")
        print(f"   Expected Logic: Only use mandatory first_month_interest, NO additional interest")
        
        # Validation checks
        first_month_interest = settlement_data['first_month_interest']
        total_interest = settlement_data['total_interest']
        accrued_interest = settlement_data['accrued_interest']
        final_amount = settlement_data['final_amount']
        loan_amount = settlement_data['loan_amount']
        
        print(f"\n✅ VALIDATION RESULTS:")
        
        # Check 1: Total interest should equal first month interest only
        if abs(total_interest - first_month_interest) < 0.01:
            print(f"   ✅ CORRECT: total_interest ({total_interest}) = first_month_interest ({first_month_interest})")
        else:
            print(f"   ❌ INCORRECT: total_interest ({total_interest}) ≠ first_month_interest ({first_month_interest})")
        
        # Check 2: Accrued interest should be 0
        if abs(accrued_interest) < 0.01:
            print(f"   ✅ CORRECT: accrued_interest ({accrued_interest}) = 0 (no additional interest)")
        else:
            print(f"   ❌ INCORRECT: accrued_interest ({accrued_interest}) should be 0")
        
        # Check 3: Final amount should be loan amount (since interest already collected)
        if abs(final_amount - loan_amount) < 0.01:
            print(f"   ✅ CORRECT: final_amount ({final_amount}) = loan_amount ({loan_amount})")
        else:
            print(f"   ⚠️  REVIEW: final_amount ({final_amount}) vs loan_amount ({loan_amount})")
            print(f"      This might be correct if payments were made")
        
        # Check 4: Only one interest calculation period
        details = settlement_data['interest_calculation_details']
        if len(details) == 1:
            print(f"   ✅ CORRECT: Only one interest period (no additional partial interest)")
            period = details[0]
            if period['is_mandatory'] and not period['is_partial']:
                print(f"   ✅ CORRECT: Period marked as mandatory, not partial")
            else:
                print(f"   ❌ INCORRECT: Period should be mandatory=True, partial=False")
        else:
            print(f"   ❌ INCORRECT: Found {len(details)} periods, should be 1 for same month")
        
        print(f"\n🎯 SUMMARY:")
        if (abs(total_interest - first_month_interest) < 0.01 and 
            abs(accrued_interest) < 0.01 and 
            len(details) == 1):
            print("   🎉 SETTLEMENT CALCULATION IS CORRECTLY FIXED!")
            print("   ✅ No additional interest added for same month settlement")
        else:
            print("   ⚠️  SETTLEMENT CALCULATION NEEDS FURTHER REVIEW")
    else:
        print(f"   Expected Behavior: Multi-month calculation (first month mandatory + additional months)")
        print(f"   ✅ This is a multi-month scenario - different validation logic applies")

def create_test_pledge_info():
    """Show information about creating test pledges for this scenario"""
    
    print("\n📝 TEST PLEDGE CREATION GUIDE:")
    print("=" * 60)
    print("To test the corrected same month settlement logic:")
    print("1. Create a pledge with today's date")
    print("2. Set first_month_interest to a fixed amount (e.g., 2500)")
    print("3. Immediately test settlement (same day/month)")
    print("4. Verify that only first_month_interest is used")
    print()
    print("Example test pledge data:")
    print("{")
    print('  "customer_id": 1,')
    print('  "scheme_id": 1,')
    print(f'  "pledge_date": "{date.today()}",')
    print(f'  "due_date": "{date.today() + timedelta(days=30)}",')
    print('  "total_loan_amount": 100000,')
    print('  "first_month_interest": 2500,')
    print('  "final_amount": 102500')
    print("}")
    print()
    print("Expected settlement result for same month:")
    print("- total_interest = 2500 (first_month_interest)")
    print("- accrued_interest = 0")
    print("- final_amount = 100000 (loan_amount)")

if __name__ == "__main__":
    print("🔧 CORRECTED PLEDGE SETTLEMENT CALCULATION TEST")
    print("=" * 80)
    print("Testing the fix for same month settlement calculation")
    
    # Show test data information
    create_test_pledge_info()
    
    # Run corrected settlement calculation test
    test_same_month_settlement_fix()
    
    print("\n📋 TESTING NOTES:")
    print("1. Update ADMIN_TOKEN with a valid authentication token")
    print("2. Update pledge_id with an actual pledge that has same month settlement")
    print("3. Verify server is running on localhost:8000")
    print("4. The corrected logic should show NO additional interest for same month settlement")
    print("\n🎯 KEY FIX VALIDATION:")
    print("✅ Same month settlement → Only first_month_interest (mandatory)")
    print("✅ No additional half/partial month interest")  
    print("✅ accrued_interest = 0")
    print("✅ total_interest = first_month_interest")
"""
Test script for the corrected pawn shop settlement calculation logic.
This validates the business rules implementation.
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

def test_settlement_business_rules():
    """Test the settlement calculation against pawn shop business rules"""
    
    print("=" * 80)
    print("PAWN SHOP SETTLEMENT CALCULATION - BUSINESS RULES VALIDATION")
    print("=" * 80)
    
    # Test scenarios based on business rules
    test_scenarios = [
        {
            "name": "Same Month Settlement (< 1 month)",
            "description": "Pledge: Sep 15, Settlement: Sep 16 → Should be loan amount only",
            "pledge_id": 1,
            "expected_logic": "Settlement = 90,000 (no additional interest)"
        },
        {
            "name": "1 Month Completed",
            "description": "Pledge: Sep 15, Settlement: Oct 16 → Loan + 1 month interest",
            "pledge_id": 2,
            "expected_logic": "Settlement = 90,000 + 1,800 = 91,800"
        },
        {
            "name": "2 Months Completed", 
            "description": "Pledge: Sep 15, Settlement: Nov 16 → Loan + 2 months interest",
            "pledge_id": 3,
            "expected_logic": "Settlement = 90,000 + 3,600 = 93,600"
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n{'=' * 60}")
        print(f"TEST: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"Expected: {scenario['expected_logic']}")
        print(f"{'=' * 60}")
        
        try:
            # Make API call to get settlement details
            response = requests.get(
                f"{BASE_URL}/api/pledges/{scenario['pledge_id']}/settlement",
                headers=headers
            )
            
            if response.status_code == 200:
                settlement_data = response.json()
                validate_business_rules(settlement_data, scenario)
            elif response.status_code == 404:
                print(f"❌ Pledge ID {scenario['pledge_id']} not found")
                print("💡 Create test pledges or update pledge IDs in this script")
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the server is running on localhost:8000")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n{'=' * 80}")
    print("BUSINESS RULES VALIDATION COMPLETED")
    print("=" * 80)

def validate_business_rules(settlement_data, scenario):
    """Validate settlement calculation against business rules"""
    
    print(f"\n📋 SETTLEMENT DETAILS:")
    print(f"   Pledge ID: {settlement_data['pledge_id']}")
    print(f"   Pledge No: {settlement_data['pledge_no']}")
    print(f"   Customer: {settlement_data['customer_name']}")
    print(f"   Pledge Date: {settlement_data['pledge_date']}")
    print(f"   Calculation Date: {settlement_data['calculation_date']}")
    
    print(f"\n💰 FINANCIAL SUMMARY:")
    print(f"   Loan Amount: ₹{settlement_data['loan_amount']:,.2f}")
    print(f"   Monthly Interest Rate: {settlement_data['scheme_interest_rate']:.2f}%")
    print(f"   First Month Interest (Paid): ₹{settlement_data['first_month_interest']:,.2f}")
    print(f"   Pending Interest: ₹{settlement_data['remaining_interest']:,.2f}")
    print(f"   Settlement Amount: ₹{settlement_data['final_amount']:,.2f}")
    
    # Calculate months difference
    pledge_date = date.fromisoformat(settlement_data['pledge_date'])
    calc_date = date.fromisoformat(settlement_data['calculation_date'])
    
    months_diff = (calc_date.year - pledge_date.year) * 12 + (calc_date.month - pledge_date.month)
    if calc_date.day < pledge_date.day:
        months_diff -= 1
    
    days_diff = (calc_date - pledge_date).days
    
    print(f"\n📊 TIME ANALYSIS:")
    print(f"   Days Difference: {days_diff}")
    print(f"   Months Completed: {max(0, months_diff)}")
    
    print(f"\n🔍 BUSINESS RULES VALIDATION:")
    
    loan_amount = settlement_data['loan_amount']
    monthly_rate = settlement_data['scheme_interest_rate']
    monthly_interest = loan_amount * monthly_rate / 100
    first_month_interest = settlement_data['first_month_interest']
    pending_interest = settlement_data['remaining_interest']
    settlement_amount = settlement_data['final_amount']
    
    # Rule 1: First month interest should be already paid
    if abs(settlement_data['paid_interest'] - first_month_interest) < 0.01:
        print(f"   ✅ RULE 1 PASSED: First month interest (₹{first_month_interest:,.2f}) is marked as paid")
    else:
        print(f"   ❌ RULE 1 FAILED: First month interest should be marked as paid")
    
    # Rule 2: Same month settlement (< 1 month)
    if months_diff <= 0:
        expected_settlement = loan_amount  # No additional interest
        if abs(pending_interest) < 0.01:
            print(f"   ✅ RULE 2 PASSED: Same month settlement - no additional interest")
        else:
            print(f"   ❌ RULE 2 FAILED: Same month should have no additional interest, got ₹{pending_interest:,.2f}")
        
        if abs(settlement_amount - expected_settlement) < 0.01:
            print(f"   ✅ SETTLEMENT PASSED: Amount = ₹{settlement_amount:,.2f} (loan amount only)")
        else:
            print(f"   ❌ SETTLEMENT FAILED: Expected ₹{expected_settlement:,.2f}, got ₹{settlement_amount:,.2f}")
    
    # Rule 3: Multiple months completed
    elif months_diff > 0:
        expected_additional_interest = months_diff * monthly_interest
        expected_settlement = loan_amount + expected_additional_interest
        
        if abs(pending_interest - expected_additional_interest) < 0.01:
            print(f"   ✅ RULE 3 PASSED: {months_diff} months × ₹{monthly_interest:,.2f} = ₹{expected_additional_interest:,.2f}")
        else:
            print(f"   ❌ RULE 3 FAILED: Expected ₹{expected_additional_interest:,.2f}, got ₹{pending_interest:,.2f}")
        
        if abs(settlement_amount - expected_settlement) < 0.01:
            print(f"   ✅ SETTLEMENT PASSED: Amount = ₹{settlement_amount:,.2f}")
        else:
            print(f"   ❌ SETTLEMENT FAILED: Expected ₹{expected_settlement:,.2f}, got ₹{settlement_amount:,.2f}")
    
    # Calculation details validation
    print(f"\n📋 CALCULATION BREAKDOWN:")
    for i, detail in enumerate(settlement_data['interest_calculation_details'], 1):
        print(f"   Period {i}: {detail['period']}")
        print(f"     └─ Interest: ₹{detail['interest_amount']:,.2f}")
        print(f"     └─ Mandatory: {'Yes' if detail['is_mandatory'] else 'No'}")
    
    # Overall validation
    if months_diff <= 0:
        rule_passed = (abs(pending_interest) < 0.01 and 
                      abs(settlement_amount - loan_amount) < 0.01)
    else:
        expected_total = loan_amount + (months_diff * monthly_interest)
        rule_passed = abs(settlement_amount - expected_total) < 0.01
    
    if rule_passed:
        print(f"\n🎉 OVERALL RESULT: ✅ BUSINESS RULES CORRECTLY IMPLEMENTED")
    else:
        print(f"\n⚠️  OVERALL RESULT: ❌ BUSINESS RULES NEED CORRECTION")

def show_business_rules():
    """Display the business rules for reference"""
    
    print("\n📋 PAWN SHOP BUSINESS RULES:")
    print("=" * 60)
    print("1. First month interest is collected upfront (already paid)")
    print("2. Same month settlement (< 1 month): Settlement = Loan amount only")
    print("3. Multiple months: Settlement = Loan + (completed_months × monthly_interest)")
    print()
    print("Examples:")
    print("- Pledge: Sep 15, Settlement: Sep 16 → ₹90,000")
    print("- Pledge: Sep 15, Settlement: Oct 16 → ₹90,000 + ₹1,800 = ₹91,800")
    print("- Pledge: Sep 15, Settlement: Nov 16 → ₹90,000 + ₹3,600 = ₹93,600")
    print()
    print("Key Points:")
    print("- First month interest (₹1,800) is always collected at pledge creation")
    print("- Additional interest only applies for completed months beyond first month")
    print("- No partial month calculations - only full completed months count")

if __name__ == "__main__":
    print("🔧 PAWN SHOP SETTLEMENT VALIDATION SUITE")
    
    # Show business rules
    show_business_rules()
    
    # Run validation tests
    test_settlement_business_rules()
    
    print("\n📋 SETUP NOTES:")
    print("1. Update ADMIN_TOKEN with valid authentication token")
    print("2. Create test pledges with appropriate dates:")
    print("   - Pledge 1: Recent date (same month)")
    print("   - Pledge 2: 1 month old")
    print("   - Pledge 3: 2 months old")
    print("3. Ensure server is running on localhost:8000")
    print("4. Verify loan amounts and interest rates match examples")
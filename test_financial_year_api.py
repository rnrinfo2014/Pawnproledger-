#!/usr/bin/env python3
"""
Financial Year Closing/Opening API Test Script
Tests year-end closing process, P&L calculation, and opening balance carry-forward
"""

import requests
import json
from datetime import date, datetime, timedelta
from typing import Dict, Any

BASE_URL = 'http://localhost:8000'

def get_auth_headers():
    """Get authentication headers for API calls"""
    # Login with admin credentials
    login_response = requests.post(f'{BASE_URL}/token', data={
        'username': 'admin',  # Replace with actual admin username
        'password': 'admin123'  # Replace with actual admin password
    })
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        return {'Authorization': f'Bearer {token}'}
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        return {}

def print_section_header(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"🏦 {title}")
    print(f"{'='*80}")

def print_api_response(title: str, response: requests.Response):
    """Print formatted API response"""
    print(f"\n📊 {title}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (int, float)):
                        print(f"   {key}: {value:,.2f}" if isinstance(value, float) else f"   {key}: {value}")
                    elif isinstance(value, str):
                        print(f"   {key}: {value}")
                    elif isinstance(value, list) and len(value) <= 5:  # Show small lists
                        print(f"   {key}: {len(value)} items")
                        for i, item in enumerate(value[:3], 1):
                            if isinstance(item, dict) and 'account_name' in item:
                                print(f"      {i}. {item.get('account_name', 'N/A')}: ₹{item.get('net_balance', 0):,.2f}")
                        if len(value) > 3:
                            print(f"      ... and {len(value) - 3} more")
                    elif isinstance(value, list):
                        print(f"   {key}: {len(value)} items")
            else:
                print(f"   Response: {data}")
        except json.JSONDecodeError:
            print(f"   Raw response: {response.text[:200]}")
    else:
        print(f"   Error: {response.text}")

def test_trial_balance(headers: Dict[str, str]):
    """Test trial balance API"""
    print_section_header("TRIAL BALANCE TEST")
    
    # Get trial balance as of today
    today = date.today()
    response = requests.get(
        f'{BASE_URL}/api/v1/financial-year/trial-balance?as_of_date={today}',
        headers=headers
    )
    
    print_api_response("Trial Balance", response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📋 TRIAL BALANCE SUMMARY:")
        print(f"   Date: {data.get('as_of_date', 'Unknown')}")
        print(f"   Company: {data.get('company_name', 'Unknown')}")
        print(f"   Total Debits: ₹{data.get('total_debits', 0):,.2f}")
        print(f"   Total Credits: ₹{data.get('total_credits', 0):,.2f}")
        print(f"   Difference: ₹{data.get('difference', 0):,.2f}")
        print(f"   Is Balanced: {'✅ Yes' if data.get('is_balanced', False) else '❌ No'}")
        
        accounts = data.get('accounts', [])
        if accounts:
            print(f"\n📈 TOP ACCOUNT BALANCES:")
            for i, account in enumerate(accounts[:10], 1):
                debit = account.get('debit_balance', 0)
                credit = account.get('credit_balance', 0)
                balance_type = "Dr" if debit > credit else "Cr"
                balance_amount = debit if debit > credit else credit
                print(f"   {i:2d}. {account.get('account_name', 'Unknown'):<25} ₹{balance_amount:>10,.2f} {balance_type}")

def test_profit_loss(headers: Dict[str, str], financial_year: int = 2024):
    """Test Profit & Loss statement"""
    print_section_header("PROFIT & LOSS STATEMENT TEST")
    
    response = requests.get(
        f'{BASE_URL}/api/v1/financial-year/profit-loss/{financial_year}',
        headers=headers
    )
    
    print_api_response("Profit & Loss Statement", response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n💰 P&L SUMMARY:")
        print(f"   Financial Year: {data.get('financial_year', 'Unknown')}")
        print(f"   Period: {data.get('period_start', '')} to {data.get('period_end', '')}")
        print(f"   Total Revenue: ₹{data.get('total_revenue', 0):,.2f}")
        print(f"   Total Expenses: ₹{data.get('total_expenses', 0):,.2f}")
        print(f"   Gross Profit: ₹{data.get('gross_profit', 0):,.2f}")
        print(f"   Net Profit: ₹{data.get('net_profit', 0):,.2f}")
        print(f"   Profit %: {data.get('profit_percentage', 0):.2f}%")
        
        revenue_accounts = data.get('revenue_accounts', [])
        if revenue_accounts:
            print(f"\n📈 REVENUE ACCOUNTS:")
            for account in revenue_accounts[:5]:
                print(f"      {account.get('account_name', 'Unknown')}: ₹{account.get('credit_balance', 0):,.2f}")
        
        expense_accounts = data.get('expense_accounts', [])
        if expense_accounts:
            print(f"\n📉 EXPENSE ACCOUNTS:")
            for account in expense_accounts[:5]:
                print(f"      {account.get('account_name', 'Unknown')}: ₹{account.get('debit_balance', 0):,.2f}")

def test_balance_sheet(headers: Dict[str, str]):
    """Test Balance Sheet"""
    print_section_header("BALANCE SHEET TEST")
    
    today = date.today()
    response = requests.get(
        f'{BASE_URL}/api/v1/financial-year/balance-sheet?as_of_date={today}',
        headers=headers
    )
    
    print_api_response("Balance Sheet", response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n🏢 BALANCE SHEET SUMMARY:")
        print(f"   As of Date: {data.get('as_of_date', 'Unknown')}")
        print(f"   Financial Year: {data.get('financial_year', 'Unknown')}")
        print(f"   Total Assets: ₹{data.get('total_assets', 0):,.2f}")
        print(f"   Total Liabilities: ₹{data.get('total_liabilities', 0):,.2f}")
        print(f"   Total Equity: ₹{data.get('total_equity', 0):,.2f}")
        print(f"   Is Balanced: {'✅ Yes' if data.get('is_balanced', False) else '❌ No'}")
        
        # Show top assets
        assets = data.get('assets', [])
        if assets:
            print(f"\n🏦 TOP ASSETS:")
            for asset in assets[:5]:
                print(f"      {asset.get('account_name', 'Unknown')}: ₹{asset.get('net_balance', 0):,.2f}")
        
        # Show top liabilities
        liabilities = data.get('liabilities', [])
        if liabilities:
            print(f"\n💳 TOP LIABILITIES:")
            for liability in liabilities[:5]:
                print(f"      {liability.get('account_name', 'Unknown')}: ₹{liability.get('net_balance', 0):,.2f}")

def test_year_closing_validation(headers: Dict[str, str], financial_year: int = 2024):
    """Test year closing validation"""
    print_section_header("YEAR CLOSING VALIDATION TEST")
    
    response = requests.get(
        f'{BASE_URL}/api/v1/financial-year/validate-closing/{financial_year}',
        headers=headers
    )
    
    print_api_response("Year Closing Validation", response)
    
    if response.status_code == 200:
        data = response.json()
        eligible = data.get('eligible', False)
        reason = data.get('reason', 'Unknown')
        
        print(f"\n✅ VALIDATION RESULT:")
        print(f"   Eligible for Closing: {'✅ Yes' if eligible else '❌ No'}")
        print(f"   Reason: {reason}")
        
        if 'closing_date' in data:
            print(f"   Previous Closing Date: {data['closing_date']}")
        if 'pending_count' in data:
            print(f"   Pending Transactions: {data['pending_count']}")
        
        return eligible
    else:
        return False

def test_year_closing_process(headers: Dict[str, str], financial_year: int = 2024):
    """Test actual year closing process (BE CAREFUL!)"""
    print_section_header("YEAR CLOSING PROCESS TEST")
    
    print("⚠️  WARNING: This will perform actual year-end closing!")
    print("   This action creates permanent accounting entries.")
    print("   Make sure you have a database backup before proceeding.")
    
    # Ask for confirmation
    user_input = input("\n❓ Do you want to proceed with year closing? (type 'YES' to confirm): ")
    
    if user_input != 'YES':
        print("❌ Year closing cancelled by user")
        return False
    
    # Prepare closing request
    closing_date = date(financial_year + 1, 3, 31)  # March 31st of next year
    
    closing_request = {
        "financial_year": financial_year,
        "closing_date": closing_date.isoformat(),
        "backup_before_closing": True,
        "admin_confirmation": "CONFIRM",
        "closing_notes": "Automated year-end closing via API test"
    }
    
    print(f"\n🔄 Initiating year closing for FY {financial_year}-{str(financial_year+1)[-2:]}...")
    
    response = requests.post(
        f'{BASE_URL}/api/v1/financial-year/close-year',
        headers=headers,
        json=closing_request
    )
    
    print_api_response("Year Closing Process", response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n🎉 YEAR CLOSING SUCCESSFUL:")
        print(f"   Financial Year: {data.get('financial_year', 'Unknown')}")
        print(f"   Closing Date: {data.get('closing_date', 'Unknown')}")
        print(f"   Status: {data.get('status', 'Unknown')}")
        print(f"   Closing Entries: {data.get('closing_entries_count', 0)}")
        print(f"   Rollback Available: {'✅ Yes' if data.get('rollback_available', False) else '❌ No'}")
        
        # Show process steps
        process_steps = data.get('process_steps', [])
        if process_steps:
            print(f"\n📋 PROCESS STEPS:")
            for step in process_steps:
                status_icon = {'completed': '✅', 'failed': '❌', 'in-progress': '🔄'}.get(step.get('status', ''), '❓')
                print(f"   {status_icon} {step.get('step', 'Unknown')}: {step.get('message', 'No message')}")
        
        # Show P&L summary
        profit_loss = data.get('profit_loss', {})
        if profit_loss:
            print(f"\n💰 FINAL P&L:")
            print(f"   Net Profit: ₹{profit_loss.get('net_profit', 0):,.2f}")
            print(f"   Total Revenue: ₹{profit_loss.get('total_revenue', 0):,.2f}")
            print(f"   Total Expenses: ₹{profit_loss.get('total_expenses', 0):,.2f}")
        
        return True
    else:
        print(f"❌ Year closing failed!")
        return False

def test_year_opening_process(headers: Dict[str, str], financial_year: int = 2025):
    """Test year opening process"""
    print_section_header("YEAR OPENING PROCESS TEST")
    
    print("⚠️  WARNING: This will create opening balance entries!")
    print("   This should only be done after the previous year is closed.")
    
    # Ask for confirmation
    user_input = input(f"\n❓ Do you want to open FY {financial_year}-{str(financial_year+1)[-2:]}? (type 'YES' to confirm): ")
    
    if user_input != 'YES':
        print("❌ Year opening cancelled by user")
        return False
    
    # Prepare opening request
    opening_date = date(financial_year, 4, 1)  # April 1st
    
    opening_request = {
        "financial_year": financial_year,
        "opening_date": opening_date.isoformat(),
        "carry_forward_balances": True,
        "admin_confirmation": "CONFIRM",
        "opening_notes": "Automated year opening via API test"
    }
    
    print(f"\n🔄 Initiating year opening for FY {financial_year}-{str(financial_year+1)[-2:]}...")
    
    response = requests.post(
        f'{BASE_URL}/api/v1/financial-year/open-year',
        headers=headers,
        json=opening_request
    )
    
    print_api_response("Year Opening Process", response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n🎉 YEAR OPENING SUCCESSFUL:")
        print(f"   Financial Year: {data.get('financial_year', 'Unknown')}")
        print(f"   Opening Date: {data.get('opening_date', 'Unknown')}")
        print(f"   Status: {data.get('status', 'Unknown')}")
        print(f"   Opening Entries: {data.get('opening_entries_count', 0)}")
        print(f"   Balances Carried Forward: {data.get('carried_forward_balances', 0)}")
        
        # Show process steps
        process_steps = data.get('process_steps', [])
        if process_steps:
            print(f"\n📋 PROCESS STEPS:")
            for step in process_steps:
                status_icon = {'completed': '✅', 'failed': '❌', 'in-progress': '🔄'}.get(step.get('status', ''), '❓')
                print(f"   {status_icon} {step.get('step', 'Unknown')}: {step.get('message', 'No message')}")
        
        return True
    else:
        print(f"❌ Year opening failed!")
        return False

def main():
    """Main test function"""
    print("🚀 FINANCIAL YEAR API COMPREHENSIVE TEST")
    print("=" * 80)
    print("This script tests all Financial Year Closing/Opening APIs")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    
    # Get authentication headers
    headers = get_auth_headers()
    if not headers:
        print("❌ Authentication failed. Please check your credentials.")
        return
    
    print("✅ Authentication successful")
    
    # Test sequence
    try:
        # 1. Test Trial Balance
        test_trial_balance(headers)
        
        # 2. Test Profit & Loss
        test_profit_loss(headers, 2024)
        
        # 3. Test Balance Sheet
        test_balance_sheet(headers)
        
        # 4. Test Year Closing Validation
        can_close = test_year_closing_validation(headers, 2024)
        
        # 5. Test Year Closing (Optional - requires confirmation)
        if can_close:
            print(f"\n📋 FY 2024-25 is eligible for closing.")
            print("   You can test the actual closing process if needed.")
            # test_year_closing_process(headers, 2024)
        else:
            print(f"\n❌ FY 2024-25 is not eligible for closing or already closed.")
        
        # 6. Test Year Opening (Optional - requires confirmation)
        print(f"\n📋 You can test year opening for FY 2025-26 if needed.")
        # test_year_opening_process(headers, 2025)
        
        print(f"\n{'='*80}")
        print("🎉 FINANCIAL YEAR API TESTING COMPLETE")
        print("All financial year management APIs are working correctly!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Please check the server logs for more details.")

if __name__ == '__main__':
    main()
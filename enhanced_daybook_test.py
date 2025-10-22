#!/usr/bin/env python3
"""
Enhanced Daybook Report Test
Shows opening balance, closing balance, and daily activities in detail
"""
import requests
import json
from datetime import datetime, date

BASE_URL = 'http://localhost:8000'

def test_enhanced_daybook():
    # Login
    print("🔐 Authenticating...")
    login_data = {'username': 'admin', 'password': 'admin123'}
    response = requests.post(f'{BASE_URL}/token', data=login_data)
    
    if response.status_code != 200:
        print('❌ Authentication failed')
        return
        
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print('✅ Authentication successful')
    
    # Get user details
    user_response = requests.get(f'{BASE_URL}/users/me', headers=headers)
    user_data = user_response.json()
    company_id = user_data.get('company_id', 1)
    
    # Test with date that has transaction data
    test_date = '2025-10-15'  # Date with 39 vouchers and 45 entries
    
    print(f"\n📊 DAYBOOK REPORT FOR {test_date}")
    print("=" * 60)
    
    # Get daily summary with all details
    response = requests.get(
        f'{BASE_URL}/api/v1/daybook/daily-summary?transaction_date={test_date}&company_id={company_id}', 
        headers=headers
    )
    
    if response.status_code != 200:
        print(f'❌ Error: {response.status_code} - {response.text}')
        return
    
    data = response.json()
    summary = data.get('summary', {})
    entries = data.get('entries', [])
    opening_balance = data.get('opening_balance', 0)
    closing_balance = data.get('closing_balance', 0)
    
    # Display Summary Information
    print(f"📈 SUMMARY INFORMATION:")
    print(f"   Opening Balance: Rs.{opening_balance:,.2f}")
    print(f"   Closing Balance: Rs.{closing_balance:,.2f}")
    print(f"   Net Change: Rs.{closing_balance - opening_balance:,.2f}")
    print(f"   Total Vouchers: {summary.get('total_vouchers', 0)}")
    print(f"   Total Entries: {len(entries)}")
    print(f"   Total Debits: Rs.{summary.get('total_debit', 0):,.2f}")
    print(f"   Total Credits: Rs.{summary.get('total_credit', 0):,.2f}")
    print(f"   Balance Check: Rs.{summary.get('balance_difference', 0):,.2f}")
    
    # Display Voucher Type Breakdown
    voucher_types = summary.get('voucher_types', {})
    if voucher_types:
        print(f"\n📋 VOUCHER TYPE BREAKDOWN:")
        for voucher_type, count in voucher_types.items():
            print(f"   {voucher_type}: {count} vouchers")
    
    # Display Daily Activities (Transaction Details)
    print(f"\n💰 DAILY ACTIVITIES ({len(entries)} transactions):")
    print("-" * 60)
    print(f"{'Sr.':<3} {'Voucher':<8} {'Account':<20} {'Debit':<12} {'Credit':<12} {'Description':<20}")
    print("-" * 60)
    
    running_balance = opening_balance
    for i, entry in enumerate(entries[:20], 1):  # Show first 20 entries
        voucher_type = entry.get('voucher_type', 'Unknown')[:7]
        voucher_no = entry.get('voucher_no', 'N/A')[:7]
        account_name = entry.get('account_name', 'Unknown')[:18]
        account_code = entry.get('account_code', 'N/A')
        debit = entry.get('debit', 0)
        credit = entry.get('credit', 0)
        narration = entry.get('narration', '')[:18]
        
        # Update running balance
        running_balance += (debit - credit)
        
        print(f"{i:<3} {voucher_type:<8} {account_name:<20} {debit:>10,.0f} {credit:>10,.0f} {narration:<20}")
    
    if len(entries) > 20:
        print(f"... and {len(entries) - 20} more transactions")
    
    print("-" * 60)
    print(f"{'TOTALS':<32} {summary.get('total_debit', 0):>10,.0f} {summary.get('total_credit', 0):>10,.0f}")
    print("-" * 60)
    
    # Account-wise Summary
    print(f"\n🏦 ACCOUNT-WISE SUMMARY FOR {test_date}:")
    print("-" * 50)
    response = requests.get(
        f'{BASE_URL}/api/v1/daybook/account-wise-summary?transaction_date={test_date}&company_id={company_id}', 
        headers=headers
    )
    
    if response.status_code == 200:
        account_data = response.json()
        accounts = account_data.get('accounts', [])
        
        print(f"{'Account':<25} {'Debit':<12} {'Credit':<12} {'Net':<12}")
        print("-" * 50)
        
        for acc in accounts[:10]:  # Show first 10 accounts
            name = acc.get('account_name', 'Unknown')[:23]
            code = acc.get('account_code', '')
            debit = acc.get('total_debit', 0)
            credit = acc.get('total_credit', 0)
            balance = acc.get('balance', 0)
            
            account_display = f"{name} ({code})" if code else name
            print(f"{account_display[:25]:<25} {debit:>10,.0f} {credit:>10,.0f} {balance:>10,.0f}")
        
        if len(accounts) > 10:
            print(f"... and {len(accounts) - 10} more accounts")
    else:
        print("❌ Could not fetch account-wise summary")
    
    print("\n" + "=" * 60)
    print("📊 DAYBOOK REPORT COMPLETED")
    print("=" * 60)

if __name__ == '__main__':
    test_enhanced_daybook()
#!/usr/bin/env python3
import requests
import json
from datetime import datetime, date

BASE_URL = 'http://localhost:8000'

def test_daybook_reports():
    # Login first - using correct endpoint
    login_data = {'username': 'admin', 'password': 'admin123'}
    response = requests.post(f'{BASE_URL}/token', data=login_data)
    
    if response.status_code != 200:
        print('❌ Authentication failed')
        print(f'Status Code: {response.status_code}')
        print(f'Response: {response.text}')
        return
        
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print('✅ Authentication successful')
    
    print('\n🔍 Testing Daybook Reports...\n')
    
    # Get user details for company_id
    user_response = requests.get(f'{BASE_URL}/users/me', headers=headers)
    if user_response.status_code != 200:
        print('❌ Could not get user details')
        return
    
    user_data = user_response.json()
    company_id = user_data.get('company_id', 1)
    print(f'Using company_id: {company_id}')
    
    # 1. Daily Summary for today
    today = datetime.now().strftime('%Y-%m-%d')
    print(f'\n📊 Daily Summary for {today}:')
    response = requests.get(f'{BASE_URL}/api/v1/daybook/daily-summary?transaction_date={today}&company_id={company_id}', headers=headers)
    if response.status_code == 200:
        data = response.json()
        summary = data.get('summary', {})
        print(f'   Total Entries: {len(data.get("entries", []))}')
        print(f'   Total Debits: Rs.{summary.get("total_debit", 0)}')
        print(f'   Total Credits: Rs.{summary.get("total_credit", 0)}')
        print(f'   Balance Difference: Rs.{summary.get("balance_difference", 0)}')
    else:
        print(f'   ❌ Error: {response.status_code} - {response.text}')
    
    # 2. Current Month Summary
    print(f'\n📅 Current Month Summary:')
    response = requests.get(f'{BASE_URL}/api/v1/daybook/current-month-summary?company_id={company_id}', headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f'   Period: {data.get("period", "N/A")}')
        print(f'   Total Entries: {data.get("total_entries", 0)}')
        print(f'   Total Debits: Rs.{data.get("total_debits", 0)}')
        print(f'   Total Credits: Rs.{data.get("total_credits", 0)}')
        print(f'   Net Balance: Rs.{data.get("net_balance", 0)}')
    else:
        print(f'   ❌ Error: {response.status_code} - {response.text}')
    
    # 3. Account-wise Summary
    print(f'\n🏦 Account-wise Summary:')
    response = requests.get(f'{BASE_URL}/api/v1/daybook/account-wise-summary?transaction_date={today}&company_id={company_id}', headers=headers)
    if response.status_code == 200:
        data = response.json()
        accounts = data.get('accounts', [])
        print(f'   Total Accounts with transactions: {len(accounts)}')
        for i, acc in enumerate(accounts[:5]):  # Show first 5 accounts
            account_name = acc.get('account_name', 'Unknown')
            account_code = acc.get('account_code', 'N/A')
            total_debit = acc.get('total_debit', 0)
            total_credit = acc.get('total_credit', 0)
            balance = acc.get('balance', 0)
            print(f'   {i+1}. {account_name} ({account_code}): Dr.{total_debit} | Cr.{total_credit} | Bal.{balance}')
        if len(accounts) > 5:
            print(f'   ... and {len(accounts) - 5} more accounts')
    else:
        print(f'   ❌ Error: {response.status_code} - {response.text}')
    
    # 4. Recent Voucher-wise Summary
    print(f'\n📋 Voucher-wise Summary:')
    response = requests.get(f'{BASE_URL}/api/v1/daybook/voucher-wise-summary?transaction_date={today}&company_id={company_id}', headers=headers)
    if response.status_code == 200:
        data = response.json()
        vouchers = data.get('vouchers', [])
        print(f'   Total Vouchers: {len(vouchers)}')
        for i, voucher in enumerate(vouchers[:3]):  # Show first 3 vouchers
            voucher_type = voucher.get('voucher_type', 'Unknown')
            voucher_date = voucher.get('voucher_date', 'N/A')
            total_amount = voucher.get('total_amount', 0)
            entry_count = voucher.get('entry_count', 0)
            print(f'   {i+1}. {voucher_type} | Date: {voucher_date} | Amount: Rs.{total_amount} | Entries: {entry_count}')
        if len(vouchers) > 3:
            print(f'   ... and {len(vouchers) - 3} more vouchers')
    else:
        print(f'   ❌ Error: {response.status_code} - {response.text}')

    # 5. Date Range Summary (last 7 days)
    from datetime import timedelta
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    
    print(f'\n📆 Date Range Summary ({start_date} to {end_date}):')
    response = requests.get(f'{BASE_URL}/api/v1/daybook/date-range-summary?start_date={start_date}&end_date={end_date}&company_id={company_id}', headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f'   Period: {data.get("start_date", "N/A")} to {data.get("end_date", "N/A")}')
        print(f'   Total Entries: {data.get("total_entries", 0)}')
        print(f'   Total Debits: Rs.{data.get("total_debits", 0)}')
        print(f'   Total Credits: Rs.{data.get("total_credits", 0)}')
        print(f'   Net Balance: Rs.{data.get("net_balance", 0)}')
        
        # Show daily breakdown if available
        daily_data = data.get('daily_breakdown', [])
        if daily_data:
            print('   Daily Breakdown:')
            for day in daily_data[:3]:  # Show first 3 days
                day_date = day.get('date', 'N/A')
                day_debits = day.get('total_debits', 0)
                day_credits = day.get('total_credits', 0)
                print(f'     {day_date}: Dr.{day_debits} | Cr.{day_credits}')
    else:
        print(f'   ❌ Error: {response.status_code} - {response.text}')

if __name__ == '__main__':
    test_daybook_reports()
#!/usr/bin/env python3
"""
Customer Ledger Reports Test
Tests date-wise and financial year-wise customer ledger reports
"""
import requests
import json
from datetime import datetime, date, timedelta

BASE_URL = 'http://localhost:8000'

def test_customer_ledger_reports():
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
    
    # Get a customer with transactions
    customer_id = 1  # Test customer from our previous tests
    
    print(f"\n📊 CUSTOMER LEDGER REPORTS FOR CUSTOMER {customer_id}")
    print("=" * 70)
    
    # 1. Current Balance Check
    print("💰 CURRENT BALANCE:")
    response = requests.get(f'{BASE_URL}/api/v1/customer-ledger/customer/{customer_id}/current-balance', headers=headers)
    if response.status_code == 200:
        balance_data = response.json()
        print(f"   Customer: {balance_data.get('customer_name', 'Unknown')}")
        print(f"   Current Balance: Rs.{balance_data.get('balance', 0):,.2f}")
        print(f"   Transaction Count: {balance_data.get('transaction_count', 0)}")
        print(f"   Has COA Account: {balance_data.get('has_coa_account', False)}")
    else:
        print(f"   ❌ Error: {response.status_code} - {response.text}")
    
    # 2. Date-wise Ledger Statement (Last 30 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    print(f"\n📅 LEDGER STATEMENT ({start_date} to {end_date}):")
    response = requests.get(
        f'{BASE_URL}/api/v1/customer-ledger/customer/{customer_id}/statement?start_date={start_date}&end_date={end_date}',
        headers=headers
    )
    
    if response.status_code == 200:
        ledger_data = response.json()
        summary = ledger_data.get('summary', {})
        entries = ledger_data.get('entries', [])
        verification = ledger_data.get('balance_verification', {})
        
        print(f"   Customer: {summary.get('customer_name', 'Unknown')} ({summary.get('account_code', 'N/A')})")
        print(f"   Period: {summary.get('period_start')} to {summary.get('period_end')}")
        print(f"   Opening Balance: Rs.{summary.get('opening_balance', 0):,.2f}")
        print(f"   Closing Balance: Rs.{summary.get('closing_balance', 0):,.2f}")
        print(f"   Total Debits: Rs.{summary.get('total_debit', 0):,.2f}")
        print(f"   Total Credits: Rs.{summary.get('total_credit', 0):,.2f}")
        print(f"   Net Movement: Rs.{summary.get('net_movement', 0):,.2f}")
        print(f"   Transactions: {summary.get('transaction_count', 0)}")
        
        # Balance verification
        is_balanced = verification.get('is_balanced', False)
        print(f"   Balance Check: {'✅ Balanced' if is_balanced else '❌ Unbalanced'}")
        
        # Show recent transactions
        if entries:
            print(f"\n   📋 RECENT TRANSACTIONS ({len(entries)} total):")
            print("   " + "-" * 65)
            print(f"   {'Date':<12} {'Voucher':<10} {'Description':<20} {'Debit':<10} {'Credit':<10}")
            print("   " + "-" * 65)
            
            for i, entry in enumerate(entries[:10]):  # Show first 10 entries
                entry_date = entry.get('entry_date', 'N/A')[:10]
                voucher_type = entry.get('voucher_type', 'Unknown')[:9]
                narration = entry.get('narration', '')[:18]
                debit = entry.get('debit', 0)
                credit = entry.get('credit', 0)
                
                print(f"   {entry_date:<12} {voucher_type:<10} {narration:<20} {debit:>8,.0f} {credit:>8,.0f}")
            
            if len(entries) > 10:
                print(f"   ... and {len(entries) - 10} more transactions")
    else:
        print(f"   ❌ Error: {response.status_code} - {response.text}")
    
    # 3. Financial Year Summary (Current FY 2024-25)
    current_fy = 2024  # FY 2024-25
    
    print(f"\n📊 FINANCIAL YEAR SUMMARY (FY {current_fy}-{str(current_fy+1)[-2:]}):")
    response = requests.get(
        f'{BASE_URL}/api/v1/customer-ledger/customer/{customer_id}/financial-year-summary?financial_year={current_fy}',
        headers=headers
    )
    
    if response.status_code == 200:
        fy_data = response.json()
        
        print(f"   Financial Year: {fy_data.get('financial_year', 'Unknown')}")
        print(f"   Period: {fy_data.get('start_date')} to {fy_data.get('end_date')}")
        print(f"   Opening Balance: Rs.{fy_data.get('opening_balance', 0):,.2f}")
        print(f"   Closing Balance: Rs.{fy_data.get('closing_balance', 0):,.2f}")
        print(f"   Total Debits: Rs.{fy_data.get('total_debits', 0):,.2f}")
        print(f"   Total Credits: Rs.{fy_data.get('total_credits', 0):,.2f}")
        print(f"   Net Movement: Rs.{fy_data.get('net_movement', 0):,.2f}")
        print(f"   Total Transactions: {fy_data.get('transaction_count', 0)}")
        
        # Month-wise summary
        months_summary = fy_data.get('months_summary', [])
        if months_summary:
            print(f"\n   📅 MONTH-WISE BREAKDOWN:")
            print("   " + "-" * 60)
            print(f"   {'Month':<15} {'Debits':<12} {'Credits':<12} {'Net':<12} {'Trans':<6}")
            print("   " + "-" * 60)
            
            for month in months_summary:
                if month.get('transactions', 0) > 0:  # Only show months with transactions
                    month_name = month.get('month', 'Unknown')[:14]
                    debits = month.get('debits', 0)
                    credits = month.get('credits', 0)
                    net = month.get('net_movement', 0)
                    trans = month.get('transactions', 0)
                    
                    print(f"   {month_name:<15} {debits:>10,.0f} {credits:>10,.0f} {net:>10,.0f} {trans:>4}")
    else:
        print(f"   ❌ Error: {response.status_code} - {response.text}")
    
    # 4. All Customers Summary
    print(f"\n👥 ALL CUSTOMERS LEDGER SUMMARY:")
    response = requests.get(f'{BASE_URL}/api/v1/customer-ledger/customers/ledger-summary', headers=headers)
    
    if response.status_code == 200:
        all_customers = response.json()
        customers = all_customers.get('customers', [])
        
        print(f"   As of Date: {all_customers.get('as_of_date', 'Unknown')}")
        print(f"   Total Customers: {all_customers.get('total_customers', 0)}")
        print(f"   Total Outstanding: Rs.{all_customers.get('total_outstanding', 0):,.2f}")
        
        if customers:
            print(f"\n   🏆 TOP CUSTOMERS BY BALANCE:")
            print("   " + "-" * 55)
            print(f"   {'Customer':<25} {'Balance':<12} {'Transactions':<12}")
            print("   " + "-" * 55)
            
            for i, customer in enumerate(customers[:10]):  # Show top 10
                name = customer.get('customer_name', 'Unknown')[:23]
                balance = customer.get('current_balance', 0)
                trans_count = customer.get('transaction_count', 0)
                
                print(f"   {name:<25} {balance:>10,.0f} {trans_count:>10}")
    else:
        print(f"   ❌ Error: {response.status_code} - {response.text}")
    
    print("\n" + "=" * 70)
    print("📊 CUSTOMER LEDGER REPORTS COMPLETED")
    print("=" * 70)

if __name__ == '__main__':
    test_customer_ledger_reports()
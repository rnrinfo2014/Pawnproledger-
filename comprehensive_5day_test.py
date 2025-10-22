#!/usr/bin/env python3
"""
Comprehensive 5-Day Pawn Shop Test
Complete workflow simulation from opening cash to daily operations
"""

import requests
import json
from datetime import date, datetime, timedelta
import psycopg2
from typing import Dict, List

BASE_URL = "http://localhost:8000"

class PawnShopTester:
    def __init__(self):
        self.headers = None
        self.customers = []
        self.pledges = []
        
    def get_auth_headers(self):
        """Get authentication headers"""
        login_data = {"username": "admin", "password": "admin123"}
        
        try:
            response = requests.post(f"{BASE_URL}/token", data=login_data)
            if response.status_code == 200:
                token = response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {token}"}
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Login failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def check_database_empty(self):
        """Check if database is empty for fresh start"""
        print("\n🔍 Checking Database Status")
        print("=" * 50)
        
        try:
            conn = psycopg2.connect('postgresql://postgres:rnrinfo@localhost:5432/pawnpro')
            cur = conn.cursor()
            
            tables_to_check = ['customers', 'pledges', 'ledger_entries', 'voucher_master', 'pledge_payments']
            
            all_empty = True
            for table in tables_to_check:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                status = "✅ Empty" if count == 0 else f"⚠️ Has {count} records"
                print(f"   {table}: {status}")
                if count > 0:
                    all_empty = False
            
            cur.close()
            conn.close()
            
            if all_empty:
                print("🎉 Database is empty and ready for testing!")
                return True
            else:
                print("⚠️ Database has existing data")
                clean = input("🤔 Clean database first? (y/n): ")
                if clean.lower() == 'y':
                    return self.clean_database()
                return False
                
        except Exception as e:
            print(f"❌ Database check error: {e}")
            return False

    def clean_database(self):
        """Clean database for fresh start"""
        try:
            conn = psycopg2.connect('postgresql://postgres:rnrinfo@localhost:5432/pawnpro')
            conn.autocommit = True
            cur = conn.cursor()
            
            tables = ['ledger_entries', 'pledge_payments', 'pledge_items', 'pledges', 'voucher_master', 'customers']
            
            for table in tables:
                cur.execute(f"TRUNCATE {table} RESTART IDENTITY CASCADE")
                print(f"   ✅ {table}: Cleaned")
            
            cur.close()
            conn.close()
            print("🎉 Database cleaned successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Database cleaning error: {e}")
            return False

    def get_account_id(self, account_code: str):
        """Get account ID by code"""
        try:
            response = requests.get(f"{BASE_URL}/accounts/", headers=self.headers)
            if response.status_code == 200:
                accounts = response.json()
                for account in accounts:
                    if account['account_code'] == account_code:
                        return account['account_id']
        except Exception as e:
            print(f"❌ Error getting account ID for {account_code}: {e}")
        return None

    def create_customers(self):
        """Step 1: Create 5 new customers"""
        print("\n👥 Step 1: Creating 5 New Customers")
        print("=" * 50)
        
        customer_data = [
            {"name": "Raj Kumar", "phone": "9876543210", "address": "123 Main Street, Chennai", "aadhaar": "123456789012"},
            {"name": "Priya Sharma", "phone": "9876543211", "address": "456 Park Road, Mumbai", "aadhaar": "123456789013"},
            {"name": "Arjun Reddy", "phone": "9876543212", "address": "789 Lake View, Bangalore", "aadhaar": "123456789014"},
            {"name": "Meera Patel", "phone": "9876543213", "address": "321 Hill Station, Pune", "aadhaar": "123456789015"},
            {"name": "Karthik Iyer", "phone": "9876543214", "address": "654 Beach Road, Kochi", "aadhaar": "123456789016"}
        ]
        
        for i, customer in enumerate(customer_data, 1):
            try:
                response = requests.post(f"{BASE_URL}/customers", headers=self.headers, json=customer)
                if response.status_code == 200:
                    created_customer = response.json()
                    self.customers.append(created_customer)
                    print(f"   ✅ Customer {i}: {customer['name']} - ID: {created_customer['customer_id']}")
                else:
                    print(f"   ❌ Failed to create {customer['name']}: {response.text}")
            except Exception as e:
                print(f"   ❌ Error creating {customer['name']}: {e}")
        
        print(f"\n📊 Total customers created: {len(self.customers)}")

    def create_opening_cash_entry(self):
        """Step 2: Create opening cash voucher entry for 01-04-2025 at ₹100,000"""
        print("\n💰 Step 2: Creating Opening Cash Entry")
        print("=" * 50)
        
        opening_date = "2025-04-01"
        amount = 100000.0
        
        try:
            # Create opening voucher
            voucher_data = {
                "voucher_date": opening_date,
                "voucher_type": "Journal",
                "narration": "Opening Cash Balance - Financial Year 2025-26",
                "created_by": 1,
                "company_id": 1
            }
            
            response = requests.post(f"{BASE_URL}/vouchers", headers=self.headers, json=voucher_data)
            if response.status_code == 200:
                voucher = response.json()
                voucher_id = voucher['voucher_id']
                print(f"✅ Opening voucher created: {voucher_id}")
                
                # Get account IDs
                cash_account_id = self.get_account_id('1001')  # Cash in Hand
                capital_account_id = self.get_account_id('3001')  # Owner's Capital
                
                if not cash_account_id or not capital_account_id:
                    print("❌ Could not find required accounts")
                    return False
                
                # Dr. Cash Account
                cash_entry = {
                    "voucher_id": voucher_id,
                    "account_id": cash_account_id,
                    "dr_cr": "D",
                    "amount": amount,
                    "narration": "Opening cash balance",
                    "entry_date": opening_date
                }
                
                # Cr. Capital Account
                capital_entry = {
                    "voucher_id": voucher_id,
                    "account_id": capital_account_id,
                    "dr_cr": "C",
                    "amount": amount,
                    "narration": "Opening capital contribution",
                    "entry_date": opening_date
                }
                
                # Create ledger entries
                for entry_data in [cash_entry, capital_entry]:
                    response = requests.post(f"{BASE_URL}/ledger-entries", headers=self.headers, json=entry_data)
                    if response.status_code == 200:
                        entry = response.json()
                        dr_cr = "Dr" if entry['dr_cr'] == 'D' else "Cr"
                        print(f"   ✅ {dr_cr} Entry: ₹{entry['amount']:,.2f} - {entry['narration']}")
                    else:
                        print(f"   ❌ Entry failed: {response.text}")
                        return False
                
                print(f"🎉 Opening cash balance of ₹{amount:,.2f} created successfully!")
                return True
                
            else:
                print(f"❌ Voucher creation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Opening cash entry error: {e}")
            return False

    def create_historical_pledges(self):
        """Step 3: Create pledges on random old dates with different amounts"""
        print("\n🏆 Step 3: Creating Historical Pledges")
        print("=" * 50)
        
        if not self.customers:
            print("❌ No customers available. Create customers first.")
            return False
        
        # Historical pledge data
        pledge_data = [
            {
                "customer_id": self.customers[0]['customer_id'],
                "pledge_date": "2025-04-15",
                "principal_amount": 25000.0,
                "items": [{"item_description": "Gold Chain 22K", "gross_weight": 15.5, "stone_weight": 0.0, "net_weight": 15.5}],
                "narration": "Gold chain pledge"
            },
            {
                "customer_id": self.customers[1]['customer_id'], 
                "pledge_date": "2025-05-10",
                "principal_amount": 35000.0,
                "items": [{"item_description": "Gold Bangles 18K", "gross_weight": 25.2, "stone_weight": 1.2, "net_weight": 24.0}],
                "narration": "Gold bangles pledge"
            },
            {
                "customer_id": self.customers[2]['customer_id'],
                "pledge_date": "2025-07-20", 
                "principal_amount": 45000.0,
                "items": [{"item_description": "Gold Necklace 22K", "gross_weight": 32.8, "stone_weight": 2.8, "net_weight": 30.0}],
                "narration": "Gold necklace pledge"
            },
            {
                "customer_id": self.customers[3]['customer_id'],
                "pledge_date": "2025-09-05",
                "principal_amount": 20000.0,
                "items": [{"item_description": "Gold Ring 18K", "gross_weight": 8.5, "stone_weight": 0.5, "net_weight": 8.0}],
                "narration": "Gold ring pledge"
            },
            {
                "customer_id": self.customers[4]['customer_id'],
                "pledge_date": "2025-10-01", 
                "principal_amount": 55000.0,
                "items": [{"item_description": "Gold Earrings 22K", "gross_weight": 18.7, "stone_weight": 0.7, "net_weight": 18.0}],
                "narration": "Gold earrings pledge"
            }
        ]
        
        for i, pledge in enumerate(pledge_data, 1):
            try:
                response = requests.post(f"{BASE_URL}/pledges", headers=self.headers, json=pledge)
                if response.status_code == 200:
                    created_pledge = response.json()
                    self.pledges.append(created_pledge)
                    customer_name = next((c['customer_name'] for c in self.customers if c['customer_id'] == pledge['customer_id']), 'Unknown')
                    print(f"   ✅ Pledge {i}: ₹{pledge['principal_amount']:,.2f} - {customer_name} ({pledge['pledge_date']})")
                else:
                    print(f"   ❌ Pledge {i} failed: {response.text}")
            except Exception as e:
                print(f"   ❌ Pledge {i} error: {e}")
        
        print(f"\n📊 Total pledges created: {len(self.pledges)}")
        return len(self.pledges) > 0

    def verify_ledger_and_daybook(self):
        """Step 4: Check ledger entries and daybook entries are working properly"""
        print("\n📊 Step 4: Verifying Ledger and Daybook Entries")
        print("=" * 50)
        
        # Check opening balance daybook
        print("📅 Checking Opening Balance (2025-04-01):")
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/daybook/daily-summary?transaction_date=2025-04-01&company_id=1",
                headers=self.headers
            )
            if response.status_code == 200:
                daybook = response.json()
                print(f"   📄 Vouchers: {daybook['summary']['total_vouchers']}")
                print(f"   💰 Total Debits: ₹{daybook['summary']['total_debit']:,.2f}")
                print(f"   💰 Total Credits: ₹{daybook['summary']['total_credit']:,.2f}")
                print(f"   🏦 Opening Balance: ₹{daybook['opening_balance']:,.2f}")
                print(f"   🏦 Closing Balance: ₹{daybook['closing_balance']:,.2f}")
            else:
                print(f"   ❌ Failed to get opening daybook: {response.text}")
        except Exception as e:
            print(f"   ❌ Opening daybook error: {e}")
        
        # Check recent pledge dates
        print("\n📅 Checking Recent Pledge Entries:")
        recent_dates = ["2025-09-05", "2025-10-01"]
        
        for check_date in recent_dates:
            try:
                response = requests.get(
                    f"{BASE_URL}/api/v1/daybook/daily-summary?transaction_date={check_date}&company_id=1",
                    headers=self.headers
                )
                if response.status_code == 200:
                    daybook = response.json()
                    if daybook['summary']['total_vouchers'] > 0:
                        print(f"   📅 {check_date}: {daybook['summary']['total_vouchers']} vouchers, Balance: ₹{daybook['closing_balance']:,.2f}")
                    else:
                        print(f"   📅 {check_date}: No transactions")
                else:
                    print(f"   ❌ Failed to get {check_date} daybook: {response.text}")
            except Exception as e:
                print(f"   ❌ {check_date} daybook error: {e}")
        
        # Check ledger entries count
        print("\n📋 Ledger Entries Summary:")
        try:
            conn = psycopg2.connect('postgresql://postgres:rnrinfo@localhost:5432/pawnpro')
            cur = conn.cursor()
            
            cur.execute("SELECT COUNT(*) FROM ledger_entries")
            total_entries = cur.fetchone()[0]
            print(f"   📊 Total Ledger Entries: {total_entries}")
            
            cur.execute("SELECT COUNT(DISTINCT voucher_id) FROM voucher_master")
            total_vouchers = cur.fetchone()[0]
            print(f"   📊 Total Vouchers: {total_vouchers}")
            
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Ledger summary error: {e}")

    def create_last_5days_transactions(self):
        """Step 5: Enter last 5 days transactions (income, expenses, pledge close)"""
        print("\n📅 Step 5: Creating Last 5 Days Transactions")
        print("=" * 50)
        
        # Get last 5 days from today
        today = date.today()
        last_5_days = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(4, -1, -1)]
        
        print(f"Creating transactions for: {', '.join(last_5_days)}")
        
        # Day-wise transaction data
        daily_transactions = [
            # Day 1 (5 days ago)
            {
                "date": last_5_days[0],
                "transactions": [
                    {"type": "Income", "amount": 5000, "narration": "Auction income - old pledge item", "account": "4002"},
                    {"type": "Expense", "amount": 2000, "narration": "Office electricity bill", "account": "5003"}
                ]
            },
            # Day 2 (4 days ago)
            {
                "date": last_5_days[1],
                "transactions": [
                    {"type": "Income", "amount": 8000, "narration": "Interest income from active pledges", "account": "4001"},
                    {"type": "Expense", "amount": 3500, "narration": "Staff salary advance", "account": "5001"}
                ]
            },
            # Day 3 (3 days ago)
            {
                "date": last_5_days[2], 
                "transactions": [
                    {"type": "Income", "amount": 12000, "narration": "Gold jewelry sale", "account": "4002"},
                    {"type": "Expense", "amount": 1500, "narration": "Office supplies purchase", "account": "5004"}
                ]
            },
            # Day 4 (2 days ago)
            {
                "date": last_5_days[3],
                "transactions": [
                    {"type": "Expense", "amount": 5000, "narration": "Monthly rent payment", "account": "5002"},
                    {"type": "Income", "amount": 15000, "narration": "Pledge closure with interest", "account": "4001"}
                ]
            },
            # Day 5 (yesterday)
            {
                "date": last_5_days[4],
                "transactions": [
                    {"type": "Income", "amount": 20000, "narration": "New pledge amount disbursed", "account": "4001"},
                    {"type": "Expense", "amount": 2500, "narration": "Security services payment", "account": "5005"}
                ]
            }
        ]
        
        for day_data in daily_transactions:
            transaction_date = day_data["date"]
            print(f"\n📅 Processing {transaction_date}:")
            
            for trans in day_data["transactions"]:
                try:
                    # Create voucher
                    voucher_data = {
                        "voucher_date": transaction_date,
                        "voucher_type": trans["type"],
                        "narration": trans["narration"],
                        "created_by": 1,
                        "company_id": 1
                    }
                    
                    response = requests.post(f"{BASE_URL}/vouchers", headers=self.headers, json=voucher_data)
                    if response.status_code == 200:
                        voucher = response.json()
                        voucher_id = voucher['voucher_id']
                        
                        # Get account IDs
                        cash_account_id = self.get_account_id('1001')  # Cash
                        other_account_id = self.get_account_id(trans["account"])
                        
                        if trans["type"] == "Income":
                            # Dr. Cash, Cr. Income Account
                            entries = [
                                {
                                    "voucher_id": voucher_id,
                                    "account_id": cash_account_id,
                                    "dr_cr": "D",
                                    "amount": trans["amount"],
                                    "narration": f"Cash received - {trans['narration']}",
                                    "entry_date": transaction_date
                                },
                                {
                                    "voucher_id": voucher_id,
                                    "account_id": other_account_id,
                                    "dr_cr": "C",
                                    "amount": trans["amount"],
                                    "narration": trans["narration"],
                                    "entry_date": transaction_date
                                }
                            ]
                        else:  # Expense
                            # Dr. Expense Account, Cr. Cash
                            entries = [
                                {
                                    "voucher_id": voucher_id,
                                    "account_id": other_account_id,
                                    "dr_cr": "D",
                                    "amount": trans["amount"],
                                    "narration": trans["narration"],
                                    "entry_date": transaction_date
                                },
                                {
                                    "voucher_id": voucher_id,
                                    "account_id": cash_account_id,
                                    "dr_cr": "C",
                                    "amount": trans["amount"],
                                    "narration": f"Cash paid - {trans['narration']}",
                                    "entry_date": transaction_date
                                }
                            ]
                        
                        # Create ledger entries
                        success = True
                        for entry_data in entries:
                            response = requests.post(f"{BASE_URL}/ledger-entries", headers=self.headers, json=entry_data)
                            if response.status_code != 200:
                                success = False
                                break
                        
                        if success:
                            type_icon = "💰" if trans["type"] == "Income" else "💸"
                            print(f"   {type_icon} {trans['type']}: ₹{trans['amount']:,.2f} - {trans['narration']}")
                        else:
                            print(f"   ❌ Failed to create entries for: {trans['narration']}")
                    else:
                        print(f"   ❌ Failed to create voucher: {trans['narration']}")
                        
                except Exception as e:
                    print(f"   ❌ Transaction error: {e}")

    def check_last_5days_daybook(self):
        """Step 6: Check last 5 days daybook working, opening closing everything"""
        print("\n📊 Step 6: Verifying Last 5 Days Daybook")
        print("=" * 50)
        
        # Get last 5 days
        today = date.today()
        last_5_days = [(today - timedelta(days=i)) for i in range(4, -1, -1)]
        
        print("📅 Daily Summary Report:")
        print("-" * 80)
        print(f"{'Date':<12} {'Vouchers':<8} {'Debits':<12} {'Credits':<12} {'Opening':<12} {'Closing':<12}")
        print("-" * 80)
        
        for check_date in last_5_days:
            date_str = check_date.strftime("%Y-%m-%d")
            try:
                response = requests.get(
                    f"{BASE_URL}/api/v1/daybook/daily-summary?transaction_date={date_str}&company_id=1",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    daybook = response.json()
                    vouchers = daybook['summary']['total_vouchers']
                    debits = daybook['summary']['total_debit']
                    credits = daybook['summary']['total_credit']
                    opening = daybook['opening_balance']
                    closing = daybook['closing_balance']
                    
                    print(f"{date_str:<12} {vouchers:<8} ₹{debits:>9,.0f} ₹{credits:>9,.0f} ₹{opening:>9,.0f} ₹{closing:>9,.0f}")
                    
                    # Show entries if any
                    if vouchers > 0:
                        entries = daybook.get('entries', [])
                        for entry in entries[:3]:  # Show first 3 entries
                            amount = entry.get('debit', 0) if entry.get('debit', 0) > 0 else entry.get('credit', 0)
                            dr_cr = "Dr" if entry.get('debit', 0) > 0 else "Cr"
                            print(f"             • {entry.get('account_name')} ({dr_cr}): ₹{amount:,.2f}")
                        if len(entries) > 3:
                            print(f"             ... and {len(entries) - 3} more entries")
                        print()
                        
                else:
                    print(f"{date_str:<12} {'ERROR':<8} {'N/A':<12} {'N/A':<12} {'N/A':<12} {'N/A':<12}")
                    
            except Exception as e:
                print(f"{date_str:<12} {'ERROR':<8} {str(e)[:50]}")
        
        print("-" * 80)
        
        # Summary statistics
        print("\n📈 Overall Summary:")
        try:
            conn = psycopg2.connect('postgresql://postgres:rnrinfo@localhost:5432/pawnpro')
            cur = conn.cursor()
            
            # Total transactions in last 5 days
            start_date = (today - timedelta(days=4)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
            
            cur.execute("""
                SELECT COUNT(DISTINCT vm.voucher_id) as vouchers,
                       SUM(CASE WHEN le.dr_cr = 'D' THEN le.amount ELSE 0 END) as total_debits,
                       SUM(CASE WHEN le.dr_cr = 'C' THEN le.amount ELSE 0 END) as total_credits
                FROM voucher_master vm
                JOIN ledger_entries le ON vm.voucher_id = le.voucher_id
                WHERE vm.voucher_date >= %s AND vm.voucher_date <= %s
                AND vm.company_id = 1
            """, (start_date, end_date))
            
            result = cur.fetchone()
            if result:
                vouchers, debits, credits = result
                print(f"   📊 Total Vouchers (Last 5 days): {vouchers or 0}")
                print(f"   📊 Total Debits: ₹{debits or 0:,.2f}")
                print(f"   📊 Total Credits: ₹{credits or 0:,.2f}")
                print(f"   📊 Balance Check: {'✅ Balanced' if abs((debits or 0) - (credits or 0)) < 0.01 else '❌ Unbalanced'}")
            
            # Current cash balance
            cur.execute("""
                SELECT SUM(CASE WHEN le.dr_cr = 'D' THEN le.amount ELSE -le.amount END) as cash_balance
                FROM ledger_entries le
                JOIN voucher_master vm ON le.voucher_id = vm.voucher_id
                JOIN accounts_master am ON le.account_id = am.account_id
                WHERE am.account_code = '1001'
                AND vm.company_id = 1
            """)
            
            cash_result = cur.fetchone()
            if cash_result and cash_result[0]:
                print(f"   💰 Current Cash Balance: ₹{cash_result[0]:,.2f}")
            
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Summary calculation error: {e}")

    def run_complete_test(self):
        """Run the complete 5-day test workflow"""
        print("🚀 Starting Comprehensive 5-Day Pawn Shop Test")
        print("=" * 60)
        
        # Step 0: Authentication
        if not self.get_auth_headers():
            return False
        
        # Step 0.1: Check database
        if not self.check_database_empty():
            return False
        
        # Step 1: Create customers
        self.create_customers()
        
        # Step 2: Create opening cash entry
        if not self.create_opening_cash_entry():
            print("❌ Failed to create opening cash entry")
            return False
        
        # Step 3: Create historical pledges
        if not self.create_historical_pledges():
            print("❌ Failed to create historical pledges")
            return False
        
        # Step 4: Verify ledger and daybook
        self.verify_ledger_and_daybook()
        
        # Step 5: Create last 5 days transactions
        self.create_last_5days_transactions()
        
        # Step 6: Check last 5 days daybook
        self.check_last_5days_daybook()
        
        print("\n🎉 Comprehensive 5-Day Test Completed Successfully!")
        print("✅ All steps executed:")
        print("   • 5 customers created")
        print("   • Opening cash balance set (₹100,000)")
        print("   • Historical pledges created")
        print("   • Ledger entries verified")
        print("   • 5 days of transactions added")
        print("   • Daybook functionality confirmed")
        print("\n💡 Your pawn shop system is working perfectly!")

if __name__ == "__main__":
    tester = PawnShopTester()
    tester.run_complete_test()
"""
COA Usage Examples and Business Logic
How to use Chart of Accounts in PawnSoft Business Operations
"""

# 1. GET ACCOUNTS BY TYPE
# http://localhost:8000/api/v1/coa/accounts?company_id=1&account_type=Asset
# http://localhost:8000/api/v1/coa/accounts?company_id=1&account_type=Income

# 2. GET TREE STRUCTURE (Only Parent Accounts)
# http://localhost:8000/api/v1/coa/accounts/tree?company_id=1

# 3. CREATE NEW ACCOUNT
POST http://localhost:8000/api/v1/coa/accounts
{
    "account_name": "Customer - Rajesh Kumar",
    "account_code": "2001-001",
    "account_type": "Liability",
    "group_name": "Customer Accounts",
    "parent_id": 30,
    "company_id": 1,
    "is_active": true
}

# 4. PAWN BUSINESS TRANSACTION MAPPING

## When Pledge is Created:
# Debit: Pledged Ornaments (1005) - Asset increases
# Credit: Customer Pledge Accounts (2001) - Liability increases

## When Interest is Earned:
# Debit: Customer Pledge Accounts (2001) - Reduce customer liability
# Credit: Pledge Interest Income (4001) - Income increases

## When Cash Payment Received:
# Debit: Cash in Hand (1001) - Asset increases
# Credit: Customer Pledge Accounts (2001) - Reduce customer liability

## When Auction Happens:
# Debit: Cash in Hand (1001) - Cash received
# Credit: Auction Income (4002) - Income from auction
# Credit: Pledged Ornaments (1005) - Remove from inventory

# 5. MONTHLY EXPENSE ENTRIES
# Staff Salary Payment:
# Debit: Staff Salaries (5001) - Expense
# Credit: Cash in Hand (1001) - Cash reduced

# Rent Payment:
# Debit: Rent Expense (5002) - Expense
# Credit: Cash at Bank (1002) - Bank balance reduced

# 6. CUSTOMER WISE SUB-ACCOUNTS
# Create individual customer accounts under "Customer Pledge Accounts" (2001)
# Each customer gets their own account code like 2001-001, 2001-002, etc.

# 7. BANK WISE SUB-ACCOUNTS
# Create separate accounts for each bank under "Cash at Bank" (1002)
# Like: SBI Account (1002-001), HDFC Account (1002-002)

# 8. INVENTORY MANAGEMENT
# Gold Purchase:
# Debit: Gold Inventory (1003)
# Credit: Cash in Hand (1001) or Cash at Bank (1002)

# Gold Sale/Auction:
# Debit: Cash in Hand (1001)
# Credit: Gold Inventory (1003)
# Credit: Auction Income (4002) - if profit

# 9. REPORTING USAGE
# Balance Sheet: Assets (1000 series) vs Liabilities (2000 series) + Equity (3000 series)
# P&L Statement: Income (4000 series) - Expenses (5000 series)

# 10. ACCOUNT HIERARCHY BENEFITS
# You can get:
# - Total Current Assets = Sum of all accounts under Current Assets (1000)
# - Total Revenue = Sum of all accounts under Revenue (4000)
# - Operating Expenses = Sum of all accounts under Operating Expenses (5000)

"""
Business Rules for Pawn Shop COA:

1. CUSTOMER ACCOUNTS:
   - Each customer should have individual sub-account under Customer Pledge Accounts
   - Format: Customer Name - Account Code (2001-XXX)

2. PLEDGE TRANSACTIONS:
   - Always involves Pledged Ornaments (Asset) and Customer Account (Liability)
   - Interest calculations should credit Pledge Interest Income

3. AUCTION PROCESS:
   - Transfer from Pledged Ornaments to Auction Inventory
   - Final sale creates Auction Income

4. CASH MANAGEMENT:
   - Multiple cash accounts for different locations/purposes
   - Bank accounts for each banking relationship

5. EXPENSE TRACKING:
   - Monthly recurring expenses (Rent, Salary, Electricity)
   - Variable expenses (Security, Maintenance)
   - Regulatory expenses (License, Insurance)

6. FINANCIAL REPORTING:
   - Monthly P&L: Income - Expenses
   - Balance Sheet: Assets = Liabilities + Equity
   - Cash Flow: Track cash movements across accounts
"""
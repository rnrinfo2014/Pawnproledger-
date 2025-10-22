"""
Transaction Creation Guide for PawnSoft
=======================================

Account transactions உங்க system-ல எப்படி create ஆகும்:

## 1. AUTO-GENERATED TRANSACTIONS (System Creates)

### A. Pledge Creation Transaction:
When pledge is created → System automatically creates:

Voucher Master:
- voucher_type: "Pledge"
- voucher_date: pledge_date
- narration: "Pledge created for customer"

Ledger Entries:
- Debit: Pledged Ornaments (1005) - ₹50,000
- Credit: Customer Pledge Account (2001-XXX) - ₹50,000

### B. Payment Receipt Transaction:
When payment is received → System automatically creates:

Voucher Master:
- voucher_type: "Receipt"
- voucher_date: payment_date
- narration: "Payment received from customer"

Ledger Entries:
- Debit: Cash in Hand (1001) - ₹3,000
- Credit: Customer Pledge Account (2001-XXX) - ₹2,500 (Principal)
- Credit: Pledge Interest Income (4001) - ₹500 (Interest)

### C. First Interest Payment (Auto):
When pledge is created → System automatically creates first interest payment:

Voucher Master:
- voucher_type: "Receipt"
- voucher_date: pledge_date
- narration: "Automatic first month interest"

Ledger Entries:
- Debit: Customer Pledge Account (2001-XXX) - ₹1,500
- Credit: Pledge Interest Income (4001) - ₹1,500

## 2. MANUAL TRANSACTIONS (User Creates)

### A. Journal Entries:
Admin can manually create journal entries:

POST /vouchers
{
    "voucher_type": "Journal",
    "voucher_date": "2025-09-17",
    "narration": "Manual adjustment",
    "created_by": 1,
    "company_id": 1
}

Then add ledger entries:
POST /ledger-entries
{
    "voucher_id": 123,
    "account_id": 19, // Cash in Hand
    "dr_cr": "D",
    "amount": 5000.0,
    "narration": "Cash received",
    "entry_date": "2025-09-17"
}

### B. Expense Transactions:
Manual expense entry:

Voucher Master:
- voucher_type: "Payment"
- narration: "Salary payment"

Ledger Entries:
- Debit: Staff Salaries (5001) - ₹25,000
- Credit: Cash in Hand (1001) - ₹25,000

## 3. WHERE TRANSACTIONS ARE SAVED:

Database Tables:
1. voucher_master → Transaction header
2. ledger_entries → Individual debit/credit lines
3. accounts_master → Chart of accounts

## 4. CURRENT API ENDPOINTS:

Auto Transactions (Built-in):
- POST /pledges → Auto creates pledge voucher
- POST /pledge-payments → Auto creates payment voucher

Manual Transactions:
- POST /vouchers → Create voucher header
- POST /ledger-entries → Add individual entries

## 5. TRANSACTION VALIDATION:

System Ensures:
✓ Debits = Credits for each voucher
✓ Valid account codes
✓ Positive amounts only
✓ Proper authorization

## 6. BUSINESS RULES:

Pledge Transactions:
- Auto-create first interest payment
- Generate unique pledge numbers
- Link to customer accounts

Payment Transactions:
- Auto-calculate interest/principal split
- Update pledge balances
- Generate receipt numbers

## 7. REPORTING:

Available Reports:
- Daily Summary (Daybook)
- Account-wise transactions
- Voucher-wise summary
- Monthly reports

## 8. INTEGRATION POINTS:

Current Auto-Integration:
- Pledge Creation → Ledger Entries
- Payment Receipt → Ledger Entries
- Interest Calculation → Automatic entries

Future Auto-Integration Options:
- Auction Sales → Auto entries
- Expense approvals → Auto vouchers
- Bank reconciliation → Auto adjustments

## 9. MANUAL OVERRIDE:

Admin Users Can:
- Create manual journal entries
- Adjust account balances
- Create correction entries
- Generate custom vouchers

## 10. AUDIT TRAIL:

Every Transaction Records:
- Created by (user_id)
- Created at (timestamp)  
- Company context
- Reference linkage
"""
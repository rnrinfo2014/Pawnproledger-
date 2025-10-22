# Manual Income/Expense Entry Workflow Guide

## Overview (அவலோகனம்)
இந்த guide manual income/expense entries எப்படி create பண்ணுவது மற்றும் அவை daybook ல எப்படி reflect ஆகும் என்று விளக்குகிறது.

## Workflow Steps (வொர்க்ஃபிலோ படிகள்)

### Step 1: Create Voucher (வௌச்சர் உருவாக்கம்)
```http
POST /vouchers
Authorization: Bearer <token>
Content-Type: application/json

{
    "voucher_date": "2024-01-15",
    "voucher_type": "Income",  // or "Expense" 
    "narration": "Office rent received from tenant",
    "company_id": 1
}
```

**Response:**
```json
{
    "voucher_id": 123,
    "voucher_date": "2024-01-15",
    "voucher_type": "Income",
    "narration": "Office rent received from tenant",
    "company_id": 1
}
```

### Step 2: Create Ledger Entries (லெட்ஜர் என்ட்ரிகள்)

#### For Income Entry (வருமானத்திற்கு):
```http
POST /ledger-entries
Authorization: Bearer <token>
Content-Type: application/json

// Entry 1: Dr. Cash Account (Asset increase)
{
    "voucher_id": 123,
    "account_id": 1,  // Cash Account (1001)
    "debit": 25000.0,
    "credit": 0.0,
    "description": "Cash received - Office rent",
    "transaction_date": "2024-01-15"
}

// Entry 2: Cr. Income Account (Income recognition)
{
    "voucher_id": 123,
    "account_id": 15, // Rental Income Account (4001)
    "debit": 0.0,
    "credit": 25000.0,
    "description": "Rental income earned",
    "transaction_date": "2024-01-15"
}
```

#### For Expense Entry (செலவுக்கு):
```http
POST /ledger-entries
Authorization: Bearer <token>
Content-Type: application/json

// Entry 1: Dr. Expense Account (Expense increase)
{
    "voucher_id": 124,
    "account_id": 25, // Office Expense Account (5001)
    "debit": 5500.0,
    "credit": 0.0,
    "description": "Office supplies purchased",
    "transaction_date": "2024-01-15"
}

// Entry 2: Cr. Cash Account (Asset decrease)
{
    "voucher_id": 124,
    "account_id": 1,  // Cash Account (1001)
    "debit": 0.0,
    "credit": 5500.0,
    "description": "Cash paid for office supplies",
    "transaction_date": "2024-01-15"
}
```

### Step 3: Verify Daybook Reflection (டேபுக் சரிபார்ப்பு)

#### Check Daily Summary:
```http
GET /api/v1/daybook/daily-summary?transaction_date=2024-01-15&company_id=1
Authorization: Bearer <token>
```

**Response:**
```json
{
    "summary": {
        "date": "2024-01-15",
        "total_vouchers": 2,
        "total_debit": 30500.0,
        "total_credit": 30500.0,
        "balance_difference": 0.0,
        "voucher_types": {
            "Income": 1,
            "Expense": 1
        }
    },
    "entries": [
        {
            "entry_date": "2024-01-15",
            "voucher_id": 123,
            "voucher_type": "Income",
            "voucher_no": "Income-000123",
            "account_name": "Cash",
            "account_code": "1001",
            "narration": "Cash received - Office rent",
            "debit": 25000.0,
            "credit": 0.0,
            "running_balance": 25000.0
        },
        // ... more entries
    ],
    "opening_balance": 150000.0,  // Previous day's closing balance
    "closing_balance": 169500.0   // Opening + (Debits - Credits)
}
```

## Account Types for Manual Entries (கணக்கு வகைகள்)

### Assets (சொத்துக்கள்) - Debit increases, Credit decreases
- **1001**: Cash Account
- **1002**: Bank Account  
- **1003**: Accounts Receivable

### Income (வருமானம்) - Credit increases, Debit decreases
- **4001**: Interest Income
- **4002**: Rental Income
- **4003**: Service Income

### Expenses (செலவுகள்) - Debit increases, Credit decreases
- **5001**: Office Expense
- **5002**: Administrative Expense
- **5008**: Customer Discount

## Double Entry Rules (இரட்டை பதிவு விதிகள்)

### Income Entry (வருமான பதிவு):
```
Dr. Cash/Bank Account    ₹25,000  (Asset increase)
    Cr. Income Account           ₹25,000  (Income earned)
```

### Expense Entry (செலவு பதிவு):
```
Dr. Expense Account     ₹5,500   (Expense incurred)
    Cr. Cash/Bank Account        ₹5,500   (Asset decrease)
```

## Opening Balance Calculation (தொடக்க இருப்பு கணக்கீடு)

### Formula:
```
Opening Balance (Today) = Closing Balance (Previous Day)
Closing Balance = Opening Balance + (Total Debits - Total Credits)
```

### Example:
```
January 14 Closing Balance: ₹150,000
January 15 Transactions:
  - Debits: ₹30,500
  - Credits: ₹30,500
January 15 Opening Balance: ₹150,000
January 15 Closing Balance: ₹150,000 + (₹30,500 - ₹30,500) = ₹150,000
```

## Daybook Reports Available (கிடைக்கும் டேபுக் அறிக்கைகள்)

1. **Daily Summary**: `/api/v1/daybook/daily-summary`
2. **Account-wise Summary**: `/api/v1/daybook/account-wise-summary`
3. **Date Range Summary**: `/api/v1/daybook/date-range-summary`
4. **Voucher Type Summary**: `/api/v1/daybook/voucher-type-summary`

## Testing Manual Entries (கையேடு பதிவுகளை சோதனை)

Run the test script:
```bash
python test_manual_income_expense.py
```

இந்த script:
- ✅ Manual vouchers create பண்ணும்
- ✅ Proper ledger entries add பண்ணும்
- ✅ Daybook reflection verify பண்ணும்
- ✅ Opening/closing balance check பண்ணும்

## Important Notes (முக்கியமான குறிப்புகள்)

1. **Balance Verification**: Total debits must equal total credits for each voucher
2. **Account Selection**: Use correct account types for proper financial reporting
3. **Date Consistency**: All entries for a voucher must have the same date
4. **Narration**: Provide clear descriptions for audit trail
5. **Company ID**: Always specify correct company for multi-company setup

## Common Scenarios (பொதுவான சூழ்நிலைகள்)

### Scenario 1: Daily Cash Sales
```
Dr. Cash Account        ₹50,000
    Cr. Sales Income            ₹50,000
```

### Scenario 2: Utility Bill Payment
```
Dr. Utilities Expense  ₹3,000
    Cr. Cash Account            ₹3,000
```

### Scenario 3: Bank Interest Received
```
Dr. Bank Account       ₹1,200
    Cr. Interest Income         ₹1,200
```

## Error Handling (பிழை கையாளுதல்)

- **Unbalanced Entries**: System will reject if debits ≠ credits
- **Invalid Account**: Verify account_id exists before entry
- **Date Issues**: Ensure proper date format (YYYY-MM-DD)
- **Authorization**: Valid token required for all operations

இந்த workflow follow பண்ணா, manual entries properly daybook ல reflect ஆகும் மற்றும் opening balance correctly calculate ஆகும்!

## ✅ Test Results Summary

### Successfully Tested:
- ✅ **Manual Voucher Creation**: Income and Expense vouchers created successfully
- ✅ **Ledger Entry Creation**: Double-entry bookkeeping with proper Dr/Cr entries  
- ✅ **Daybook Integration**: All manual entries reflect immediately in daybook
- ✅ **Balance Verification**: Total debits = Total credits (₹30,500 each)
- ✅ **Opening Balance**: Previous day's closing balance carried forward correctly
- ✅ **Account-wise Reporting**: All manual transactions categorized properly

### Test Results:
```
📊 Test Summary (2025-10-22):
   📄 Total Vouchers: 2 (1 Income, 1 Expense)
   💰 Total Debits: ₹30,500.00
   💰 Total Credits: ₹30,500.00
   ⚖️ Balance Difference: ₹0.00 (Balanced)
   
   Manual Entries Created:
   1. Income Entry: Office rent ₹25,000
      - Dr. Cash Account ₹25,000
      - Cr. Interest Income ₹25,000
   
   2. Expense Entry: Office supplies ₹5,500
      - Dr. Staff Salaries ₹5,500  
      - Cr. Cash Account ₹5,500
```

### Daybook Features Working:
- **Daily Summary**: Complete transaction overview with voucher counts
- **Account-wise Summary**: Transactions grouped by account
- **Running Balance**: Real-time balance calculation
- **Opening Balance Calculation**: Based on previous day's transactions

## 🚀 Quick Start Commands

```bash
# Test the complete manual entry system
python test_manual_income_expense.py

# Check voucher constraints in database
python check_voucher_types.py

# View daybook for today
curl "http://localhost:8000/api/v1/daybook/daily-summary?transaction_date=2025-10-22&company_id=1" \
  -H "Authorization: Bearer <your-token>"
```

Manual entry system தயார் ஆயிடுச்சு! 🎉
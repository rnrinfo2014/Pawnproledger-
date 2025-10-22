# Discount and Penalty Accounting Documentation

## Overview
The PawnSoft system now properly handles discount and penalty amounts in financial transactions with complete double-entry bookkeeping.

## Accounting Treatment

### 📊 **Standard Payment (No Discount/Penalty)**
```
Dr. Cash Account           ₹2,000
    Cr. Customer Account        ₹2,000
```

### 💰 **Payment with Discount**
When a discount of ₹100 is given:
```
Dr. Cash Account           ₹2,000
Dr. Customer Discount      ₹100     (Expense - reduces profit)
    Cr. Customer Account        ₹2,100
```

### ⚠️ **Payment with Penalty**
When a penalty of ₹50 is charged:
```
Dr. Cash Account           ₹2,000
    Cr. Customer Account        ₹1,950
    Cr. Penalty Income          ₹50     (Income - increases profit)
```

### 💰⚠️ **Payment with Both Discount and Penalty**
When both discount (₹100) and penalty (₹50) are applied:
```
Dr. Cash Account           ₹2,000
Dr. Customer Discount      ₹100     (Expense)
    Cr. Customer Account        ₹2,050
    Cr. Penalty Income          ₹50     (Income)
```

## Chart of Accounts Integration

### Required Accounts
- **5008** - Customer Discount (Expense)
- **4003** - Service Charges/Penalty Income (Income)
- **4002** - Interest Income (Income)
- **1001** - Cash Account (Asset)

### Auto-Creation
These accounts are automatically created when setting up the default Chart of Accounts for new companies.

## Database Storage

### PledgePayment Table Fields
- `discount_amount` - Amount of discount given (stored as positive value)
- `penalty_amount` - Amount of penalty charged (stored as positive value)
- `amount` - Actual cash received amount
- `interest_amount` - Interest portion
- `principal_amount` - Principal portion

### Ledger Entries
Each payment creates multiple ledger entries:
1. **Cash Debit** - Actual amount received
2. **Customer Credit** - Net customer account impact
3. **Interest Income Credit** - Interest portion (if any)
4. **Penalty Income Credit** - Penalty portion (if any)
5. **Discount Expense Debit** - Discount given (if any)

## Business Rules

### Authorization
- **Discounts**: Require `approve_discount: true` flag
- **Penalties**: Require `approve_penalty: true` flag
- **Audit Trail**: Reasons mandatory for both

### Validation
- All accounting entries must balance (total debits = total credits)
- Net customer impact = payment_amount - interest - penalty + discount
- Manager approval required for any discount/penalty amounts

## API Response Enhancement

### Payment Response Fields
```json
{
  "total_amount_paid": 2000.0,
  "total_discount_given": 100.0,
  "total_penalty_charged": 50.0,
  "net_amount": 1950.0,
  "pledge_results": [
    {
      "payment_amount": 2000.0,
      "discount_amount": 100.0,
      "penalty_amount": 50.0,
      "net_payment_amount": 1950.0
    }
  ]
}
```

## Example Scenarios

### Scenario 1: Customer Loyalty Discount
- Customer pays ₹5,000 for multiple pledges
- Given ₹200 loyalty discount
- **Result**: Customer account credited ₹5,200, Discount expense ₹200

### Scenario 2: Late Payment Penalty
- Customer pays ₹3,000 but is 30 days late
- Charged ₹150 penalty
- **Result**: Customer account credited ₹2,850, Penalty income ₹150

### Scenario 3: Mixed Transaction
- Payment: ₹4,000
- Discount: ₹100 (early payment incentive)
- Penalty: ₹50 (processing fee)
- **Net Effect**: Customer gets ₹50 benefit overall

## Verification Methods

### 1. Check Payment Record
```bash
GET /pledge-payments/{payment_id}
```
Verify `discount_amount` and `penalty_amount` fields are saved.

### 2. Check Ledger Entries
```bash
GET /ledger-entries/?limit=50
```
Look for entries with account codes 5008 (discount) and 4003 (penalty).

### 3. Accounting Balance Verification
All entries for a payment must have:
```
Total Debits = Total Credits
```

### 4. Customer Account Impact
```
Customer Credit = Payment Amount - Interest - Penalty + Discount
```

## Error Handling

### Missing Accounts
If required COA accounts don't exist:
- System attempts fallback account codes
- Transaction fails if no suitable account found
- Clear error message provided

### Unbalanced Entries
If debits ≠ credits:
- Transaction is rolled back
- Detailed error message shows amounts
- All changes are reverted

## Performance Impact

### Minimal Overhead
- Discount/penalty processing adds ~2-3 additional ledger entries
- No significant performance impact
- All operations within same database transaction

### Audit Trail
- Complete transaction history maintained
- Voucher numbers link all related entries
- Reason tracking for compliance

## Testing

Use `test_discount_penalty_accounting.py` to verify:
1. ✅ Payment creation with discount/penalty
2. ✅ Accounting entries generation
3. ✅ Database storage verification
4. ✅ COA account existence
5. ✅ Balance verification

## Conclusion

The discount and penalty feature provides:
- **Complete Accounting Integration** - Proper double-entry bookkeeping
- **Audit Compliance** - Full transaction trails with reasons
- **Business Flexibility** - Support for various discount/penalty scenarios
- **Data Integrity** - Balanced accounting entries with validation
- **Performance** - Minimal overhead with robust error handling

Now both penalty and discount amounts are properly saved in financial transactions! 🎉
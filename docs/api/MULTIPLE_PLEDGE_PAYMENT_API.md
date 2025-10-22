# Multiple Pledge Payment API Documentation

## Overview
This API provides functionality for handling multiple pledges in a single payment transaction, which is a common requirement in pawn shop operations.

## 1. Customer Pending Pledges API

### Endpoint
```
GET /customers/{customer_id}/pending-pledges
```

### Description
Fetches all active pledges for a customer with detailed interest calculations and payment breakdowns.

### Request Parameters
- `customer_id` (path parameter): Integer - The customer's ID

### Authentication
- Requires admin/staff authentication
- Customer must belong to user's company

### Response Model: `CustomerPendingPledgesResponse`

```json
{
  "customer_id": 1,
  "customer_name": "Rajesh Kumar",
  "total_pledges": 3,
  "total_outstanding": 125000.0,
  "pledges": [
    {
      "pledge_id": 101,
      "pledge_no": "PLG001",
      "pledge_amount": 50000.0,
      "scheme_id": 1,
      "pledge_date": "2024-01-15",
      "due_date": "2024-04-15",
      "total_interest_due": 7500.0,
      "paid_principal": 0.0,
      "paid_interest": 2500.0,
      "current_outstanding": 55000.0,
      "days_since_pledge": 90,
      "months_elapsed": 3,
      "first_month_interest": 2500.0,
      "additional_interest": 5000.0,
      "remaining_principal": 50000.0,
      "remaining_interest": 5000.0,
      "scheme_name": "Gold Loan - 5% Monthly",
      "monthly_interest_rate": 5.0
    }
  ]
}
```

### Field Descriptions

#### Main Response Fields:
- `customer_id`: Customer's unique identifier
- `customer_name`: Customer's full name
- `total_pledges`: Number of active pledges
- `total_outstanding`: Sum of all outstanding amounts across pledges

#### Individual Pledge Fields:
- `pledge_id`: Unique pledge identifier
- `pledge_no`: Human-readable pledge number
- `pledge_amount`: Original loan/pledge amount
- `scheme_id`: Interest scheme identifier
- `pledge_date`: Date when pledge was created
- `due_date`: Maturity/due date for the pledge
- `total_interest_due`: Total interest calculated based on elapsed time
- `paid_principal`: Amount of principal already paid
- `paid_interest`: Amount of interest already paid
- `current_outstanding`: Total amount currently due (remaining principal + remaining interest)
- `days_since_pledge`: Number of days since pledge creation
- `months_elapsed`: Number of complete months elapsed
- `first_month_interest`: Interest amount for the first month
- `additional_interest`: Interest accumulated beyond first month
- `remaining_principal`: Outstanding principal amount
- `remaining_interest`: Outstanding interest amount
- `scheme_name`: Name of the interest scheme
- `monthly_interest_rate`: Monthly interest rate percentage

## Interest Calculation Logic

The API implements sophisticated interest calculation rules:

### Rules:
1. **First Month Interest**: Always mandatory (collected at pledge creation)
2. **Additional Interest**: Only applies after 30 days from pledge start
3. **Month-wise Calculation**: Based on actual elapsed time
4. **Partial Month Rules**:
   - ≤ 15 days = 50% of monthly interest
   - \> 15 days = Full monthly interest

### Calculation Example:
```javascript
// For a pledge created 75 days ago with ₹2,500 first month interest:
// - First 30 days: ₹2,500 (mandatory)
// - Days 31-60: ₹2,500 (full month)
// - Days 61-75: ₹2,500 (>15 days, so full month)
// Total Interest Due: ₹7,500
```

## Usage Examples

### Example 1: Get Customer Pending Pledges
```bash
curl -X GET "http://localhost:8000/customers/1/pending-pledges" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Example 2: Using in Frontend
```javascript
const fetchCustomerPendingPledges = async (customerId) => {
  const response = await fetch(`/customers/${customerId}/pending-pledges`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  const data = await response.json();
  return data;
};

// Usage
fetchCustomerPendingPledges(1).then(data => {
  console.log(`Customer: ${data.customer_name}`);
  console.log(`Total Outstanding: ₹${data.total_outstanding}`);
  
  data.pledges.forEach(pledge => {
    console.log(`Pledge ${pledge.pledge_no}: ₹${pledge.current_outstanding}`);
  });
});
```

## Error Responses

### 404 - Customer Not Found
```json
{
  "detail": "Customer not found"
}
```

### 401 - Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 - Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

## Business Use Cases

1. **Payment Collection**: Show all pending amounts before accepting payment
2. **Customer Statement**: Generate comprehensive account statement
3. **Settlement Planning**: Plan partial or full settlement across multiple pledges
4. **Interest Tracking**: Monitor interest accumulation across time
5. **Financial Reporting**: Aggregate outstanding amounts for reporting

## Next Features (Coming Soon)

1. **Multiple Pledge Payment**: Single payment across multiple pledges ✅ **COMPLETED**
2. **Payment Distribution Logic**: Smart allocation of payments ✅ **COMPLETED**
3. **Partial Settlement**: Handle partial payments with priority rules ✅ **COMPLETED**
4. **Payment Plans**: Create structured payment schedules

## 2. Multiple Pledge Payment API ✅ NEW!

### Endpoint
```
POST /customers/{customer_id}/multiple-pledge-payment
```

### Description
Create a single payment that covers multiple pledges with automatic financial transactions. This generates one receipt for multiple pledges and handles all accounting automatically.

### Request Model: `MultiPledgePaymentRequest`

```json
{
  "customer_id": 1,
  "total_payment_amount": 15000.0,
  "payment_method": "cash",
  "bank_reference": "TXN123456789",
  "payment_date": "2024-10-14",
  "pledge_payments": [
    {
      "pledge_id": 101,
      "payment_amount": 7500.0,
      "payment_type": "partial_principal",
      "interest_amount": 2500.0,
      "principal_amount": 5000.0,
      "remarks": "Partial payment for gold pledge"
    },
    {
      "pledge_id": 102,
      "payment_amount": 7500.0,
      "payment_type": "interest",
      "interest_amount": 7500.0,
      "principal_amount": 0.0,
      "remarks": "Interest payment only"
    }
  ],
  "general_remarks": "Monthly payment collection",
  "receipt_no": "MPR20241014001"
}
```

### Response Model: `MultiPledgePaymentResponse`

```json
{
  "payment_id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_id": 1,
  "customer_name": "Rajesh Kumar",
  "total_amount_paid": 15000.0,
  "payment_date": "2024-10-14",
  "payment_method": "cash",
  "receipt_no": "MPR20241014001",
  "master_voucher_no": "MP20241014123456",
  "pledge_results": [
    {
      "pledge_id": 101,
      "pledge_no": "PLG001",
      "payment_amount": 7500.0,
      "interest_paid": 2500.0,
      "principal_paid": 5000.0,
      "remaining_balance": 42500.0,
      "payment_status": "partial",
      "voucher_no": "MP20241014123456"
    },
    {
      "pledge_id": 102,
      "pledge_no": "PLG002", 
      "payment_amount": 7500.0,
      "interest_paid": 7500.0,
      "principal_paid": 0.0,
      "remaining_balance": 50000.0,
      "payment_status": "interest_only",
      "voucher_no": "MP20241014123456"
    }
  ],
  "accounting_entries": [
    "Pledge PLG001: Dr.Cash ₹7,500, Cr.Customer A/c",
    "Pledge PLG002: Dr.Cash ₹7,500, Cr.Customer A/c"
  ],
  "message": "Successfully processed payment of ₹15,000 across 2 pledges"
}
```

### Key Features

1. **Single Receipt**: One receipt number for multiple pledges
2. **Automatic Accounting**: Complete double-entry bookkeeping
3. **Payment Distribution**: Flexible allocation across pledges
4. **Status Updates**: Automatic pledge status updates when fully paid
5. **Transaction Safety**: All-or-nothing transaction processing

### Request Fields

#### Main Payment Info:
- `customer_id`: Customer identifier
- `total_payment_amount`: Total amount being paid
- `payment_method`: cash, bank_transfer, cheque, upi
- `bank_reference`: Reference for non-cash payments
- `payment_date`: Payment date (defaults to today)
- `general_remarks`: Overall payment notes
- `receipt_no`: Custom receipt number (auto-generated if not provided)

#### Per-Pledge Breakdown (`pledge_payments`):
- `pledge_id`: Specific pledge identifier
- `payment_amount`: Amount allocated to this pledge
- `payment_type`: interest, principal, partial_principal, full_settlement
- `interest_amount`: Interest portion of payment
- `principal_amount`: Principal portion of payment
- `discount_amount`: Discount given on this pledge (optional, default: 0.0)
- `penalty_amount`: Penalty charged on this pledge (optional, default: 0.0)
- `discount_reason`: Reason for discount (required if discount_amount > 0)
- `penalty_reason`: Reason for penalty (required if penalty_amount > 0)
- `remarks`: Pledge-specific notes

#### Overall Discount/Penalty Options:
- `total_discount_amount`: Additional overall discount (optional, default: 0.0)
- `total_penalty_amount`: Additional overall penalty (optional, default: 0.0)
- `discount_reason`: Overall discount reason
- `penalty_reason`: Overall penalty reason
- `approve_discount`: Manager approval for discounts (required if total discount > 0)
- `approve_penalty`: Manager approval for penalties (required if total penalty > 0)

### Response Fields

#### Payment Summary:
- `payment_id`: Unique payment identifier (UUID)
- `customer_name`: Customer's full name
- `total_amount_paid`: Total amount processed
- `master_voucher_no`: Main accounting voucher number
- `receipt_no`: Final receipt number used

#### Per-Pledge Results (`pledge_results`):
- `discount_amount`: Discount applied to this pledge
- `penalty_amount`: Penalty charged on this pledge
- `net_payment_amount`: Actual payment amount after discount/penalty (payment_amount + penalty - discount)
- `remaining_balance`: Outstanding amount after payment
- `payment_status`: partial, full_settlement, interest_only
- `voucher_no`: Accounting voucher reference

#### Enhanced Payment Summary:
- `total_discount_given`: Total discount amount across all pledges
- `total_penalty_charged`: Total penalty amount across all pledges  
- `net_amount`: Final amount after all discounts and penalties (total_amount_paid + penalty - discount)

### Automatic Features

1. **Financial Transactions**:
   - Debit: Cash in Hand (Asset increases)
   - Credit: Customer Pledge Account (Liability decreases)
   - Individual ledger entries per pledge

2. **Status Management**:
   - Auto-close pledges when fully paid
   - Update pledge timestamps
   - Maintain payment history

3. **Validation**:
   - Verify customer ownership of pledges
   - Ensure pledges are active
   - Validate payment amount consistency
   - Check total amount matches sum of pledge payments

### Usage Examples

#### Example 1: Mixed Payment (Interest + Principal)
```bash
curl -X POST "http://localhost:8000/customers/1/multiple-pledge-payment" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "total_payment_amount": 12000.0,
    "payment_method": "cash",
    "pledge_payments": [
      {
        "pledge_id": 101,
        "payment_amount": 5000.0,
        "payment_type": "interest",
        "interest_amount": 5000.0,
        "principal_amount": 0.0
      },
      {
        "pledge_id": 102,
        "payment_amount": 7000.0,
        "payment_type": "partial_principal", 
        "interest_amount": 2000.0,
        "principal_amount": 5000.0
      }
    ]
  }'
```

#### Example 2: Full Settlement of Multiple Pledges
```bash
curl -X POST "http://localhost:8000/customers/1/multiple-pledge-payment" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "total_payment_amount": 125000.0,
    "payment_method": "bank_transfer",
    "bank_reference": "NEFT123456789",
    "pledge_payments": [
      {
        "pledge_id": 101,
        "payment_amount": 55000.0,
        "payment_type": "full_settlement",
        "interest_amount": 5000.0,
        "principal_amount": 50000.0
      },
      {
        "pledge_id": 102,
        "payment_amount": 70000.0,
        "payment_type": "full_settlement",
        "interest_amount": 7500.0,
        "principal_amount": 62500.0
      }
    ]
  }'
```

### Error Responses

#### 400 - Validation Errors
```json
{
  "detail": "Total payment amount (15000.0) doesn't match sum of pledge payments (14500.0)"
}
```

```json
{
  "detail": "Some pledges not found or not active: {103, 104}"
}
```

#### 404 - Customer Not Found
```json
{
  "detail": "Customer not found"
}
```

## Discount and Penalty Features ✅ NEW!

### Enhanced Payment Processing
The multiple pledge payment API now supports advanced discount and penalty management with proper authorization controls.

### Example 1: Payment with Customer Discount

```json
{
  "customer_id": 1,
  "total_payment_amount": 5000.0,
  "payment_method": "cash",
  "pledge_payments": [
    {
      "pledge_id": 101,
      "payment_amount": 3000.0,
      "payment_type": "partial_principal",
      "interest_amount": 1000.0,
      "principal_amount": 2000.0,
      "discount_amount": 100.0,
      "discount_reason": "Good customer discount",
      "penalty_amount": 0.0
    },
    {
      "pledge_id": 102,
      "payment_amount": 2000.0,
      "payment_type": "interest",
      "interest_amount": 2000.0,
      "principal_amount": 0.0,
      "discount_amount": 50.0,
      "discount_reason": "Early payment discount",
      "penalty_amount": 0.0
    }
  ],
  "total_discount_amount": 25.0,
  "discount_reason": "Customer loyalty program",
  "approve_discount": true,
  "approve_penalty": false
}
```

### Example 2: Payment with Late Fee Penalty

```json
{
  "customer_id": 1,
  "total_payment_amount": 3000.0,
  "payment_method": "bank_transfer",
  "bank_reference": "TXN987654321",
  "pledge_payments": [
    {
      "pledge_id": 103,
      "payment_amount": 3000.0,
      "payment_type": "full_settlement",
      "interest_amount": 1500.0,
      "principal_amount": 1500.0,
      "discount_amount": 0.0,
      "penalty_amount": 200.0,
      "penalty_reason": "Late payment penalty"
    }
  ],
  "total_penalty_amount": 50.0,
  "penalty_reason": "Processing delay penalty", 
  "approve_discount": false,
  "approve_penalty": true
}
```

### Example 3: Mixed Discount and Penalty

```json
{
  "customer_id": 1,
  "total_payment_amount": 4000.0,
  "payment_method": "cash",
  "pledge_payments": [
    {
      "pledge_id": 104,
      "payment_amount": 2500.0,
      "payment_type": "partial_principal",
      "interest_amount": 1000.0,
      "principal_amount": 1500.0,
      "discount_amount": 75.0,
      "discount_reason": "Volume discount",
      "penalty_amount": 25.0,
      "penalty_reason": "Processing fee"
    },
    {
      "pledge_id": 105,
      "payment_amount": 1500.0,
      "payment_type": "interest",
      "interest_amount": 1500.0,
      "principal_amount": 0.0,
      "discount_amount": 25.0,
      "discount_reason": "Prompt payment discount",
      "penalty_amount": 0.0
    }
  ],
  "total_discount_amount": 50.0,
  "total_penalty_amount": 30.0,
  "discount_reason": "Overall customer discount",
  "penalty_reason": "Overall processing penalty",
  "approve_discount": true,
  "approve_penalty": true
}
```

### Enhanced Response with Discount/Penalty

```json
{
  "payment_id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_id": 1,
  "customer_name": "Rajesh Kumar",
  "total_amount_paid": 4000.0,
  "total_discount_given": 150.0,
  "total_penalty_charged": 55.0,
  "net_amount": 3905.0,
  "payment_date": "2024-10-21",
  "payment_method": "cash",
  "receipt_no": "MPR20241021001",
  "master_voucher_no": "MP20241021123456",
  "pledge_results": [
    {
      "pledge_id": 104,
      "pledge_no": "PLG004",
      "payment_amount": 2500.0,
      "interest_paid": 1000.0,
      "principal_paid": 1500.0,
      "discount_amount": 75.0,
      "penalty_amount": 25.0,
      "net_payment_amount": 2450.0,
      "remaining_balance": 47500.0,
      "payment_status": "partial",
      "voucher_no": "MP20241021123456"
    },
    {
      "pledge_id": 105,
      "pledge_no": "PLG005",
      "payment_amount": 1500.0,
      "interest_paid": 1500.0,
      "principal_paid": 0.0,
      "discount_amount": 25.0,
      "penalty_amount": 0.0,
      "net_payment_amount": 1475.0,
      "remaining_balance": 50000.0,
      "payment_status": "interest_only",
      "voucher_no": "MP20241021123456"
    }
  ],
  "accounting_entries": [
    "Pledge PLG004: Dr.Cash ₹2450.0, Cr.Customer A/c",
    "Pledge PLG005: Dr.Cash ₹1475.0, Cr.Customer A/c"
  ],
  "message": "Successfully processed payment of ₹4000.0 across 2 pledges. Net amount: ₹3905.00 (Discount: ₹150.00, Penalty: ₹55.00)"
}
```

### Validation Rules for Discount/Penalty

#### Authorization Requirements:
- **Discounts**: Require `approve_discount: true` and valid reason
- **Penalties**: Require `approve_penalty: true` and valid reason
- **Manager Override**: Both require administrative approval

#### Error Examples:

**Unauthorized Discount:**
```json
{
  "detail": "Discount of ₹175.00 requires manager approval. Set approve_discount=true"
}
```

**Missing Discount Reason:**
```json
{
  "detail": "Discount reason is required when applying discounts"
}
```

**Unauthorized Penalty:**
```json
{
  "detail": "Penalty of ₹85.00 requires manager approval. Set approve_penalty=true"
}
```

### Business Use Cases for Discount/Penalty

1. **Customer Loyalty Discounts**: Reward long-term customers
2. **Early Payment Incentives**: Encourage prompt payments
3. **Volume Discounts**: Multi-pledge payment benefits
4. **Late Fee Management**: Charge penalties for overdue payments
5. **Processing Fees**: Administrative charges
6. **Settlement Negotiations**: Flexible payment terms
7. **Promotional Offers**: Marketing-driven discounts
8. **Risk Management**: Penalty-based deterrents
```

### Business Benefits

1. **Operational Efficiency**: Single transaction for multiple pledges
2. **Customer Experience**: One receipt for all payments
3. **Accounting Accuracy**: Automatic double-entry bookkeeping
4. **Audit Trail**: Complete transaction history with voucher numbers
5. **Flexibility**: Custom payment allocation per pledge

## Related APIs

- `POST /pledge-payments` - Single pledge payment
- `GET /customers/{id}/pledges` - All customer pledges (including closed)
- `GET /pledges/{id}/payments` - Payment history for specific pledge
- `POST /pledges/{id}/settlement` - Full pledge settlement

---

*This API is part of the PawnSoft system's comprehensive pledge management functionality.*
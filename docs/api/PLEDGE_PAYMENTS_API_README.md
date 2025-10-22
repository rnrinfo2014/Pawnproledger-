# Pledge Payment API Documentation

## Overview

The Pledge Payment API provides comprehensive functionality for managing payments against pledges in the PawnPro system. This API supports various payment types, automatic balance calculations, payment tracking, and detailed reporting.

## Features

- ✅ **Multiple Payment Types**: Interest, principal, partial redemption, full redemption
- ✅ **Automatic Balance Calculation**: Real-time remaining balance updates
- ✅ **Payment Methods**: Cash, bank transfer, cheque, card payments
- ✅ **Receipt Generation**: Automatic receipt number generation
- ✅ **Comprehensive Filtering**: Filter by pledge, date range, payment type, method
- ✅ **Payment Summary**: Detailed payment analytics and summaries
- ✅ **Transaction Safety**: All operations are database transaction-safe
- ✅ **Company Isolation**: Multi-tenant support with proper data isolation

## Database Schema

### PledgePayment Table Structure

```sql
CREATE TABLE pledge_payments (
    payment_id SERIAL PRIMARY KEY,
    pledge_id INTEGER NOT NULL REFERENCES pledges(pledge_id) ON DELETE CASCADE,
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    payment_type VARCHAR(20) NOT NULL,  -- interest, principal, partial_redeem, full_redeem
    amount FLOAT NOT NULL,
    interest_amount FLOAT DEFAULT 0.0,
    principal_amount FLOAT DEFAULT 0.0,
    penalty_amount FLOAT DEFAULT 0.0,
    balance_amount FLOAT NOT NULL,      -- Remaining balance after this payment
    payment_method VARCHAR(20) DEFAULT 'cash',  -- cash, bank_transfer, cheque, etc.
    bank_reference VARCHAR(100),
    receipt_no VARCHAR(50),
    remarks TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER NOT NULL REFERENCES users(id),
    company_id INTEGER NOT NULL REFERENCES companies(id)
);

-- Indexes for performance
CREATE INDEX idx_pledge_payments_pledge_id ON pledge_payments (pledge_id);
CREATE INDEX idx_pledge_payments_date ON pledge_payments (payment_date);
CREATE INDEX idx_pledge_payments_company_id ON pledge_payments (company_id);
CREATE INDEX idx_pledge_payments_type ON pledge_payments (payment_type);
CREATE INDEX idx_pledge_payments_pledge_company ON pledge_payments (pledge_id, company_id);
```

## API Endpoints

### 1. Create Payment

**POST** `/pledge-payments/`

Create a new payment against a pledge.

#### Request Body

```json
{
    "pledge_id": 1,
    "payment_date": "2024-01-15",  // Optional, defaults to current date
    "payment_type": "interest",    // Required: interest, principal, partial_redeem, full_redeem
    "amount": 1000.0,             // Required: payment amount
    "interest_amount": 1000.0,    // Optional: interest portion
    "principal_amount": 0.0,      // Optional: principal portion
    "penalty_amount": 0.0,        // Optional: penalty amount
    "payment_method": "cash",     // Optional: cash, bank_transfer, cheque, card
    "bank_reference": "TXN123",   // Optional: for non-cash payments
    "receipt_no": "RCPT001",      // Optional: auto-generated if not provided
    "remarks": "Monthly interest payment"
}
```

#### Response

```json
{
    "payment_id": 1,
    "pledge_id": 1,
    "payment_date": "2024-01-15",
    "payment_type": "interest",
    "amount": 1000.0,
    "interest_amount": 1000.0,
    "principal_amount": 0.0,
    "penalty_amount": 0.0,
    "balance_amount": 49000.0,
    "payment_method": "cash",
    "bank_reference": "TXN123",
    "receipt_no": "RCPT001",
    "remarks": "Monthly interest payment",
    "created_at": "2024-01-15T10:30:00Z",
    "created_by": 1,
    "company_id": 1
}
```

#### Business Logic

- Validates pledge exists and belongs to user's company
- Checks pledge status (must be 'active' or 'partial_paid')
- Prevents overpayment (amount cannot exceed remaining balance)
- Automatically updates pledge status based on balance:
  - `redeemed`: when balance reaches zero
  - `partial_paid`: when some payment is made
  - `active`: when no payments exist
- Auto-generates receipt number if not provided

### 2. Get Payments (List with Filters)

**GET** `/pledge-payments/`

Retrieve payments with optional filtering and pagination.

#### Query Parameters

- `pledge_id` (int): Filter by specific pledge
- `payment_type` (string): Filter by payment type
- `payment_method` (string): Filter by payment method
- `from_date` (date): Filter payments from date (YYYY-MM-DD)
- `to_date` (date): Filter payments to date (YYYY-MM-DD)
- `skip` (int): Pagination offset (default: 0)
- `limit` (int): Number of records (default: 100)

#### Example Requests

```bash
# Get all payments
GET /pledge-payments/

# Filter by pledge
GET /pledge-payments/?pledge_id=1

# Filter by date range
GET /pledge-payments/?from_date=2024-01-01&to_date=2024-01-31

# Filter by payment type
GET /pledge-payments/?payment_type=interest

# Combined filters with pagination
GET /pledge-payments/?pledge_id=1&payment_type=interest&skip=0&limit=10
```

#### Response

```json
[
    {
        "payment_id": 1,
        "pledge_id": 1,
        "payment_date": "2024-01-15",
        "payment_type": "interest",
        "amount": 1000.0,
        "interest_amount": 1000.0,
        "principal_amount": 0.0,
        "penalty_amount": 0.0,
        "balance_amount": 49000.0,
        "payment_method": "cash",
        "bank_reference": null,
        "receipt_no": "RCPT-1-20240115103000",
        "remarks": "Monthly interest payment",
        "created_at": "2024-01-15T10:30:00Z",
        "created_by": 1,
        "company_id": 1,
        "pledge_no": "PLG-001-2024",
        "customer_name": "John Doe",
        "created_by_username": "admin"
    }
]
```

### 3. Get Payment by ID

**GET** `/pledge-payments/{payment_id}`

Retrieve specific payment details with extended information.

#### Response

```json
{
    "payment_id": 1,
    "pledge_id": 1,
    "payment_date": "2024-01-15",
    "payment_type": "interest",
    "amount": 1000.0,
    "interest_amount": 1000.0,
    "principal_amount": 0.0,
    "penalty_amount": 0.0,
    "balance_amount": 49000.0,
    "payment_method": "cash",
    "bank_reference": null,
    "receipt_no": "RCPT-1-20240115103000",
    "remarks": "Monthly interest payment",
    "created_at": "2024-01-15T10:30:00Z",
    "created_by": 1,
    "company_id": 1,
    "pledge_no": "PLG-001-2024",
    "customer_name": "John Doe",
    "created_by_username": "admin"
}
```

### 4. Update Payment

**PUT** `/pledge-payments/{payment_id}`

Update an existing payment. Only provided fields will be updated.

#### Request Body

```json
{
    "amount": 1200.0,
    "remarks": "Updated payment amount",
    "payment_method": "bank_transfer",
    "bank_reference": "TXN456"
}
```

#### Response

```json
{
    "payment_id": 1,
    "pledge_id": 1,
    "payment_date": "2024-01-15",
    "payment_type": "interest",
    "amount": 1200.0,
    "interest_amount": 1000.0,
    "principal_amount": 0.0,
    "penalty_amount": 0.0,
    "balance_amount": 48800.0,
    "payment_method": "bank_transfer",
    "bank_reference": "TXN456",
    "receipt_no": "RCPT-1-20240115103000",
    "remarks": "Updated payment amount",
    "created_at": "2024-01-15T10:30:00Z",
    "created_by": 1,
    "company_id": 1
}
```

#### Business Logic

- Recalculates balance if amount is updated
- Prevents overpayment
- Updates pledge status if necessary
- Maintains transaction integrity

### 5. Delete Payment

**DELETE** `/pledge-payments/{payment_id}`

Delete a payment and recalculate pledge status.

#### Response

```json
{
    "message": "Payment deleted successfully"
}
```

#### Business Logic

- Deletes the payment record
- Recalculates pledge status based on remaining payments
- Updates pledge status accordingly
- Maintains referential integrity

### 6. Get Payments by Pledge

**GET** `/pledges/{pledge_id}/payments`

Retrieve all payments for a specific pledge.

#### Response

```json
[
    {
        "payment_id": 1,
        "pledge_id": 1,
        "payment_date": "2024-01-15",
        "payment_type": "interest",
        "amount": 1000.0,
        "balance_amount": 49000.0,
        "payment_method": "cash",
        "receipt_no": "RCPT-1-20240115103000",
        "created_at": "2024-01-15T10:30:00Z",
        "created_by": 1,
        "company_id": 1
    }
]
```

### 7. Get Pledge Payment Summary

**GET** `/pledges/{pledge_id}/payment-summary`

Get comprehensive payment analytics for a pledge.

#### Response

```json
{
    "pledge_id": 1,
    "pledge_no": "PLG-001-2024",
    "final_amount": 50000.0,
    "total_payments": 5,
    "total_amount_paid": 15000.0,
    "remaining_balance": 35000.0,
    "total_interest_paid": 12000.0,
    "total_principal_paid": 3000.0,
    "total_penalty_paid": 0.0,
    "payment_percentage": 30.0,
    "status": "partial_paid"
}
```

## Payment Types

### 1. Interest Payment
- **Type**: `interest`
- **Purpose**: Regular interest payments
- **Impact**: Does not change principal balance
- **Status**: Maintains current pledge status

### 2. Principal Payment
- **Type**: `principal`
- **Purpose**: Reduces principal amount
- **Impact**: Directly reduces loan balance
- **Status**: May change to 'redeemed' if balance reaches zero

### 3. Partial Redemption
- **Type**: `partial_redeem`
- **Purpose**: Partial closure with mixed interest/principal
- **Impact**: Reduces total balance
- **Status**: Changes to 'partial_paid' or 'redeemed'

### 4. Full Redemption
- **Type**: `full_redeem`
- **Purpose**: Complete closure of pledge
- **Impact**: Should bring balance to zero
- **Status**: Changes to 'redeemed'

## Payment Methods

- **cash**: Cash payments (default)
- **bank_transfer**: Bank transfer payments
- **cheque**: Cheque payments
- **card**: Card payments
- **other**: Other payment methods

For non-cash payments, use the `bank_reference` field to store transaction references.

## Error Handling

### Common Error Responses

#### 404 - Pledge Not Found
```json
{
    "detail": "Pledge not found"
}
```

#### 400 - Excessive Payment
```json
{
    "detail": "Payment amount (15000.0) exceeds remaining balance (10000.0)"
}
```

#### 400 - Invalid Pledge Status
```json
{
    "detail": "Cannot make payment for pledge with status: redeemed"
}
```

#### 422 - Validation Error
```json
{
    "detail": [
        {
            "loc": ["body", "amount"],
            "msg": "ensure this value is greater than 0",
            "type": "value_error.number.not_gt"
        }
    ]
}
```

## Migration Instructions

### 1. Run Migration Script

```bash
cd PawnProApi
python migrate_pledge_payments.py
```

This will:
- Create the `pledge_payments` table
- Add necessary indexes
- Verify table structure

### 2. Update Database Models

The migration automatically adds the new model relationships:
- `PledgePayment` model with all relationships
- Updated `Pledge`, `Company`, and `User` models with payment relationships

### 3. API Integration

All endpoints are automatically available after migration:
- No additional configuration required
- Uses existing authentication system
- Follows company isolation patterns

## Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest requests

# Run payment API tests
python test_payment_api.py

# Or use pytest
pytest test_payment_api.py -v
```

### Test Coverage

The test suite covers:
- ✅ Payment creation with validation
- ✅ Payment listing with filters
- ✅ Payment updates and balance recalculation
- ✅ Payment deletion and status updates
- ✅ Payment summary and analytics
- ✅ Error handling and edge cases
- ✅ Authentication and authorization
- ✅ Business logic validation

## Usage Examples

### Example 1: Monthly Interest Payment

```python
import requests

# Create monthly interest payment
payment_data = {
    "pledge_id": 1,
    "payment_type": "interest",
    "amount": 2000.0,
    "interest_amount": 2000.0,
    "payment_method": "cash",
    "remarks": "January 2024 interest payment"
}

response = requests.post(
    "http://localhost:8000/pledge-payments/",
    json=payment_data,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

payment = response.json()
print(f"Payment created: {payment['receipt_no']}")
```

### Example 2: Partial Redemption

```python
# Partial redemption payment
payment_data = {
    "pledge_id": 1,
    "payment_type": "partial_redeem",
    "amount": 15000.0,
    "interest_amount": 5000.0,
    "principal_amount": 10000.0,
    "payment_method": "bank_transfer",
    "bank_reference": "TXN789456123",
    "remarks": "Partial redemption - 10k principal + 5k interest"
}

response = requests.post(
    "http://localhost:8000/pledge-payments/",
    json=payment_data,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

### Example 3: Payment Summary Report

```python
# Get payment summary for reporting
pledge_id = 1
response = requests.get(
    f"http://localhost:8000/pledges/{pledge_id}/payment-summary",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

summary = response.json()
print(f"Pledge: {summary['pledge_no']}")
print(f"Total Paid: ${summary['total_amount_paid']}")
print(f"Remaining: ${summary['remaining_balance']}")
print(f"Progress: {summary['payment_percentage']}%")
```

### Example 4: Payment History

```python
# Get payment history with filters
response = requests.get(
    "http://localhost:8000/pledge-payments/?pledge_id=1&from_date=2024-01-01",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

payments = response.json()
for payment in payments:
    print(f"{payment['payment_date']}: ${payment['amount']} ({payment['payment_type']})")
```

## Best Practices

### 1. Payment Validation
- Always validate payment amounts against remaining balance
- Check pledge status before accepting payments
- Use appropriate payment types for different scenarios

### 2. Transaction Safety
- All payment operations are wrapped in database transactions
- Failed operations are automatically rolled back
- Pledge status is always kept consistent

### 3. Receipt Management
- Let the system auto-generate receipt numbers for consistency
- Store bank references for non-cash payments
- Include meaningful remarks for audit trails

### 4. Performance Optimization
- Use pagination for large payment lists
- Apply date range filters for better performance
- Leverage database indexes for common queries

### 5. Error Handling
- Handle overpayment scenarios gracefully
- Provide clear error messages for validation failures
- Log payment operations for audit purposes

## Security Considerations

- ✅ JWT authentication required for all endpoints
- ✅ Company-based data isolation
- ✅ Role-based access control integration
- ✅ SQL injection prevention through ORM
- ✅ Input validation and sanitization
- ✅ Audit trail through created_by tracking

## Performance Metrics

- **Database Indexes**: 5 optimized indexes for common queries
- **Query Performance**: Sub-second response for payment lists < 10,000 records
- **Concurrent Users**: Supports multiple simultaneous payment operations
- **Data Integrity**: ACID transaction compliance for all operations

---

**Version**: 1.0  
**Last Updated**: January 2024  
**API Compatibility**: PawnPro v1.0+

For support or questions, please refer to the main PawnPro documentation or contact the development team.
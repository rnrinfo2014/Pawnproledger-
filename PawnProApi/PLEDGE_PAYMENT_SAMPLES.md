# Pledge Payment API - Comprehensive Samples

## Overview
This document provides comprehensive examples for the Pledge Payment API, including various payment scenarios, request/response formats, and practical use cases.

## API Base URL
```
http://localhost:8000
```

## Authentication
All requests require a Bearer token in the Authorization header:
```
Authorization: Bearer {your_jwt_token}
```

---

## 1. CREATE PLEDGE PAYMENT

### Endpoint
```
POST /pledge-payments/
```

### Sample Scenarios

#### Scenario 1: Interest Payment (Monthly Interest)
```json
{
  "pledge_id": 1,
  "payment_date": "2025-09-16",
  "payment_type": "interest",
  "amount": 1800.00,
  "interest_amount": 1800.00,
  "principal_amount": 0.00,
  "penalty_amount": 0.00,
  "payment_method": "cash",
  "receipt_no": "RCPT-001-001",
  "remarks": "Monthly interest payment for September 2025"
}
```

**Response:**
```json
{
  "payment_id": 101,
  "pledge_id": 1,
  "payment_date": "2025-09-16",
  "payment_type": "interest",
  "amount": 1800.00,
  "interest_amount": 1800.00,
  "principal_amount": 0.00,
  "penalty_amount": 0.00,
  "balance_amount": 90000.00,
  "payment_method": "cash",
  "bank_reference": null,
  "receipt_no": "RCPT-001-001",
  "remarks": "Monthly interest payment for September 2025",
  "created_at": "2025-09-16T10:30:00",
  "created_by": 1,
  "company_id": 1
}
```

#### Scenario 2: Principal Payment (Partial Redemption)
```json
{
  "pledge_id": 1,
  "payment_date": "2025-09-16",
  "payment_type": "principal",
  "amount": 25000.00,
  "interest_amount": 0.00,
  "principal_amount": 25000.00,
  "penalty_amount": 0.00,
  "payment_method": "bank_transfer",
  "bank_reference": "TXN123456789",
  "receipt_no": "RCPT-001-002",
  "remarks": "Partial principal payment"
}
```

**Response:**
```json
{
  "payment_id": 102,
  "pledge_id": 1,
  "payment_date": "2025-09-16",
  "payment_type": "principal",
  "amount": 25000.00,
  "interest_amount": 0.00,
  "principal_amount": 25000.00,
  "penalty_amount": 0.00,
  "balance_amount": 65000.00,
  "payment_method": "bank_transfer",
  "bank_reference": "TXN123456789",
  "receipt_no": "RCPT-001-002",
  "remarks": "Partial principal payment",
  "created_at": "2025-09-16T11:45:00",
  "created_by": 1,
  "company_id": 1
}
```

#### Scenario 3: Mixed Payment (Interest + Principal)
```json
{
  "pledge_id": 1,
  "payment_date": "2025-09-16",
  "payment_type": "partial_redeem",
  "amount": 10000.00,
  "interest_amount": 1800.00,
  "principal_amount": 8200.00,
  "penalty_amount": 0.00,
  "payment_method": "cash",
  "receipt_no": "RCPT-001-003",
  "remarks": "Combined interest and principal payment"
}
```

**Response:**
```json
{
  "payment_id": 103,
  "pledge_id": 1,
  "payment_date": "2025-09-16",
  "payment_type": "partial_redeem",
  "amount": 10000.00,
  "interest_amount": 1800.00,
  "principal_amount": 8200.00,
  "penalty_amount": 0.00,
  "balance_amount": 81800.00,
  "payment_method": "cash",
  "bank_reference": null,
  "receipt_no": "RCPT-001-003",
  "remarks": "Combined interest and principal payment",
  "created_at": "2025-09-16T14:20:00",
  "created_by": 1,
  "company_id": 1
}
```

#### Scenario 4: Full Redemption
```json
{
  "pledge_id": 1,
  "payment_date": "2025-09-16",
  "payment_type": "full_redeem",
  "amount": 91800.00,
  "interest_amount": 1800.00,
  "principal_amount": 90000.00,
  "penalty_amount": 0.00,
  "payment_method": "bank_transfer",
  "bank_reference": "TXN987654321",
  "receipt_no": "RCPT-001-004",
  "remarks": "Full pledge redemption"
}
```

**Response:**
```json
{
  "payment_id": 104,
  "pledge_id": 1,
  "payment_date": "2025-09-16",
  "payment_type": "full_redeem",
  "amount": 91800.00,
  "interest_amount": 1800.00,
  "principal_amount": 90000.00,
  "penalty_amount": 0.00,
  "balance_amount": 0.00,
  "payment_method": "bank_transfer",
  "bank_reference": "TXN987654321",
  "receipt_no": "RCPT-001-004",
  "remarks": "Full pledge redemption",
  "created_at": "2025-09-16T16:30:00",
  "created_by": 1,
  "company_id": 1
}
```

#### Scenario 5: Payment with Penalty
```json
{
  "pledge_id": 2,
  "payment_date": "2025-09-16",
  "payment_type": "interest",
  "amount": 2300.00,
  "interest_amount": 1800.00,
  "principal_amount": 0.00,
  "penalty_amount": 500.00,
  "payment_method": "cheque",
  "bank_reference": "CHQ789012345",
  "receipt_no": "RCPT-001-005",
  "remarks": "Late payment with penalty charges"
}
```

---

## 2. GET PLEDGE PAYMENTS

### Endpoint
```
GET /pledge-payments/
```

### Query Parameters
- `pledge_id` (optional): Filter by specific pledge
- `payment_type` (optional): Filter by payment type
- `payment_method` (optional): Filter by payment method
- `from_date` (optional): Filter from date (YYYY-MM-DD)
- `to_date` (optional): Filter to date (YYYY-MM-DD)
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Pagination limit (default: 100)

### Sample Requests

#### Get All Payments
```
GET /pledge-payments/
```

#### Get Payments for Specific Pledge
```
GET /pledge-payments/?pledge_id=1
```

#### Get Interest Payments Only
```
GET /pledge-payments/?payment_type=interest
```

#### Get Payments by Date Range
```
GET /pledge-payments/?from_date=2025-09-01&to_date=2025-09-30
```

#### Get Cash Payments Only
```
GET /pledge-payments/?payment_method=cash
```

### Sample Response
```json
[
  {
    "payment_id": 101,
    "pledge_id": 1,
    "payment_date": "2025-09-16",
    "payment_type": "interest",
    "amount": 1800.00,
    "interest_amount": 1800.00,
    "principal_amount": 0.00,
    "penalty_amount": 0.00,
    "balance_amount": 90000.00,
    "payment_method": "cash",
    "bank_reference": null,
    "receipt_no": "RCPT-001-001",
    "remarks": "Monthly interest payment for September 2025",
    "created_at": "2025-09-16T10:30:00",
    "created_by": 1,
    "company_id": 1,
    "pledge_no": "PLG-001",
    "customer_name": "John Doe",
    "created_by_username": "admin"
  },
  {
    "payment_id": 102,
    "pledge_id": 1,
    "payment_date": "2025-09-16",
    "payment_type": "principal",
    "amount": 25000.00,
    "interest_amount": 0.00,
    "principal_amount": 25000.00,
    "penalty_amount": 0.00,
    "balance_amount": 65000.00,
    "payment_method": "bank_transfer",
    "bank_reference": "TXN123456789",
    "receipt_no": "RCPT-001-002",
    "remarks": "Partial principal payment",
    "created_at": "2025-09-16T11:45:00",
    "created_by": 1,
    "company_id": 1,
    "pledge_no": "PLG-001",
    "customer_name": "John Doe",
    "created_by_username": "admin"
  }
]
```

---

## 3. GET SPECIFIC PLEDGE PAYMENT

### Endpoint
```
GET /pledge-payments/{payment_id}
```

### Sample Request
```
GET /pledge-payments/101
```

### Sample Response
```json
{
  "payment_id": 101,
  "pledge_id": 1,
  "payment_date": "2025-09-16",
  "payment_type": "interest",
  "amount": 1800.00,
  "interest_amount": 1800.00,
  "principal_amount": 0.00,
  "penalty_amount": 0.00,
  "balance_amount": 90000.00,
  "payment_method": "cash",
  "bank_reference": null,
  "receipt_no": "RCPT-001-001",
  "remarks": "Monthly interest payment for September 2025",
  "created_at": "2025-09-16T10:30:00",
  "created_by": 1,
  "company_id": 1,
  "pledge_no": "PLG-001",
  "customer_name": "John Doe",
  "created_by_username": "admin"
}
```

---

## 4. GET PAYMENTS BY PLEDGE

### Endpoint
```
GET /pledges/{pledge_id}/payments
```

### Sample Request
```
GET /pledges/1/payments
```

### Sample Response
```json
[
  {
    "payment_id": 101,
    "pledge_id": 1,
    "payment_date": "2025-09-16",
    "payment_type": "interest",
    "amount": 1800.00,
    "interest_amount": 1800.00,
    "principal_amount": 0.00,
    "penalty_amount": 0.00,
    "balance_amount": 90000.00,
    "payment_method": "cash",
    "receipt_no": "RCPT-001-001",
    "remarks": "Monthly interest payment",
    "created_at": "2025-09-16T10:30:00",
    "created_by": 1,
    "company_id": 1
  }
]
```

---

## 5. GET PAYMENT SUMMARY

### Endpoint
```
GET /pledges/{pledge_id}/payment-summary
```

### Sample Request
```
GET /pledges/1/payment-summary
```

### Sample Response
```json
{
  "pledge_id": 1,
  "pledge_no": "PLG-001",
  "customer_name": "John Doe",
  "loan_amount": 90000.00,
  "total_payments": 10000.00,
  "total_interest_paid": 1800.00,
  "total_principal_paid": 8200.00,
  "total_penalty_paid": 0.00,
  "remaining_balance": 81800.00,
  "payment_count": 2,
  "last_payment_date": "2025-09-16",
  "pledge_status": "partial_paid",
  "payments": [
    {
      "payment_date": "2025-09-16",
      "payment_type": "interest",
      "amount": 1800.00,
      "receipt_no": "RCPT-001-001"
    },
    {
      "payment_date": "2025-09-16", 
      "payment_type": "partial_redeem",
      "amount": 8200.00,
      "receipt_no": "RCPT-001-003"
    }
  ]
}
```

---

## 6. UPDATE PAYMENT

### Endpoint
```
PUT /pledge-payments/{payment_id}
```

### Sample Request
```json
{
  "remarks": "Updated payment remarks",
  "bank_reference": "UPDATED_TXN123456"
}
```

### Sample Response
```json
{
  "payment_id": 101,
  "pledge_id": 1,
  "payment_date": "2025-09-16",
  "payment_type": "interest",
  "amount": 1800.00,
  "interest_amount": 1800.00,
  "principal_amount": 0.00,
  "penalty_amount": 0.00,
  "balance_amount": 90000.00,
  "payment_method": "cash",
  "bank_reference": "UPDATED_TXN123456",
  "receipt_no": "RCPT-001-001",
  "remarks": "Updated payment remarks",
  "created_at": "2025-09-16T10:30:00",
  "created_by": 1,
  "company_id": 1
}
```

---

## 7. DELETE PAYMENT

### Endpoint
```
DELETE /pledge-payments/{payment_id}
```

### Sample Request
```
DELETE /pledge-payments/101
```

### Sample Response
```json
{
  "message": "Payment deleted successfully",
  "deleted_payment_id": 101,
  "updated_pledge_balance": 91800.00
}
```

---

## 8. PYTHON CLIENT EXAMPLES

### Create Payment Function
```python
import requests
from datetime import date

def create_pledge_payment(
    base_url="http://localhost:8000",
    token="your_jwt_token",
    pledge_id=1,
    payment_type="interest",
    amount=1800.00,
    interest_amount=1800.00,
    principal_amount=0.00,
    payment_method="cash",
    remarks="Monthly interest payment"
):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "pledge_id": pledge_id,
        "payment_date": str(date.today()),
        "payment_type": payment_type,
        "amount": amount,
        "interest_amount": interest_amount,
        "principal_amount": principal_amount,
        "payment_method": payment_method,
        "remarks": remarks
    }
    
    response = requests.post(
        f"{base_url}/pledge-payments/",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Usage example
payment = create_pledge_payment(
    pledge_id=1,
    payment_type="interest",
    amount=1800.00,
    interest_amount=1800.00,
    payment_method="cash",
    remarks="September 2025 interest payment"
)
print(payment)
```

### Get Payments Function
```python
def get_pledge_payments(
    base_url="http://localhost:8000",
    token="your_jwt_token",
    pledge_id=None,
    payment_type=None,
    from_date=None,
    to_date=None
):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    params = {}
    if pledge_id:
        params["pledge_id"] = pledge_id
    if payment_type:
        params["payment_type"] = payment_type
    if from_date:
        params["from_date"] = from_date
    if to_date:
        params["to_date"] = to_date
    
    response = requests.get(
        f"{base_url}/pledge-payments/",
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Usage example
payments = get_pledge_payments(
    pledge_id=1,
    payment_type="interest",
    from_date="2025-09-01",
    to_date="2025-09-30"
)
print(payments)
```

---

## 9. PAYMENT TYPES

| Type | Description | Use Case |
|------|-------------|----------|
| `interest` | Interest-only payment | Monthly interest payments |
| `principal` | Principal-only payment | Partial loan reduction |
| `partial_redeem` | Mixed payment | Interest + partial principal |
| `full_redeem` | Complete settlement | Full loan closure |

## 10. PAYMENT METHODS

| Method | Description | Bank Reference Required |
|--------|-------------|------------------------|
| `cash` | Cash payment | No |
| `bank_transfer` | Bank transfer/NEFT/RTGS | Yes |
| `cheque` | Cheque payment | Optional (cheque number) |
| `upi` | UPI payment | Optional (transaction ID) |
| `card` | Card payment | Optional (transaction ID) |

## 11. ERROR SCENARIOS

### Payment Amount Exceeds Balance
```json
{
  "detail": "Payment amount (100000.00) exceeds remaining balance (91800.00)"
}
```

### Pledge Not Found
```json
{
  "detail": "Pledge not found"
}
```

### Inactive Pledge
```json
{
  "detail": "Cannot make payment for pledge with status: redeemed"
}
```

---

**Note**: Replace `{your_jwt_token}` with actual authentication tokens and update pledge IDs, amounts, and other values according to your test data.
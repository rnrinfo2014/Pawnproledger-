# Pledge Listing API Documentation

## Overview

The Pledge Listing APIs provide comprehensive functionality for retrieving pledge information based on customers and schemes in the PawnPro system. These endpoints are designed to support various business scenarios like customer portfolio management, scheme analysis, and reporting.

## Features

- ✅ **Customer-based Pledge Listing**: Get all pledges for specific customers
- ✅ **Active Pledge Filtering**: Filter only active pledges
- ✅ **Scheme-based Filtering**: Get pledges under specific schemes
- ✅ **Comprehensive Data**: Includes principal amount, interest rates, remaining balances
- ✅ **Status Mapping**: Converts internal status to business status (ACTIVE, CLOSED, DEFAULTED)
- ✅ **Pagination Support**: Efficient handling of large datasets
- ✅ **Admin-only Access**: Secured with JWT authentication for staff/admin users
- ✅ **Company Isolation**: Multi-tenant support with proper data separation

## API Endpoints

### 1. Get Customer Active Pledges

**GET** `/customers/{customer_id}/pledges/active`

Retrieve all active pledges for a specific customer.

#### Parameters

- `customer_id` (int, required): ID of the customer
- `skip` (int, optional): Number of records to skip for pagination (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100)

#### Response Schema: PledgeOut

```json
[
    {
        "id": 1,
        "customer_id": 123,
        "scheme_id": 456,
        "principal_amount": 50000.0,
        "interest_rate": 2.5,
        "start_date": "2024-01-15",
        "maturity_date": "2024-07-15",
        "remaining_principal": 35000.0,
        "status": "ACTIVE",
        "created_at": "2024-01-15T10:30:00Z",
        "closed_at": null
    }
]
```

#### Example Request

```bash
GET /customers/123/pledges/active?skip=0&limit=10
Authorization: Bearer YOUR_JWT_TOKEN
```

#### Business Logic

- Only returns pledges with status 'active' or 'partial_paid' (both mapped to 'ACTIVE')
- Calculates remaining principal based on payment history
- Verifies customer belongs to authenticated user's company
- Results are not ordered by default (add ordering if needed)

### 2. Get All Customer Pledges

**GET** `/customers/{customer_id}/pledges`

Retrieve all pledges for a specific customer (active, closed, and defaulted).

#### Parameters

- `customer_id` (int, required): ID of the customer
- `skip` (int, optional): Number of records to skip for pagination (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100)

#### Response Schema: PledgeOut (List)

```json
[
    {
        "id": 1,
        "customer_id": 123,
        "scheme_id": 456,
        "principal_amount": 50000.0,
        "interest_rate": 2.5,
        "start_date": "2024-01-15",
        "maturity_date": "2024-07-15",
        "remaining_principal": 0.0,
        "status": "CLOSED",
        "created_at": "2024-01-15T10:30:00Z",
        "closed_at": "2024-07-10T14:20:00Z"
    },
    {
        "id": 2,
        "customer_id": 123,
        "scheme_id": 789,
        "principal_amount": 75000.0,
        "interest_rate": 3.0,
        "start_date": "2024-02-01",
        "maturity_date": "2024-08-01",
        "remaining_principal": 75000.0,
        "status": "ACTIVE",
        "created_at": "2024-02-01T09:15:00Z",
        "closed_at": null
    }
]
```

#### Example Request

```bash
GET /customers/123/pledges?skip=0&limit=20
Authorization: Bearer YOUR_JWT_TOKEN
```

#### Business Logic

- Returns pledges with all statuses
- Results ordered by created_at (newest first)
- Calculates `closed_at` timestamp for closed pledges based on latest payment
- Includes both active and historical pledge data

### 3. Get Active Pledges by Scheme

**GET** `/schemes/{scheme_id}/pledges/active`

Retrieve all active pledges under a specific scheme.

#### Parameters

- `scheme_id` (int, required): ID of the scheme
- `skip` (int, optional): Number of records to skip for pagination (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100)

#### Response Schema: PledgeOut (List)

```json
[
    {
        "id": 1,
        "customer_id": 123,
        "scheme_id": 456,
        "principal_amount": 50000.0,
        "interest_rate": 2.5,
        "start_date": "2024-01-15",
        "maturity_date": "2024-07-15",
        "remaining_principal": 35000.0,
        "status": "ACTIVE",
        "created_at": "2024-01-15T10:30:00Z",
        "closed_at": null
    },
    {
        "id": 3,
        "customer_id": 456,
        "scheme_id": 456,
        "principal_amount": 25000.0,
        "interest_rate": 2.5,
        "start_date": "2024-01-20",
        "maturity_date": "2024-07-20",
        "remaining_principal": 25000.0,
        "status": "ACTIVE",
        "created_at": "2024-01-20T11:45:00Z",
        "closed_at": null
    }
]
```

#### Example Request

```bash
GET /schemes/456/pledges/active?skip=0&limit=50
Authorization: Bearer YOUR_JWT_TOKEN
```

#### Business Logic

- Only returns active pledges under the specified scheme
- Useful for scheme performance analysis
- Results ordered by created_at (newest first)
- Verifies scheme belongs to authenticated user's company

## Data Schema Details

### PledgeOut Model

| Field | Type | Description | Source |
|-------|------|-------------|---------|
| `id` | int | Unique pledge identifier | `pledge_id` from database |
| `customer_id` | int | Customer identifier | Direct mapping |
| `scheme_id` | int | Scheme identifier | Direct mapping |
| `principal_amount` | float | Original loan amount | `total_loan_amount` |
| `interest_rate` | float | Monthly interest rate (%) | From associated scheme |
| `start_date` | date | Pledge start date | `pledge_date` |
| `maturity_date` | date | Pledge maturity date | `due_date` |
| `remaining_principal` | float | Remaining principal balance | Calculated from payments |
| `status` | string | Business status | Mapped from internal status |
| `created_at` | datetime | Creation timestamp | Direct mapping |
| `closed_at` | datetime | Closure timestamp (nullable) | Calculated for closed pledges |

### Status Mapping

Internal statuses are mapped to business-friendly statuses:

| Internal Status | Business Status | Description |
|----------------|-----------------|-------------|
| `active` | `ACTIVE` | Currently active pledge |
| `partial_paid` | `ACTIVE` | Pledge with partial payments |
| `redeemed` | `CLOSED` | Successfully redeemed pledge |
| `auctioned` | `DEFAULTED` | Defaulted and auctioned |
| Other | `ACTIVE` | Default mapping |

## Business Logic

### Remaining Principal Calculation

The `remaining_principal` is calculated as:
```
remaining_principal = original_principal - sum(principal_payments)
```

This provides real-time balance information based on payment history.

### Closed Date Calculation

For closed pledges (`status = 'CLOSED'`), the `closed_at` field is populated with the timestamp of the latest payment that closed the pledge.

### Interest Rate Source

The `interest_rate` comes from the associated scheme's `interest_rate_monthly` field, providing the monthly interest percentage.

## Authentication & Authorization

### Required Authentication

All endpoints require JWT authentication with admin/staff privileges:

```python
current_user: UserModel = Depends(get_current_admin_user)
```

### Company Isolation

All queries are automatically filtered by the authenticated user's `company_id` to ensure proper multi-tenant data separation.

## Error Handling

### Common Error Responses

#### 401 - Unauthorized
```json
{
    "detail": "Not authenticated"
}
```

#### 403 - Forbidden
```json
{
    "detail": "Not enough permissions"
}
```

#### 404 - Customer/Scheme Not Found
```json
{
    "detail": "Customer not found"
}
```

#### 422 - Validation Error
```json
{
    "detail": [
        {
            "loc": ["path", "customer_id"],
            "msg": "ensure this value is greater than 0",
            "type": "value_error.number.not_gt"
        }
    ]
}
```

## Usage Examples

### Example 1: Get Customer Portfolio

```python
import requests

# Get all pledges for a customer
headers = {"Authorization": "Bearer YOUR_JWT_TOKEN"}
response = requests.get(
    "http://localhost:8000/customers/123/pledges",
    headers=headers
)

pledges = response.json()

# Calculate total exposure
total_principal = sum(p["principal_amount"] for p in pledges)
total_remaining = sum(p["remaining_principal"] for p in pledges)
print(f"Total Principal: ${total_principal}")
print(f"Total Remaining: ${total_remaining}")
```

### Example 2: Active Pledges Report

```python
# Get active pledges for reporting
response = requests.get(
    "http://localhost:8000/customers/123/pledges/active",
    headers=headers
)

active_pledges = response.json()

for pledge in active_pledges:
    print(f"Pledge {pledge['id']}: ${pledge['remaining_principal']} remaining")
```

### Example 3: Scheme Analysis

```python
# Analyze performance of a specific scheme
response = requests.get(
    "http://localhost:8000/schemes/456/pledges/active",
    headers=headers
)

scheme_pledges = response.json()

total_active = len(scheme_pledges)
total_value = sum(p["principal_amount"] for p in scheme_pledges)
avg_interest = sum(p["interest_rate"] for p in scheme_pledges) / len(scheme_pledges)

print(f"Scheme 456: {total_active} active pledges, ${total_value} total value")
print(f"Average Interest Rate: {avg_interest}%")
```

### Example 4: Pagination Handling

```python
# Handle large datasets with pagination
all_pledges = []
skip = 0
limit = 50

while True:
    response = requests.get(
        f"http://localhost:8000/customers/123/pledges?skip={skip}&limit={limit}",
        headers=headers
    )
    
    pledges = response.json()
    if not pledges:
        break
    
    all_pledges.extend(pledges)
    skip += limit

print(f"Retrieved {len(all_pledges)} total pledges")
```

## Performance Considerations

### Database Optimization

- Customer and scheme existence checks use indexed lookups
- Pagination prevents large dataset memory issues
- Join operations are optimized for scheme data retrieval

### Query Performance

- Indexes on `customer_id`, `scheme_id`, and `company_id` ensure fast filtering
- Payment calculations are done in real-time (consider caching for high-volume scenarios)

### Recommended Usage

- Use pagination for customers with many pledges
- Consider caching scheme data if interest rates don't change frequently
- Implement client-side filtering for additional criteria

## Testing

### Test Coverage

The provided test suite covers:
- ✅ Active pledge retrieval by customer
- ✅ All pledge retrieval by customer  
- ✅ Active pledge retrieval by scheme
- ✅ Pagination functionality
- ✅ Authentication and authorization
- ✅ Error handling for non-existent resources
- ✅ Schema validation

### Running Tests

```bash
# Start the API server
uvicorn main:app --reload

# Run the test suite
python test_pledge_listing_api.py
```

## Integration Notes

### Database Requirements

Ensure the following relationships exist:
- `pledges.customer_id` → `customers.id`
- `pledges.scheme_id` → `schemes.id`
- `pledge_payments.pledge_id` → `pledges.pledge_id`

### API Dependencies

These endpoints integrate with existing PawnPro APIs:
- Customer management APIs for customer validation
- Scheme management APIs for interest rate data
- Payment APIs for remaining balance calculations

## Security Considerations

- ✅ JWT authentication required for all endpoints
- ✅ Admin/staff role verification prevents unauthorized access
- ✅ Company-based data isolation prevents cross-tenant data access
- ✅ SQL injection prevention through SQLAlchemy ORM
- ✅ Input validation through Pydantic schemas

## Migration Requirements

No database schema changes are required. These endpoints work with existing tables:
- `pledges`
- `customers`
- `schemes`
- `pledge_payments`

---

**Version**: 1.0  
**Last Updated**: September 2024  
**API Compatibility**: PawnPro v1.0+

For support or questions, please refer to the main PawnPro documentation or contact the development team.
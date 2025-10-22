# Pledge with Items API Documentation

## Overview
The Pledge with Items API provides comprehensive endpoints for creating and updating pledges along with their associated items in single transactions. This ensures data consistency and simplifies pledge management by handling both pledge and item operations atomically.

## Key Features
- ✅ **Atomic Transactions** - All operations succeed or fail together
- ✅ **Auto-Calculations** - Automatic weight and count calculations from items
- ✅ **Flexible Operations** - Add, update, delete items in single request
- ✅ **Data Validation** - Comprehensive validation of all inputs
- ✅ **Error Handling** - Detailed error messages and warnings

## API Endpoints

### 1. Create Pledge with Items
**POST** `/pledges/with-items`

Creates a new pledge along with its pledge items in a single transaction.

#### Request Body
```json
{
    "customer_id": 1,
    "scheme_id": 1,
    "pledge_date": "2025-09-15",
    "due_date": "2025-12-15",
    "document_charges": 100.0,
    "first_month_interest": 500.0,
    "total_loan_amount": 50000.0,
    "final_amount": 50500.0,
    "status": "active",
    "is_move_to_bank": false,
    "remarks": "Pledge with multiple gold items",
    "auto_calculate_weights": true,
    "auto_calculate_item_count": true,
    "items": [
        {
            "jewell_design_id": 1,
            "jewell_condition": "Excellent",
            "gross_weight": 25.5,
            "net_weight": 24.0,
            "net_value": 25000.0,
            "remarks": "Gold ring with diamonds"
        },
        {
            "jewell_design_id": 2,
            "jewell_condition": "Good",
            "gross_weight": 15.2,
            "net_weight": 14.8,
            "net_value": 15000.0,
            "remarks": "Gold chain"
        }
    ]
}
```

#### Response (200 OK)
```json
{
    "success": true,
    "message": "Pledge created successfully with 2 items",
    "pledge": {
        "pledge_id": 123,
        "pledge_no": "SCH001/2025/000123",
        "customer": {
            "id": 1,
            "name": "John Doe",
            "phone": "9876543210"
        },
        "scheme": {
            "id": 1,
            "scheme_name": "Gold Loan Scheme",
            "interest_rate_monthly": 1.5
        },
        "item_count": 2,
        "gross_weight": 40.7,
        "net_weight": 38.8,
        "total_loan_amount": 50000.0,
        "status": "active",
        "pledge_items": [
            {
                "pledge_item_id": 456,
                "jewell_design": {
                    "id": 1,
                    "design_name": "Diamond Ring"
                },
                "jewell_condition": "Excellent",
                "gross_weight": 25.5,
                "net_weight": 24.0,
                "net_value": 25000.0,
                "remarks": "Gold ring with diamonds"
            }
        ]
    },
    "items_created": 2,
    "items_updated": 0,
    "items_deleted": 0,
    "warnings": []
}
```

### 2. Update Pledge with Items
**PUT** `/pledges/{pledge_id}/with-items`

Updates an existing pledge and performs various operations on its items.

#### Request Body
```json
{
    "total_loan_amount": 60000.0,
    "final_amount": 60600.0,
    "remarks": "Updated pledge with item modifications",
    "auto_calculate_weights": true,
    "auto_calculate_item_count": true,
    "delete_item_ids": [456],
    "items": [
        {
            "jewell_design_id": 3,
            "jewell_condition": "Excellent",
            "gross_weight": 8.5,
            "net_weight": 8.2,
            "net_value": 8500.0,
            "remarks": "New gold bracelet",
            "action": "add"
        },
        {
            "pledge_item_id": 457,
            "jewell_design_id": 2,
            "jewell_condition": "Very Good",
            "gross_weight": 16.0,
            "net_weight": 15.5,
            "net_value": 16000.0,
            "remarks": "Updated gold chain valuation",
            "action": "update"
        }
    ]
}
```

#### Response (200 OK)
```json
{
    "success": true,
    "message": "Pledge and items updated successfully",
    "pledge": {
        "pledge_id": 123,
        "item_count": 2,
        "gross_weight": 24.5,
        "net_weight": 23.7,
        "total_loan_amount": 60000.0
    },
    "items_created": 1,
    "items_updated": 1,
    "items_deleted": 1,
    "warnings": []
}
```

## Request Models

### PledgeWithItemsCreate
```typescript
interface PledgeWithItemsCreate {
    // Pledge information
    customer_id: number;
    scheme_id: number;
    pledge_date: string; // YYYY-MM-DD format
    due_date: string;
    document_charges?: number; // default: 0.0
    first_month_interest: number;
    total_loan_amount: number;
    final_amount: number;
    status?: string; // default: "active"
    is_move_to_bank?: boolean; // default: false
    remarks?: string;
    
    // Items
    items: PledgeItemCreateData[];
    
    // Auto-calculation flags
    auto_calculate_weights?: boolean; // default: true
    auto_calculate_item_count?: boolean; // default: true
}

interface PledgeItemCreateData {
    jewell_design_id: number;
    jewell_condition: string;
    gross_weight: number; // >= 0
    net_weight: number; // >= 0
    net_value: number; // >= 0
    remarks?: string;
}
```

### PledgeWithItemsUpdate
```typescript
interface PledgeWithItemsUpdate {
    // Pledge information (all optional)
    customer_id?: number;
    scheme_id?: number;
    pledge_date?: string;
    due_date?: string;
    document_charges?: number;
    first_month_interest?: number;
    total_loan_amount?: number;
    final_amount?: number;
    status?: string;
    is_move_to_bank?: boolean;
    remarks?: string;
    
    // Item operations
    items?: PledgeItemUpdateData[];
    delete_item_ids?: number[];
    
    // Auto-calculation flags
    auto_calculate_weights?: boolean; // default: true
    auto_calculate_item_count?: boolean; // default: true
}

interface PledgeItemUpdateData {
    pledge_item_id?: number; // Required for update/delete actions
    jewell_design_id: number;
    jewell_condition: string;
    gross_weight: number;
    net_weight: number;
    net_value: number;
    remarks?: string;
    action: "keep" | "add" | "update" | "delete"; // default: "keep"
}
```

## Usage Examples

### cURL Examples

#### Create Pledge with Items
```bash
curl -X POST "http://localhost:8000/pledges/with-items" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "scheme_id": 1,
    "pledge_date": "2025-09-15",
    "due_date": "2025-12-15",
    "first_month_interest": 500.0,
    "total_loan_amount": 50000.0,
    "final_amount": 50500.0,
    "items": [
      {
        "jewell_design_id": 1,
        "jewell_condition": "Excellent",
        "gross_weight": 25.5,
        "net_weight": 24.0,
        "net_value": 25000.0,
        "remarks": "Gold ring"
      }
    ]
  }'
```

#### Update Pledge - Add New Items
```bash
curl -X PUT "http://localhost:8000/pledges/123/with-items" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "jewell_design_id": 2,
        "jewell_condition": "Good",
        "gross_weight": 10.0,
        "net_weight": 9.5,
        "net_value": 10000.0,
        "action": "add"
      }
    ]
  }'
```

#### Update Pledge - Modify Existing Item
```bash
curl -X PUT "http://localhost:8000/pledges/123/with-items" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "pledge_item_id": 456,
        "jewell_design_id": 1,
        "jewell_condition": "Excellent Plus",
        "gross_weight": 26.0,
        "net_weight": 24.5,
        "net_value": 26000.0,
        "action": "update"
      }
    ]
  }'
```

#### Update Pledge - Delete Items
```bash
curl -X PUT "http://localhost:8000/pledges/123/with-items" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "delete_item_ids": [456, 457]
  }'
```

### Python Example
```python
import requests

# Authentication
auth_response = requests.post("http://localhost:8000/token", data={
    "username": "your_username",
    "password": "your_password"
})
token = auth_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create pledge with items
pledge_data = {
    "customer_id": 1,
    "scheme_id": 1,
    "pledge_date": "2025-09-15",
    "due_date": "2025-12-15",
    "first_month_interest": 500.0,
    "total_loan_amount": 50000.0,
    "final_amount": 50500.0,
    "items": [
        {
            "jewell_design_id": 1,
            "jewell_condition": "Excellent",
            "gross_weight": 25.5,
            "net_weight": 24.0,
            "net_value": 25000.0
        }
    ]
}

response = requests.post("http://localhost:8000/pledges/with-items", 
                        json=pledge_data, 
                        headers=headers)
pledge = response.json()

# Update pledge - add items
update_data = {
    "items": [
        {
            "jewell_design_id": 2,
            "jewell_condition": "Good",
            "gross_weight": 10.0,
            "net_weight": 9.5,
            "net_value": 10000.0,
            "action": "add"
        }
    ]
}

response = requests.put(f"http://localhost:8000/pledges/{pledge['pledge']['pledge_id']}/with-items",
                       json=update_data,
                       headers=headers)
```

## Item Operations Guide

### Action Types in Updates

1. **"add"** - Create new pledge item
   - `pledge_item_id` not required
   - All other fields required

2. **"update"** - Modify existing pledge item
   - `pledge_item_id` required
   - All other fields will update the existing item

3. **"delete"** - Remove pledge item
   - `pledge_item_id` required
   - Can also use `delete_item_ids` array

4. **"keep"** - No action (default)
   - Used when you want to include item data but not modify it

### Alternative Deletion Methods

**Method 1: Using action="delete"**
```json
{
    "items": [
        {
            "pledge_item_id": 456,
            "action": "delete"
        }
    ]
}
```

**Method 2: Using delete_item_ids**
```json
{
    "delete_item_ids": [456, 457]
}
```

## Auto-Calculation Features

### Weight Calculation
When `auto_calculate_weights: true`:
- `gross_weight` = sum of all item gross weights
- `net_weight` = sum of all item net weights

### Item Count Calculation
When `auto_calculate_item_count: true`:
- `item_count` = total number of pledge items

### Manual Override
Set flags to `false` to maintain existing values or set them manually.

## Business Rules

### Validation Rules
1. **Required Items**: At least one item required for pledge creation
2. **Customer Validation**: Customer must exist and belong to user's company
3. **Scheme Validation**: Scheme must exist in the system
4. **Design Validation**: All jewell_design_ids must exist
5. **Weight Validation**: All weights must be >= 0
6. **Value Validation**: All values must be >= 0

### Transaction Safety
- All operations within single database transaction
- If any operation fails, entire transaction is rolled back
- Maintains data consistency across pledge and items

### Company Isolation
- Users can only access pledges from their company
- Customer and pledge validation enforces company boundaries

## Error Handling

### Common Error Responses

#### 400 Bad Request - Missing Items
```json
{
    "detail": "At least one pledge item is required"
}
```

#### 400 Bad Request - Invalid Customer
```json
{
    "detail": "Customer not found"
}
```

#### 400 Bad Request - Invalid Design
```json
{
    "detail": "Jewell design ID 999 not found"
}
```

#### 404 Not Found - Pledge Not Found
```json
{
    "detail": "Pledge not found"
}
```

#### 500 Internal Server Error
```json
{
    "detail": "Error creating pledge with items: [specific error message]"
}
```

## Response Fields

### PledgeWithItemsResponse
- `success`: Boolean indicating operation success
- `message`: Human-readable message
- `pledge`: Complete pledge details with items
- `items_created`: Number of items created
- `items_updated`: Number of items updated
- `items_deleted`: Number of items deleted
- `warnings`: Array of non-critical warnings

## Testing

Run the comprehensive test suite:
```bash
python test_pledge_with_items_api.py
```

The test suite covers:
- ✅ Pledge creation with multiple items
- ✅ Adding items to existing pledge
- ✅ Updating existing items
- ✅ Deleting items from pledge
- ✅ Comprehensive mixed operations
- ✅ Error scenario handling
- ✅ Auto-calculation verification

## Performance Considerations

1. **Single Transaction**: All operations in one transaction reduces database overhead
2. **Batch Operations**: Multiple item operations processed efficiently
3. **Eager Loading**: Relationships loaded efficiently for response
4. **Validation Batching**: Design validation done in single query

## Security Features

- 🔐 JWT token authentication required
- 🏢 Company-level data isolation
- 🛡️ SQL injection prevention through SQLAlchemy ORM
- ✅ Comprehensive input validation
- 📊 Audit trail with timestamps

## Comparison with Individual APIs

| Feature | Individual APIs | Pledge with Items API |
|---------|----------------|----------------------|
| Transaction Safety | ❌ Separate transactions | ✅ Single transaction |
| Data Consistency | ⚠️ Potential inconsistency | ✅ Guaranteed consistency |
| API Calls | 🔄 Multiple calls needed | ✅ Single call |
| Error Handling | ⚠️ Partial failures possible | ✅ All-or-nothing |
| Performance | 📈 Multiple round trips | ✅ Single round trip |
| Complexity | 🔧 Client handles coordination | ✅ Server handles coordination |

The Pledge with Items API is recommended for all new integrations requiring pledge and item operations.
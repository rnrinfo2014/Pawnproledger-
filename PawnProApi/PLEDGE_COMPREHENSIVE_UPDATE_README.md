# Comprehensive Pledge Update API Documentation

## Overview

The comprehensive pledge update endpoint allows you to perform complex operations on pledges in a single transaction, including:

- **Customer Updates**: Modify customer information or transfer pledge to different customer
- **Scheme Changes**: Change the pledge scheme with optional financial recalculation
- **Date Modifications**: Update pledge date, due date
- **Pledge Item Operations**: Add, update, or remove pledge items
- **Financial Updates**: Update amounts, charges, and recalculate weights
- **Status Changes**: Change pledge status (active, redeemed, auctioned, etc.)

## Endpoint

```
PUT /pledges/{pledge_id}/comprehensive-update
```

**Authentication**: Required (JWT Bearer token)

## Request Body Schema

### Basic Pledge Updates
```json
{
  "scheme_id": 2,                    // Change to different scheme
  "pledge_date": "2024-01-15",       // Change pledge date
  "due_date": "2024-12-15",          // Change due date  
  "document_charges": 150.0,         // Update document charges
  "first_month_interest": 500.0,     // Update first month interest
  "total_loan_amount": 45000.0,      // Update total loan amount
  "final_amount": 45500.0,           // Update final amount
  "status": "active",                // Change status: active, redeemed, auctioned
  "is_move_to_bank": false,          // Update bank move status
  "remarks": "Updated pledge notes", // Update remarks
}
```

### Customer Operations

#### Option 1: Update Existing Customer Information
```json
{
  "customer_updates": {
    "name": "Updated Customer Name",
    "address": "New Address 123",
    "city": "New City",
    "area_id": 5,
    "phone": "9876543210",           // Must be unique
    "id_proof_type": "Aadhaar Card"
  }
}
```

#### Option 2: Transfer Pledge to Different Customer
```json
{
  "change_customer_id": 15           // Transfer entire pledge to customer ID 15
}
```

### Pledge Item Operations

```json
{
  "item_operations": [
    {
      "operation": "add",             // Add new item
      "jewell_design_id": 3,
      "jewell_condition": "Excellent",
      "gross_weight": 15.5,
      "net_weight": 14.8,
      "net_value": 65000.0,
      "remarks": "New gold necklace"
    },
    {
      "operation": "update",          // Update existing item
      "pledge_item_id": 7,            // Required for update/remove
      "gross_weight": 12.0,
      "net_weight": 11.2,
      "net_value": 50000.0,
      "remarks": "Weight updated after cleaning"
    },
    {
      "operation": "remove",          // Remove item
      "pledge_item_id": 8
    }
  ]
}
```

### Recalculation Options

```json
{
  "recalculate_weights": true,        // Auto-recalculate gross/net weights from items
  "recalculate_item_count": true,     // Auto-recalculate item count from items  
  "recalculate_financials": false     // Recalculate loan amounts based on new scheme
}
```

## Complete Example Request

```json
{
  "scheme_id": 2,
  "pledge_date": "2024-01-15",
  "due_date": "2024-12-15",
  "document_charges": 150.0,
  "remarks": "Comprehensive update with customer and items changes",
  
  "customer_updates": {
    "address": "Updated Address 123, New Location",
    "city": "Mumbai",
    "phone": "9876543210"
  },
  
  "item_operations": [
    {
      "operation": "add",
      "jewell_design_id": 1,
      "jewell_condition": "Good", 
      "gross_weight": 10.5,
      "net_weight": 9.8,
      "net_value": 45000.0,
      "remarks": "Additional gold ring"
    },
    {
      "operation": "update",
      "pledge_item_id": 5,
      "gross_weight": 12.0,
      "net_weight": 11.2,
      "remarks": "Updated after re-measurement"
    },
    {
      "operation": "remove", 
      "pledge_item_id": 3
    }
  ],
  
  "recalculate_weights": true,
  "recalculate_item_count": true,
  "recalculate_financials": false
}
```

## Response Schema

```json
{
  "success": true,
  "message": "Pledge updated successfully",
  "warnings": [
    "Financial recalculation should be implemented based on business rules"
  ],
  "changes_summary": {
    "customer_updated": ["address: Updated Address 123", "city: Mumbai"],
    "pledge_updated": ["document_charges: 150.0", "remarks: Updated notes"],
    "weights_recalculated": "gross: 125.5, net: 118.2"
  },
  "items_added": 1,
  "items_updated": 1, 
  "items_removed": 1,
  "updated_pledge": {
    // Complete PledgeDetailView object with all related data
    "pledge_id": 1,
    "pledge_no": "GLD001",
    "customer": { 
      "id": 1,
      "name": "Customer Name",
      "address": "Updated Address 123",
      // ... full customer details
    },
    "scheme": {
      "id": 2,
      "scheme_name": "Gold Scheme B",
      // ... full scheme details  
    },
    "pledge_items": [
      // ... array of updated pledge items with full details
    ]
    // ... all other pledge fields
  }
}
```

## Usage Scenarios

### 1. Customer Information Update
```bash
curl -X PUT "http://localhost:8000/pledges/1/comprehensive-update" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_updates": {
      "address": "New Address",
      "phone": "9876543210"
    }
  }'
```

### 2. Scheme Change with Financial Recalculation  
```bash
curl -X PUT "http://localhost:8000/pledges/1/comprehensive-update" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scheme_id": 3,
    "recalculate_financials": true
  }'
```

### 3. Transfer Pledge to Different Customer
```bash
curl -X PUT "http://localhost:8000/pledges/1/comprehensive-update" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "change_customer_id": 25
  }'
```

### 4. Add Multiple Items and Recalculate
```bash
curl -X PUT "http://localhost:8000/pledges/1/comprehensive-update" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_operations": [
      {
        "operation": "add",
        "jewell_design_id": 1,
        "jewell_condition": "Excellent",
        "gross_weight": 15.0,
        "net_weight": 14.5,
        "net_value": 70000.0
      }
    ],
    "recalculate_weights": true,
    "recalculate_item_count": true
  }'
```

### 5. Remove Items and Update Status
```bash  
curl -X PUT "http://localhost:8000/pledges/1/comprehensive-update" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_operations": [
      {"operation": "remove", "pledge_item_id": 10},
      {"operation": "remove", "pledge_item_id": 11}
    ],
    "status": "partially_redeemed",
    "recalculate_weights": true,
    "recalculate_item_count": true
  }'
```

## Error Responses

### 404 - Pledge Not Found
```json
{
  "detail": "Pledge not found"
}
```

### 400 - Validation Errors
```json
{
  "detail": "Phone number already exists for another customer"
}
```

```json
{
  "detail": "New scheme not found"
}
```

### 500 - Server Error
```json
{
  "detail": "Error updating pledge: [specific error message]"
}
```

## Business Rules & Validations

1. **Customer Phone Uniqueness**: Phone numbers must be unique across customers in the same company
2. **Scheme Validation**: New scheme must exist and belong to the same company
3. **Customer Transfer**: Target customer must exist and belong to the same company
4. **Item Operations**: 
   - Add operations require jewell_design_id and jewell_condition
   - Update/Remove operations require valid pledge_item_id
   - Jewell designs must exist in the system
5. **Transaction Safety**: All operations are performed in a single database transaction
6. **Company Isolation**: All operations are scoped to the current user's company

## Notes

- **File Uploads**: Image updates for customers or pledge items should be handled through separate file upload endpoints
- **Financial Recalculation**: The `recalculate_financials` flag is a placeholder for business-specific financial recalculation logic
- **Audit Trail**: Consider implementing audit logging for tracking changes to critical pledge data
- **Permissions**: Ensure proper role-based access control for different types of updates
- **Rollback**: If any part of the update fails, the entire transaction is rolled back to maintain data consistency

## Testing

Use the provided test script `test_pledge_comprehensive_update.py` to test various scenarios:

1. Update the configuration variables (BASE_URL, TEST_PLEDGE_ID, token)
2. Ensure you have valid customer IDs, scheme IDs, and pledge item IDs
3. Run different test scenarios to verify functionality
4. Check the response for success, warnings, and change summaries
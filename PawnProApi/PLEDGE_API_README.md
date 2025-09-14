# Pledge API Endpoints

## Overview
The PawnPro API now includes comprehensive CRUD operations for pledge management with automatic pledge number generation.

## Pledge Endpoints

### Create Pledge
- **POST** `/pledges/`
- **Body**: PledgeCreate schema
- **Auto-generates**: `pledge_no` with scheme prefix (e.g., "GL-0001")
- **Validates**: Customer and scheme existence

### Get All Pledges
- **GET** `/pledges/`
- **Query params**: `skip=0`, `limit=100`
- **Filters**: Only pledges from user's company

### Get Single Pledge
- **GET** `/pledges/{pledge_id}`
- **Validates**: Pledge exists and belongs to user's company

### Update Pledge
- **PUT** `/pledges/{pledge_id}`
- **Body**: PledgeCreate schema

### Update Pledge with Items
- **PUT** `/pledges/{pledge_id}/with-items`
- **Body**: PledgeUpdateWithItems schema
- **Features**: 
  - Updates pledge details
  - Replaces all existing pledge items with new ones
  - Atomic transaction (all changes or no changes)
  - Validates customer, scheme, and jewell design references

### Delete Pledge
- **DELETE** `/pledges/{pledge_id}`
- **Cascades**: Deletes all associated pledge items

## Pledge Item Endpoints

### Create Pledge Item
- **POST** `/pledge-items/`
- **Body**: PledgeItemCreate schema
- **Validates**: Pledge and jewell type existence

### Get All Pledge Items
- **GET** `/pledge-items/`
- **Query params**: `skip=0`, `limit=100`

### Get Items by Pledge
- **GET** `/pledges/{pledge_id}/items`
- **Returns**: All items for a specific pledge

### Get Single Pledge Item
- **GET** `/pledge-items/{item_id}`

### Update Pledge Item
- **PUT** `/pledge-items/{item_id}`
- **Body**: PledgeItemCreate schema

### Delete Pledge Item
- **DELETE** `/pledge-items/{item_id}`

## Data Models

### Pledge
```json
{
  "pledge_id": 1,
  "customer_id": 1,
  "scheme_id": 1,
  "pledge_no": "GL-0001",
  "pledge_date": "2025-09-09",
  "due_date": "2025-10-09",
  "item_count": 2,
  "gross_weight": 10.5,
  "net_weight": 9.8,
  "document_charges": 100.0,
  "first_month_interest": 50.0,
  "total_loan_amount": 5000.0,
  "final_amount": 5150.0,
  "status": "active",
  "created_at": "2025-09-09T10:00:00",
  "created_by": 1,
  "is_move_to_bank": false,
  "remarks": "Test pledge",
  "company_id": 1
}
```

### Pledge Item
```json
{
  "pledge_item_id": 1,
  "pledge_id": 1,
  "jewell_design_id": 1,
  "jewell_condition": "Good",
  "gross_weight": 5.5,
  "net_weight": 5.0,
  "image": null,
  "net_value": 2500.0,
  "remarks": "Gold necklace",
  "created_at": "2025-09-09T10:00:00"
}
```

### Pledge Update with Items
```json
{
  "customer_id": 1,
  "scheme_id": 1,
  "pledge_date": "2025-09-09",
  "due_date": "2025-10-09",
  "item_count": 2,
  "gross_weight": 12.0,
  "net_weight": 11.5,
  "document_charges": 150.0,
  "first_month_interest": 75.0,
  "total_loan_amount": 6000.0,
  "final_amount": 6225.0,
  "company_id": 1,
  "status": "active",
  "is_move_to_bank": false,
  "remarks": "Updated pledge with new items",
  "pledge_items": [
    {
      "jewell_design_id": 1,
      "jewell_condition": "Excellent",
      "gross_weight": 6.0,
      "net_weight": 5.8,
      "net_value": 3000.0,
      "remarks": "Gold ring"
    },
    {
      "jewell_design_id": 2,
      "jewell_condition": "Good",
      "gross_weight": 6.0,
      "net_weight": 5.7,
      "net_value": 3000.0,
      "remarks": "Gold chain"
    }
  ]
}
```

## Features
- ✅ Auto-generated pledge numbers with scheme prefixes
- ✅ Company-based data isolation
- ✅ Foreign key validation
- ✅ Cascade delete for pledge items
- ✅ JWT authentication required
- ✅ Comprehensive CRUD operations
- ✅ RESTful API design
- ✅ Atomic pledge and items update

## Usage Example
```javascript
// Create a pledge
const pledgeData = {
  customer_id: 1,
  scheme_id: 1,
  pledge_date: "2025-09-09",
  due_date: "2025-10-09",
  item_count: 2,
  gross_weight: 10.5,
  net_weight: 9.8,
  document_charges: 100.0,
  first_month_interest: 50.0,
  total_loan_amount: 5000.0,
  final_amount: 5150.0,
  company_id: 1
};

fetch('/pledges/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify(pledgeData)
});

// Update pledge with new items (replaces all existing items)
const pledgeUpdateData = {
  customer_id: 1,
  scheme_id: 1,
  pledge_date: "2025-09-09",
  due_date: "2025-10-09",
  item_count: 2,
  gross_weight: 12.0,
  net_weight: 11.5,
  document_charges: 150.0,
  first_month_interest: 75.0,
  total_loan_amount: 6000.0,
  final_amount: 6225.0,
  company_id: 1,
  status: "active",
  is_move_to_bank: false,
  remarks: "Updated pledge with new items",
  pledge_items: [
    {
      jewell_design_id: 1,
      jewell_condition: "Excellent",
      gross_weight: 6.0,
      net_weight: 5.8,
      net_value: 3000.0,
      remarks: "Gold ring"
    },
    {
      jewell_design_id: 2,
      jewell_condition: "Good", 
      gross_weight: 6.0,
      net_weight: 5.7,
      net_value: 3000.0,
      remarks: "Gold chain"
    }
  ]
};

fetch('/pledges/1/with-items', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify(pledgeData)
});
```

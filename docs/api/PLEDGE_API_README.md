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
- **Query params**: 
  - `skip=0` - Number of records to skip (pagination)
  - `limit=100` - Maximum number of records to return
  - `search` - Optional search term to filter pledges
- **Filters**: Only pledges from user's company
- **Search Fields**: Searches across multiple fields:
  - Pledge number (`pledge_no`)
  - Pledge status (`status`)
  - Pledge remarks (`remarks`)
  - Customer name (`customer.name`)
  - Customer phone (`customer.phone`)
- **Search Example**: `/pledges/?search=PL001` or `/pledges/?search=active`

### Get Single Pledge
- **GET** `/pledges/{pledge_id}`
- **Validates**: Pledge exists and belongs to user's company

### Update Pledge
- **PUT** `/pledges/{pledge_id}`
- **Body**: PledgeCreate schema

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

## Features
- ✅ Auto-generated pledge numbers with scheme prefixes
- ✅ Company-based data isolation
- ✅ Foreign key validation
- ✅ Cascade delete for pledge items
- ✅ JWT authentication required
- ✅ Comprehensive CRUD operations
- ✅ RESTful API design

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

// Search Examples

// 1. Get all pledges (no search)
fetch('/pledges/')
  .then(response => response.json())
  .then(pledges => console.log('All pledges:', pledges));

// 2. Search by pledge number
fetch('/pledges/?search=PL001')
  .then(response => response.json())
  .then(pledges => console.log('Pledges matching PL001:', pledges));

// 3. Search by customer name
fetch('/pledges/?search=John')
  .then(response => response.json())
  .then(pledges => console.log('Pledges for customers named John:', pledges));

// 4. Search by status
fetch('/pledges/?search=active')
  .then(response => response.json())
  .then(pledges => console.log('Active pledges:', pledges));

// 5. Search with pagination
fetch('/pledges/?search=PL&limit=10&skip=0')
  .then(response => response.json())
  .then(pledges => console.log('First 10 pledges starting with PL:', pledges));

// 6. Search by customer phone
fetch('/pledges/?search=9876543210')
  .then(response => response.json())
  .then(pledges => console.log('Pledges for customer with phone:', pledges));

fetch('/pledges/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify(pledgeData)
});
```

# Payment Receipt API Documentation

## 🧾 Overview

The Payment Receipt API provides comprehensive functionality for managing and retrieving payment receipts in the PawnPro system. This API allows users to search, filter, and view detailed receipt information for all payment transactions.

## 🚀 Features

- ✅ **Receipt Retrieval**: Get receipts by receipt number, payment ID, customer, or pledge
- ✅ **Advanced Search**: Multi-criteria search with partial matching and range filters  
- ✅ **Pagination Support**: Efficient pagination for large receipt datasets
- ✅ **Detailed Information**: Complete receipt details suitable for printing/PDF generation
- ✅ **Analytics Dashboard**: Receipt summaries with breakdowns by payment method and type
- ✅ **Latest Receipts**: Quick access to most recent payment receipts
- ✅ **Multi-tenant Support**: Company-specific data isolation

## 📍 API Base URL

```
Base URL: http://localhost:8000/api/v1/receipts
```

## 🔐 Authentication

All endpoints require authentication. Include the access token in the header:

```
Authorization: Bearer <your_access_token>
```

## 📋 API Endpoints

### 1. Get All Receipts (Paginated)

```http
GET /api/v1/receipts/
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Records per page (default: 50, max: 500) 
- `customer_id` (int, optional): Filter by customer ID
- `pledge_id` (int, optional): Filter by pledge ID
- `payment_type` (string, optional): Filter by payment type
- `payment_method` (string, optional): Filter by payment method
- `from_date` (date, optional): Start date filter (YYYY-MM-DD)
- `to_date` (date, optional): End date filter (YYYY-MM-DD)
- `sort_by` (string): Sort field (default: "created_at")
- `sort_order` (string): Sort order: "asc" or "desc" (default: "desc")

**Sample Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/receipts/?page=1&limit=20&payment_type=interest&from_date=2024-10-01" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

**Sample Response:**
```json
{
  "receipts": [
    {
      "payment_id": 123,
      "receipt_no": "RCPT-1-2024-00001",
      "payment_date": "2024-10-15",
      "customer_name": "John Doe",
      "pledge_no": "PLG-001-2024",
      "amount": 2500.0,
      "payment_type": "interest",
      "payment_method": "cash",
      "created_at": "2024-10-15T10:30:00Z"
    }
  ],
  "total_count": 45,
  "page": 1,
  "limit": 20,
  "total_amount": 125000.0
}
```

### 2. Get Receipt by Receipt Number

```http
GET /api/v1/receipts/receipt/{receipt_no}
```

**Path Parameters:**
- `receipt_no` (string): The receipt number to retrieve

**Sample Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/receipts/receipt/RCPT-1-2024-00001" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

**Sample Response:**
```json
{
  "payment_id": 123,
  "receipt_no": "RCPT-1-2024-00001",
  "payment_date": "2024-10-15",
  "payment_type": "interest",
  "payment_method": "cash",
  "bank_reference": null,
  "amount": 2500.0,
  "interest_amount": 2500.0,
  "principal_amount": 0.0,
  "penalty_amount": 0.0,
  "discount_amount": 0.0,
  "balance_amount": 47500.0,
  "remarks": "Monthly interest payment",
  "created_at": "2024-10-15T10:30:00Z",
  "created_by": 1,
  
  "customer_id": 101,
  "customer_name": "John Doe",
  "customer_phone": "+91-9876543210",
  "customer_address": "123 Main Street, City",
  
  "pledge_id": 501,
  "pledge_no": "PLG-001-2024",
  "pledge_date": "2024-09-15",
  "loan_amount": 50000.0,
  "final_amount": 50000.0,
  
  "company_name": "ABC Pawn Shop",
  "company_address": "456 Business St, City",
  "company_phone": "+91-1234567890",
  
  "staff_name": "admin"
}
```

### 3. Get Receipt by Payment ID

```http
GET /api/v1/receipts/payment/{payment_id}
```

**Path Parameters:**
- `payment_id` (int): The payment ID to retrieve

**Sample Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/receipts/payment/123" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:** Same as receipt by receipt number

### 4. Get Customer Receipts

```http
GET /api/v1/receipts/customer/{customer_id}
```

**Path Parameters:**
- `customer_id` (int): Customer ID

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Records per page (default: 50)
- `from_date` (date, optional): Start date filter
- `to_date` (date, optional): End date filter

**Sample Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/receipts/customer/101?from_date=2024-10-01" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Get Pledge Receipts

```http
GET /api/v1/receipts/pledge/{pledge_id}
```

**Path Parameters:**
- `pledge_id` (int): Pledge ID

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Records per page (default: 50)

**Sample Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/receipts/pledge/501" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Advanced Receipt Search

```http
POST /api/v1/receipts/search
```

**Request Body:**
```json
{
  "receipt_no": "RCPT-1",
  "customer_name": "John",
  "pledge_no": "PLG-001",
  "payment_type": "interest",
  "payment_method": "cash",
  "from_date": "2024-10-01",
  "to_date": "2024-10-31",
  "min_amount": 1000.0,
  "max_amount": 5000.0
}
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Records per page (default: 50)

**Sample Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/receipts/search?page=1&limit=20" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "customer_name": "John",
       "payment_type": "interest",
       "from_date": "2024-10-01",
       "min_amount": 1000.0
     }'
```

### 7. Receipt Summary & Analytics

```http
GET /api/v1/receipts/summary
```

**Query Parameters:**
- `from_date` (date, optional): Start date filter
- `to_date` (date, optional): End date filter

**Sample Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/receipts/summary?from_date=2024-10-01" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

**Sample Response:**
```json
{
  "total_receipts": 150,
  "total_amount": 375000.0,
  "payment_methods": {
    "cash": {
      "count": 120,
      "amount": 300000.0
    },
    "bank_transfer": {
      "count": 25,
      "amount": 62500.0
    },
    "upi": {
      "count": 5,
      "amount": 12500.0
    }
  },
  "payment_types": {
    "interest": {
      "count": 100,
      "amount": 250000.0
    },
    "principal": {
      "count": 30,
      "amount": 75000.0
    },
    "partial_redeem": {
      "count": 20,
      "amount": 50000.0
    }
  },
  "date_range": {
    "earliest_payment": "2024-10-01",
    "latest_payment": "2024-10-15"
  }
}
```

### 8. Latest Receipts

```http
GET /api/v1/receipts/latest
```

**Query Parameters:**
- `count` (int): Number of latest receipts (default: 10, max: 100)

**Sample Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/receipts/latest?count=5" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:** Array of basic receipt information (same format as paginated list)

## 📊 Data Models

### ReceiptBasicInfo
```json
{
  "payment_id": 123,
  "receipt_no": "RCPT-1-2024-00001",
  "payment_date": "2024-10-15",
  "customer_name": "John Doe",
  "pledge_no": "PLG-001-2024",
  "amount": 2500.0,
  "payment_type": "interest",
  "payment_method": "cash",
  "created_at": "2024-10-15T10:30:00Z"
}
```

### ReceiptDetailInfo
Complete receipt information including customer, pledge, company, and staff details.

### ReceiptSearchRequest
```json
{
  "receipt_no": "string (optional)",
  "customer_name": "string (optional)",
  "pledge_no": "string (optional)", 
  "payment_type": "string (optional)",
  "payment_method": "string (optional)",
  "from_date": "date (optional)",
  "to_date": "date (optional)",
  "min_amount": "float (optional)",
  "max_amount": "float (optional)"
}
```

## 🔍 Search Features

### Partial Matching
- Receipt numbers: Search "RCPT-1" finds "RCPT-1-2024-00001"
- Customer names: Search "John" finds "John Doe", "Johnson", etc.
- Pledge numbers: Search "PLG" finds all pledge-related receipts

### Range Filters
- Date ranges: Filter receipts between specific dates
- Amount ranges: Filter by minimum and maximum payment amounts

### Multiple Criteria
- Combine multiple search criteria for precise filtering
- All search parameters are optional and can be used independently

## 📄 Use Cases

### 1. Receipt Lookup
```bash
# Find receipt by number
GET /api/v1/receipts/receipt/RCPT-1-2024-00001

# Get all receipts for customer
GET /api/v1/receipts/customer/101
```

### 2. Daily Operations
```bash
# Get today's receipts
GET /api/v1/receipts/?from_date=2024-10-15&to_date=2024-10-15

# Get latest 10 receipts
GET /api/v1/receipts/latest?count=10
```

### 3. Customer Service
```bash
# Find customer payments
POST /api/v1/receipts/search
{
  "customer_name": "John Doe",
  "from_date": "2024-10-01"
}
```

### 4. Financial Reporting
```bash
# Get monthly summary
GET /api/v1/receipts/summary?from_date=2024-10-01&to_date=2024-10-31

# Find large payments
POST /api/v1/receipts/search
{
  "min_amount": 10000,
  "payment_type": "principal"
}
```

## ⚡ Performance Tips

1. **Use Pagination**: Always specify reasonable limits for large datasets
2. **Date Filters**: Use date ranges to limit search scope for better performance
3. **Specific Filters**: Use specific payment types/methods when possible
4. **Index Utilization**: Receipt numbers and payment IDs are indexed for fast lookup

## 🛡️ Security Features

- **Authentication Required**: All endpoints require valid JWT tokens
- **Company Isolation**: Users can only access receipts from their company
- **Role-based Access**: Standard users can view receipts, admin users have full access
- **Data Validation**: All input parameters are validated for security

## 📈 Integration Examples

### Frontend Dashboard
```javascript
// Get latest receipts for dashboard
const response = await fetch('/api/v1/receipts/latest?count=5', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const latestReceipts = await response.json();
```

### Customer Statement
```javascript
// Get all customer receipts
const response = await fetch(`/api/v1/receipts/customer/${customerId}`, {
  headers: { 'Authorization': `Bearer ${token}` }
});
const customerReceipts = await response.json();
```

### Receipt Printing
```javascript
// Get detailed receipt for printing
const response = await fetch(`/api/v1/receipts/receipt/${receiptNo}`, {
  headers: { 'Authorization': `Bearer ${token}` }
});
const receiptDetails = await response.json();
```

## 🎯 Best Practices

1. **Caching**: Cache frequently accessed receipts on the frontend
2. **Lazy Loading**: Load receipt details only when needed
3. **Error Handling**: Always handle 404 errors for non-existent receipts
4. **Date Formatting**: Use ISO date format (YYYY-MM-DD) for consistency
5. **Pagination**: Implement proper pagination controls in UI

## 📱 Mobile App Support

All endpoints are mobile-friendly and return JSON responses suitable for mobile applications. Consider implementing:

- Offline receipt storage for recently viewed receipts
- Image capture of physical receipts for reference
- Push notifications for payment confirmations

---

**Note**: This API is part of the PawnPro system's modular architecture and integrates seamlessly with other modules including Pledge Management, Customer Management, and Financial Accounting.
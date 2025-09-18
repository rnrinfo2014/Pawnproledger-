# 📚 PawnSoft API Documentation

Complete API reference for PawnSoft Pawn Shop Management System

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.rnrinfo.dev`

## Authentication

All API endpoints (except health check and token generation) require JWT authentication.

### Headers
```
Authorization: Bearer <your-jwt-token>
Content-Type: application/json
```

---

## 🔐 Authentication Endpoints

### Login
```http
POST /token
Content-Type: application/x-www-form-urlencoded

username=admin&password=your_password
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User
```http
GET /users/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@pawnsoft.com",
  "role": "admin",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

## 👥 User Management

### Create User
```http
POST /users
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "secure_password",
  "role": "user"
}
```

### List Users
```http
GET /users
Authorization: Bearer <admin-token>
```

### Get User by ID
```http
GET /users/{user_id}
Authorization: Bearer <admin-token>
```

---

## 🏢 Company Management

### List Companies
```http
GET /companies
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "company_name": "ABC Pawn Shop",
    "address": "123 Main Street",
    "phone": "+1-234-567-8900",
    "email": "info@abcpawn.com",
    "pan_number": "ABCDE1234F",
    "gst_number": "12ABCDE1234F1Z1",
    "is_active": true,
    "logo_path": "/uploads/company_1_logo.jpg"
  }
]
```

### Create Company
```http
POST /companies
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "company_name": "New Pawn Shop",
  "address": "456 Oak Avenue",
  "phone": "+1-555-123-4567",
  "email": "info@newpawn.com",
  "pan_number": "NEWPA1234N",
  "gst_number": "12NEWPA1234N1Z1"
}
```

---

## 👤 Customer Management

### List Customers
```http
GET /customers
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100)

### Create Customer
```http
POST /customers
Authorization: Bearer <token>
Content-Type: application/json

{
  "customer_name": "John Doe",
  "father_husband_name": "Robert Doe",
  "phone_number": "+1-555-987-6543",
  "alt_phone_number": "+1-555-987-6544",
  "address": "789 Pine Street",
  "id_proof_type": "Aadhaar",
  "id_proof_number": "1234-5678-9012",
  "company_id": 1,
  "area_id": 1
}
```

### Search Customers
```http
GET /customers/search?query=john
Authorization: Bearer <token>
```

---

## 💎 Pledge Management

### List Pledges
```http
GET /pledges
Authorization: Bearer <token>
```

**Query Parameters:**
- `customer_id`: Filter by customer
- `status`: Filter by pledge status
- `from_date`: Filter from date (YYYY-MM-DD)
- `to_date`: Filter to date (YYYY-MM-DD)

### Create Pledge
```http
POST /pledges
Authorization: Bearer <token>
Content-Type: application/json

{
  "customer_id": 1,
  "company_id": 1,
  "scheme_id": 1,
  "pledge_amount": 50000.00,
  "interest_rate": 2.5,
  "months": 12,
  "pledge_date": "2025-01-15",
  "due_date": "2026-01-15",
  "items": [
    {
      "item_name": "Gold Necklace",
      "metal_type": "Gold",
      "weight": 25.5,
      "purity": "22K",
      "item_value": 60000.00,
      "description": "Traditional gold necklace"
    }
  ]
}
```

### Get Pledge Details
```http
GET /pledges/{pledge_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "pledge_number": "PL001",
  "customer": {
    "id": 1,
    "customer_name": "John Doe",
    "phone_number": "+1-555-987-6543"
  },
  "pledge_amount": 50000.00,
  "interest_rate": 2.5,
  "due_date": "2026-01-15",
  "status": "Active",
  "items": [
    {
      "id": 1,
      "item_name": "Gold Necklace",
      "weight": 25.5,
      "purity": "22K",
      "item_value": 60000.00
    }
  ],
  "payments": [
    {
      "id": 1,
      "payment_date": "2025-02-15",
      "amount": 1250.00,
      "payment_type": "Interest"
    }
  ]
}
```

---

## 💰 Payment Management

### Record Payment
```http
POST /pledge_payments
Authorization: Bearer <token>
Content-Type: application/json

{
  "pledge_id": 1,
  "payment_date": "2025-02-15",
  "amount": 1250.00,
  "payment_method": "Cash",
  "payment_type": "Interest",
  "reference_number": "REF001",
  "notes": "Monthly interest payment"
}
```

### List Payments
```http
GET /pledge_payments
Authorization: Bearer <token>
```

**Query Parameters:**
- `pledge_id`: Filter by pledge
- `customer_id`: Filter by customer
- `from_date`: Filter from date
- `to_date`: Filter to date

---

## 📊 Chart of Accounts API

### Get All Accounts
```http
GET /api/v1/coa/accounts
Authorization: Bearer <token>
```

**Query Parameters:**
- `company_id`: Company ID (required)
- `account_type`: Filter by account type (Asset, Liability, Income, Expense, Equity)
- `is_active`: Filter by active status

**Response:**
```json
[
  {
    "id": 1,
    "account_code": "1001",
    "account_name": "Cash in Hand",
    "account_type": "Asset",
    "group_name": "Current Assets",
    "parent_id": null,
    "is_active": true,
    "balance": 150000.00
  }
]
```

### Create Account
```http
POST /api/v1/coa/accounts
Authorization: Bearer <token>
Content-Type: application/json

{
  "account_name": "Customer - John Doe",
  "account_code": "2001-001",
  "account_type": "Liability",
  "group_name": "Customer Accounts",
  "parent_id": 30,
  "company_id": 1,
  "is_active": true
}
```

### Get Account Tree Structure
```http
GET /api/v1/coa/accounts/tree?company_id=1
Authorization: Bearer <token>
```

### Initialize Pawn Shop COA
```http
POST /api/v1/coa/initialize?company_id=1
Authorization: Bearer <admin-token>
```

---

## 📅 Daybook API

### Daily Summary
```http
GET /api/v1/daybook/daily_summary
Authorization: Bearer <token>
```

**Query Parameters:**
- `company_id`: Company ID (required)
- `date`: Specific date (YYYY-MM-DD, default: today)

**Response:**
```json
{
  "date": "2025-01-15",
  "company_id": 1,
  "total_debit": 125000.00,
  "total_credit": 125000.00,
  "transaction_count": 15,
  "voucher_types": {
    "Pledge": 5,
    "Payment": 8,
    "Expense": 2
  },
  "summary_by_account": [
    {
      "account_name": "Cash in Hand",
      "account_code": "1001",
      "total_debit": 25000.00,
      "total_credit": 15000.00,
      "net_change": 10000.00
    }
  ]
}
```

### Date Range Report
```http
GET /api/v1/daybook/date_range
Authorization: Bearer <token>
```

**Query Parameters:**
- `company_id`: Company ID (required)
- `from_date`: Start date (YYYY-MM-DD)
- `to_date`: End date (YYYY-MM-DD)
- `account_id`: Filter by specific account (optional)

### Export Transactions
```http
GET /api/v1/daybook/export
Authorization: Bearer <token>
```

**Query Parameters:**
- `company_id`: Company ID (required)
- `from_date`: Start date
- `to_date`: End date
- `format`: Export format (json, csv)

---

## 🏦 Bank Management

### List Banks
```http
GET /banks
Authorization: Bearer <token>
```

### Create Bank Account
```http
POST /banks
Authorization: Bearer <token>
Content-Type: application/json

{
  "bank_name": "State Bank of India",
  "branch_name": "Main Branch",
  "account_number": "123456789012",
  "ifsc_code": "SBIN0001234",
  "account_holder_name": "ABC Pawn Shop",
  "company_id": 1
}
```

---

## 📦 Inventory Management

### Gold/Silver Rates
```http
GET /gold_silver_rates
Authorization: Bearer <token>
```

### Update Rates
```http
POST /gold_silver_rates
Authorization: Bearer <token>
Content-Type: application/json

{
  "date": "2025-01-15",
  "jewell_type_id": 1,
  "rate": 6500.00
}
```

### Jewell Types
```http
GET /jewell_types
Authorization: Bearer <token>
```

---

## 📁 File Upload

### Upload File
```http
POST /upload_file
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary-file-data>
company_id: 1
upload_type: "customer_id_proof" | "company_logo"
```

**Response:**
```json
{
  "filename": "customer_1_id_proof_20250115.jpg",
  "file_path": "/uploads/customer_1_id_proof_20250115.jpg",
  "file_size": 1024000,
  "upload_type": "customer_id_proof"
}
```

---

## 🔍 Search APIs

### Customer Search
```http
GET /customers/search?query=john
Authorization: Bearer <token>
```

### Jewell Design Search
```http
GET /jewell_designs/search?query=necklace
Authorization: Bearer <token>
```

---

## ❤️ Health Check

### Health Status
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-15T10:30:00Z",
  "database": "connected",
  "environment": "development"
}
```

---

## 📝 Request/Response Formats

### Common Response Structure
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

---

## 🔒 Security Notes

1. **Rate Limiting**: 100 requests per minute per IP
2. **Token Expiry**: JWT tokens expire in 30 minutes
3. **CORS**: Configured for specific origins
4. **Input Validation**: All inputs are validated and sanitized
5. **SQL Injection Protection**: Parameterized queries used throughout
6. **Password Security**: bcrypt hashing with salt

---

## 📞 API Support

- **Interactive Documentation**: Visit `/docs` when running the server
- **Postman Collection**: Available in repository
- **SDK Libraries**: Python, JavaScript SDKs available
- **Support Email**: api-support@rnrinfo.dev

---

**Last Updated**: January 15, 2025
**API Version**: 1.0.0
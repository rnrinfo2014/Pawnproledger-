# Bank Management API Documentation

## Overview
The Bank Management API provides simple CRUD operations for managing basic bank information in the PawnPro system. Each bank record contains only essential information: bank name, branch name, account name, and status.

## Database Schema

### Banks Table (Simplified)
```sql
CREATE TABLE banks (
    id SERIAL PRIMARY KEY,
    bank_name VARCHAR(200) NOT NULL,
    branch_name VARCHAR(200),
    account_name VARCHAR(200),
    status VARCHAR(20) DEFAULT 'active',
    company_id INTEGER NOT NULL REFERENCES companies(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT banks_company_bank_unique UNIQUE (company_id, bank_name)
);
```

## API Endpoints

### 1. Create Bank
**POST** `/banks/`

Creates a new bank record with essential information only.

**Request Body:**
```json
{
    "bank_name": "State Bank of India",
    "branch_name": "Main Branch",
    "account_name": "PawnPro Company Ltd",
    "status": "active"
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "bank_name": "State Bank of India",
    "branch_name": "Main Branch", 
    "account_name": "PawnPro Company Ltd",
    "status": "active",
    "company_id": 1,
    "created_at": "2025-09-15T10:30:00Z",
    "updated_at": null
}
```

### 2. Get All Banks
**GET** `/banks/`

Retrieves all banks for the authenticated user's company with optional filtering.

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum number of records to return (default: 100)
- `status` (string): Filter by status ('active', 'inactive')
- `search` (string): Search in bank name, branch name, or account name

**Examples:**
```bash
# Get all banks
GET /banks/

# Get only active banks
GET /banks/?status=active

# Search for banks
GET /banks/?search=State Bank

# Pagination
GET /banks/?skip=10&limit=20
```

### 3. Get Bank by ID
**GET** `/banks/{bank_id}`

Retrieves a specific bank by ID.

**Response (200 OK):**
```json
{
    "id": 1,
    "bank_name": "State Bank of India",
    "branch_name": "Main Branch",
    "account_name": "PawnPro Company Ltd",
    "status": "active",
    "company_id": 1,
    "created_at": "2025-09-15T10:30:00Z",
    "updated_at": null
}
```

### 4. Update Bank
**PUT** `/banks/{bank_id}`

Updates an existing bank record. Only provided fields are updated.

**Request Body (partial update):**
```json
{
    "account_name": "PawnPro Solutions Ltd",
    "status": "active"
}
```

### 5. Deactivate Bank (Soft Delete)
**DELETE** `/banks/{bank_id}`

Soft deletes a bank by setting its status to 'inactive'.

**Response (200 OK):**
```json
{
    "message": "Bank deactivated successfully"
}
```

### 6. Activate Bank
**POST** `/banks/{bank_id}/activate`

Reactivates an inactive bank by setting its status to 'active'.

**Response (200 OK):**
```json
{
    "message": "Bank activated successfully"
}
```

## Usage Examples

### cURL Examples

#### Create a Bank
```bash
curl -X POST "http://localhost:8000/banks/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bank_name": "HDFC Bank",
    "branch_name": "Corporate Branch",
    "account_name": "PawnPro Solutions",
    "status": "active"
  }'
```

#### Search Banks
```bash
curl -X GET "http://localhost:8000/banks/?search=HDFC&status=active" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Update Bank
```bash
curl -X PUT "http://localhost:8000/banks/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_name": "Updated Account Name"
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

# Create a bank
bank_data = {
    "bank_name": "ICICI Bank",
    "branch_name": "Business Banking",
    "account_name": "My Company Account",
    "status": "active"
}
response = requests.post("http://localhost:8000/banks/", 
                        json=bank_data, 
                        headers=headers)
bank = response.json()

# Get all active banks
banks = requests.get("http://localhost:8000/banks/?status=active", 
                    headers=headers).json()

# Update bank
update_data = {"account_name": "New Account Name"}
requests.put(f"http://localhost:8000/banks/{bank['id']}", 
            json=update_data, 
            headers=headers)
```

## Request/Response Models

### BankCreate
```json
{
    "bank_name": "string (required, max 200 chars)",
    "branch_name": "string (optional, max 200 chars)",
    "account_name": "string (optional, max 200 chars)", 
    "status": "string (optional, default: 'active')"
}
```

### BankUpdate
```json
{
    "bank_name": "string (optional, max 200 chars)",
    "branch_name": "string (optional, max 200 chars)",
    "account_name": "string (optional, max 200 chars)",
    "status": "string (optional)"
}
```

### Bank Response
```json
{
    "id": "integer",
    "bank_name": "string",
    "branch_name": "string",
    "account_name": "string",
    "status": "string",
    "company_id": "integer",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

## Business Rules

### 1. Unique Constraint
- Each company can only have one bank with the same bank_name
- This prevents duplicate bank entries per company

### 2. Company Isolation
- Users can only access banks belonging to their company
- All operations are automatically filtered by company_id

### 3. Soft Delete
- Banks are not permanently deleted
- Deactivation sets status to 'inactive' for audit trails
- Inactive banks can be reactivated

### 4. Search Functionality
- Search across: bank name, branch name, account name
- Case-insensitive search using ILIKE
- Supports partial matches

## Error Responses

### 400 Bad Request
```json
{
    "detail": "Bank with same name already exists for this company"
}
```

### 404 Not Found
```json
{
    "detail": "Bank not found"
}
```

### 401 Unauthorized
```json
{
    "detail": "Could not validate credentials"
}
```

## Database Migration

To migrate existing banks table to simplified version:
```bash
python migrate_bank_table.py
```

This will:
- Remove unnecessary columns (IFSC, address, contact details, etc.)
- Rename account_holder_name to account_name
- Preserve existing data where possible
- Update constraints for simplified structure

## Testing

Run the simplified test suite:
```bash
python test_bank_api.py
```

The test suite covers:
- ✅ Authentication
- ✅ Bank creation with minimal data
- ✅ Reading all banks
- ✅ Reading bank by ID
- ✅ Updating bank information
- ✅ Search and filtering
- ✅ Duplicate prevention
- ✅ Soft delete (deactivation)
- ✅ Reactivation

## Security Features

- 🔐 JWT token authentication required for all endpoints
- 🏢 Company-level data isolation
- 🛡️ SQL injection prevention through SQLAlchemy ORM
- ✅ Input validation through Pydantic models
- 📊 Audit trail with created_at and updated_at timestamps

## Simplified Benefits

- 🚀 **Faster Performance** - Fewer fields to process and validate
- 📝 **Easier Integration** - Simple API with only essential fields
- 💾 **Reduced Storage** - Smaller database footprint
- 🎯 **Focused Functionality** - Only what you need for bank management
- 🔧 **Easier Maintenance** - Less complex data model
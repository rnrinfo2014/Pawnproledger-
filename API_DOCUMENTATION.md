# PawnSoft API Documentation

**Generated on:** October 18, 2025  
**Total Endpoints:** 148  
**Base URL:** http://localhost:8000

---

## 📊 API Overview

| Statistic | Count |
|-----------|-------|
| Total Endpoints | 148 |
| Total Modules | 7 |
| GET Endpoints | 78 |
| POST Endpoints | 31 |
| PUT Endpoints | 20 |
| DELETE Endpoints | 19 |

---

## 🔗 API Access Points

- **Base URL:** http://localhost:8000
- **Interactive Documentation (Swagger UI):** http://localhost:8000/docs
- **Alternative Documentation (ReDoc):** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

---

## 📂 API Modules

### 🔵 Pledge Payments (2 endpoints)
API module for handling multiple pledge payments and pending pledge calculations.

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 1 | 🟢 GET | `/api/v1/pledge-payments/customers/{customer_id}/pending` | Get Customer Pending Pledges |
| 2 | 🔵 POST | `/api/v1/pledge-payments/customers/{customer_id}/multiple-payment` | Create Multiple Pledge Payment |

**Key Features:**
- Fetch customer's pending pledges with detailed calculations
- Process multiple pledge payments in a single transaction
- Automatic interest calculation and balance updates
- Receipt generation for multiple pledges

---

### 🟡 Payment Management (4 endpoints)
Advanced payment receipt management with transaction reversal capabilities.

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 1 | 🟡 PUT | `/api/v1/payment-management/payment/{payment_id}` | Update Payment Receipt |
| 2 | 🔴 DELETE | `/api/v1/payment-management/payment/{payment_id}` | Delete Payment Receipt |
| 3 | 🟢 GET | `/api/v1/payment-management/payment/{payment_id}/can-modify` | Check Payment Modifiable |
| 4 | 🟢 GET | `/api/v1/payment-management/recent-modifications` | Get Recent Payment Modifications |

**Key Features:**
- Update payment receipts with automatic transaction reversal
- Delete payments with complete accounting integrity
- Safety restrictions (age limits, admin access)
- Comprehensive audit trails
- Automatic pledge status recalculation

---

### 📊 Customer Ledger Reports (4 endpoints)
Comprehensive customer financial reporting and ledger management.

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 1 | 🟢 GET | `/api/v1/customer-ledger/customer/{customer_id}/statement` | Get Customer Ledger Statement |
| 2 | 🟢 GET | `/api/v1/customer-ledger/customer/{customer_id}/financial-year-summary` | Get Customer Financial Year Summary |
| 3 | 🟢 GET | `/api/v1/customer-ledger/customer/{customer_id}/current-balance` | Get Customer Current Balance |
| 4 | 🟢 GET | `/api/v1/customer-ledger/customers/ledger-summary` | Get All Customers Ledger Summary |

**Key Features:**
- Date-wise customer statements
- Financial year summaries
- Current balance calculations
- All customers overview with filtering options

---

### 🧾 Payment Receipts (8 endpoints)
Receipt management, search, and retrieval system.

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 1 | 🟢 GET | `/api/v1/receipts/` | Get Receipts |
| 2 | 🟢 GET | `/api/v1/receipts/receipt/{receipt_no}` | Get Receipt By Number |
| 3 | 🟢 GET | `/api/v1/receipts/payment/{payment_id}` | Get Receipt By Payment Id |
| 4 | 🟢 GET | `/api/v1/receipts/customer/{customer_id}` | Get Customer Receipts |
| 5 | 🟢 GET | `/api/v1/receipts/pledge/{pledge_id}` | Get Pledge Receipts |
| 6 | 🔵 POST | `/api/v1/receipts/search` | Search Receipts |
| 7 | 🟢 GET | `/api/v1/receipts/summary` | Get Receipt Summary |
| 8 | 🟢 GET | `/api/v1/receipts/latest` | Get Latest Receipts |

**Key Features:**
- Receipt search by multiple criteria
- Customer and pledge receipt history
- Receipt summaries and statistics
- PDF generation capabilities

---

### 💰 Chart of Accounts (8 endpoints)
Financial accounting structure and account management.

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 1 | 🟢 GET | `/api/v1/coa/accounts` | Get All Accounts |
| 2 | 🔵 POST | `/api/v1/coa/accounts` | Create Account |
| 3 | 🟢 GET | `/api/v1/coa/accounts/tree` | Get Accounts Tree |
| 4 | 🟢 GET | `/api/v1/coa/accounts/{account_id}` | Get Account |
| 5 | 🟡 PUT | `/api/v1/coa/accounts/{account_id}` | Update Account |
| 6 | 🔴 DELETE | `/api/v1/coa/accounts/{account_id}` | Delete Account |
| 7 | 🟢 GET | `/api/v1/coa/account-types` | Get Account Types |
| 8 | 🔵 POST | `/api/v1/coa/initialize-pawn-coa` | Initialize Pawn Coa |

**Key Features:**
- Complete chart of accounts management
- Hierarchical account structure
- Account type management
- Pawn shop specific COA initialization

---

### 📖 Daybook (6 endpoints)
Daily transaction summaries and financial reporting.

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 1 | 🟢 GET | `/api/v1/daybook/daily-summary` | Get Daily Summary |
| 2 | 🟢 GET | `/api/v1/daybook/date-range-summary` | Get Date Range Summary |
| 3 | 🟢 GET | `/api/v1/daybook/account-wise-summary` | Get Account Wise Summary |
| 4 | 🟢 GET | `/api/v1/daybook/voucher-wise-summary` | Get Voucher Wise Summary |
| 5 | 🟢 GET | `/api/v1/daybook/current-month-summary` | Get Current Month Summary |
| 6 | 🟢 GET | `/api/v1/daybook/export-daybook` | Export Daybook Data |

**Key Features:**
- Daily transaction summaries
- Date range analysis
- Account and voucher wise breakdowns
- Data export capabilities

---

### 🏢 Core Business Operations (116 endpoints)
Primary business functionality and entity management.

#### Authentication & Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| 🟢 GET | `/health` | Health Check |
| 🔵 POST | `/token` | Login For Access Token |
| 🟢 GET | `/users/me` | Read Current User |
| 🔵 POST | `/users` | Create User |
| 🟢 GET | `/users` | Read Users |
| 🟢 GET | `/users/{user_id}` | Read User |
| 🟡 PUT | `/users/{user_id}` | Update User |
| 🔴 DELETE | `/users/{user_id}` | Delete User |

#### Companies & Areas
| Method | Endpoint | Description |
|--------|----------|-------------|
| 🟢 GET | `/companies` | Read Companies |
| 🔵 POST | `/companies` | Create Company |
| 🟢 GET | `/companies/{company_id}` | Read Company |
| 🟡 PUT | `/companies/{company_id}` | Update Company |
| 🔴 DELETE | `/companies/{company_id}` | Delete Company |
| 🟢 GET | `/areas` | Read Areas |
| 🔵 POST | `/areas` | Create Area |
| 🟢 GET | `/areas/{area_id}` | Read Area |
| 🟡 PUT | `/areas/{area_id}` | Update Area |
| 🔴 DELETE | `/areas/{area_id}` | Delete Area |

#### Gold/Silver Rates & Jewelry Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| 🟢 GET | `/gold_silver_rates` | Read Gold Silver Rates |
| 🔵 POST | `/gold_silver_rates` | Create Gold Silver Rate |
| 🟢 GET | `/gold_silver_rates/{rate_id}` | Read Gold Silver Rate |
| 🟡 PUT | `/gold_silver_rates/{rate_id}` | Update Gold Silver Rate |
| 🔴 DELETE | `/gold_silver_rates/{rate_id}` | Delete Gold Silver Rate |
| 🟢 GET | `/jewell_designs` | Read Jewell Designs |
| 🔵 POST | `/jewell_designs` | Create Jewell Design |
| 🟢 GET | `/jewell_designs/search` | Search Jewell Designs |
| 🟢 GET | `/jewell_designs/{design_id}` | Read Jewell Design |
| 🟡 PUT | `/jewell_designs/{design_id}` | Update Jewell Design |
| 🔴 DELETE | `/jewell_designs/{design_id}` | Delete Jewell Design |
| 🟢 GET | `/jewell_conditions` | Read Jewell Conditions |
| 🔵 POST | `/jewell_conditions` | Create Jewell Condition |
| 🟢 GET | `/jewell_conditions/{condition_id}` | Read Jewell Condition |
| 🟡 PUT | `/jewell_conditions/{condition_id}` | Update Jewell Condition |
| 🔴 DELETE | `/jewell_conditions/{condition_id}` | Delete Jewell Condition |
| 🟢 GET | `/jewell_types` | Read Jewell Types |
| 🔵 POST | `/jewell_types` | Create Jewell Type |
| 🟢 GET | `/jewell_types/{type_id}` | Read Jewell Type |
| 🟡 PUT | `/jewell_types/{type_id}` | Update Jewell Type |
| 🔴 DELETE | `/jewell_types/{type_id}` | Delete Jewell Type |
| 🟢 GET | `/jewell_rates` | Read Jewell Rates |
| 🔵 POST | `/jewell_rates` | Create Jewell Rate |
| 🟢 GET | `/jewell_rates/{rate_id}` | Read Jewell Rate |
| 🟡 PUT | `/jewell_rates/{rate_id}` | Update Jewell Rate |
| 🔴 DELETE | `/jewell_rates/{rate_id}` | Delete Jewell Rate |
| 🟢 GET | `/jewell_rates/by_type/{type_id}` | Read Jewell Rates By Type |

#### Schemes & Customer Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| 🟢 GET | `/schemes` | Read Schemes |
| 🔵 POST | `/schemes` | Create Scheme |
| 🟢 GET | `/schemes/{scheme_id}` | Read Scheme |
| 🟡 PUT | `/schemes/{scheme_id}` | Update Scheme |
| 🔴 DELETE | `/schemes/{scheme_id}` | Delete Scheme |
| 🟢 GET | `/customers` | Read Customers |
| 🔵 POST | `/customers` | Create Customer |
| 🟢 GET | `/customers/search` | Search Customers |
| 🟢 GET | `/customers/{customer_id}` | Read Customer |
| 🟡 PUT | `/customers/{customer_id}` | Update Customer |
| 🔴 DELETE | `/customers/{customer_id}` | Delete Customer |
| 🟢 GET | `/customers/{customer_id}/balance` | Get Customer COA Balance |
| 🔵 POST | `/customers/migrate-to-coa/{company_id}` | Migrate Customers To COA |
| 🟢 GET | `/customers/{customer_id}/coa-info` | Get Customer COA Info |

#### Items & File Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| 🟢 GET | `/items` | Read Items |
| 🔵 POST | `/items` | Create Item |
| 🟢 GET | `/items/{item_id}` | Read Item |
| 🟡 PUT | `/items/{item_id}` | Update Item |
| 🔴 DELETE | `/items/{item_id}` | Delete Item |
| 🔵 POST | `/upload/company-logo/{company_id}` | Upload Company Logo |
| 🔵 POST | `/upload/customer-photo/{customer_id}` | Upload Customer Photo |
| 🔵 POST | `/upload/customer-id-proof/{customer_id}` | Upload Customer ID Proof |
| 🔵 POST | `/upload/item-photos/{item_id}` | Upload Item Photos |
| 🟢 GET | `/files/{file_path}` | Get File |
| 🟢 GET | `/uploads/{file_path}` | Serve Uploaded File |

#### Accounting & Ledger
| Method | Endpoint | Description |
|--------|----------|-------------|
| 🟢 GET | `/accounts` | Read Accounts |
| 🔵 POST | `/accounts` | Create Account |
| 🟢 GET | `/accounts/{account_id}` | Read Account |
| 🟡 PUT | `/accounts/{account_id}` | Update Account |
| 🔴 DELETE | `/accounts/{account_id}` | Delete Account |
| 🟢 GET | `/vouchers` | Read Vouchers |
| 🔵 POST | `/vouchers` | Create Voucher |
| 🟢 GET | `/vouchers/{voucher_id}` | Read Voucher |
| 🟢 GET | `/ledger-entries` | Read Ledger Entries |
| 🔵 POST | `/ledger-entries` | Create Ledger Entry |

#### Pledge Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| 🔵 POST | `/pledges/` | Create Pledge |
| 🟢 GET | `/pledges/` | Read Pledges |
| 🟢 GET | `/pledges/{pledge_id}` | Read Pledge |
| 🟡 PUT | `/pledges/{pledge_id}` | Update Pledge |
| 🔴 DELETE | `/pledges/{pledge_id}` | Delete Pledge |
| 🟢 GET | `/pledges/{pledge_id}/detail` | Get Pledge Detail View |
| 🟡 PUT | `/pledges/{pledge_id}/comprehensive-update` | Update Pledge Comprehensive |
| 🔵 POST | `/pledges/with-items` | Create Pledge With Items |
| 🟡 PUT | `/pledges/{pledge_id}/with-items` | Update Pledge With Items |

#### Pledge Items
| Method | Endpoint | Description |
|--------|----------|-------------|
| 🔵 POST | `/pledge-items/` | Create Pledge Item |
| 🟢 GET | `/pledge-items/` | Read Pledge Items |
| 🟢 GET | `/pledges/{pledge_id}/items` | Read Pledge Items By Pledge |
| 🔴 DELETE | `/pledges/{pledge_id}/items` | Delete All Pledge Items |
| 🟢 GET | `/pledge-items/{item_id}` | Read Pledge Item |
| 🟡 PUT | `/pledge-items/{item_id}` | Update Pledge Item |
| 🔴 DELETE | `/pledge-items/{item_id}` | Delete Pledge Item |

#### Customer-Pledge Relationships
| Method | Endpoint | Description |
|--------|----------|-------------|
| 🟢 GET | `/customers/{customer_id}/pledges/active` | Get Customer Active Pledges |
| 🟢 GET | `/customers/{customer_id}/pledges` | Get Customer All Pledges |
| 🟢 GET | `/customers/{customer_id}/pending-pledges` | Get Customer Pending Pledges |
| 🔵 POST | `/customers/{customer_id}/multiple-pledge-payment` | Create Multiple Pledge Payment |
| 🟢 GET | `/schemes/{scheme_id}/pledges/active` | Get Scheme Active Pledges |

#### Banks
| Method | Endpoint | Description |
|--------|----------|-------------|
| 🔵 POST | `/banks/` | Create Bank |
| 🟢 GET | `/banks/` | Read Banks |
| 🟢 GET | `/banks/{bank_id}` | Read Bank |
| 🟡 PUT | `/banks/{bank_id}` | Update Bank |
| 🔴 DELETE | `/banks/{bank_id}` | Delete Bank |
| 🔵 POST | `/banks/{bank_id}/activate` | Activate Bank |

#### Individual Pledge Payments
| Method | Endpoint | Description |
|--------|----------|-------------|
| 🔵 POST | `/pledge-payments/` | Create Pledge Payment |
| 🟢 GET | `/pledge-payments/` | Get Pledge Payments |
| 🟢 GET | `/pledge-payments/{payment_id}` | Get Pledge Payment |
| 🟡 PUT | `/pledge-payments/{payment_id}` | Update Pledge Payment |
| 🔴 DELETE | `/pledge-payments/{payment_id}` | Delete Pledge Payment |
| 🟢 GET | `/pledges/{pledge_id}/payments` | Get Payments By Pledge |
| 🟢 GET | `/pledges/{pledge_id}/payment-summary` | Get Pledge Payment Summary |
| 🟢 GET | `/api/pledges/{pledge_id}/settlement` | Get Pledge Settlement Details |

---

## ⭐ Key Business Workflows

### 🔐 Authentication Flow
1. **POST** `/token` - Login with credentials to get access token
2. **GET** `/users/me` - Verify current user details

### 👥 Customer Management Flow
1. **POST** `/customers` - Create new customer
2. **GET** `/customers/search` - Search for existing customers
3. **GET** `/customers/{customer_id}` - Get customer details
4. **GET** `/customers/{customer_id}/balance` - Check customer COA balance

### 💎 Pledge Creation Flow
1. **POST** `/pledges/with-items` - Create pledge with jewelry items
2. **GET** `/pledges/{pledge_id}/detail` - Get complete pledge details
3. **PUT** `/pledges/{pledge_id}/comprehensive-update` - Update pledge details

### 💰 Payment Processing Flow
1. **GET** `/api/v1/pledge-payments/customers/{customer_id}/pending` - Get pending pledges
2. **POST** `/api/v1/pledge-payments/customers/{customer_id}/multiple-payment` - Process multiple payments
3. **GET** `/api/v1/receipts/receipt/{receipt_no}` - Get payment receipt

### 🔄 Payment Management Flow
1. **GET** `/api/v1/payment-management/payment/{payment_id}/can-modify` - Check if modifiable
2. **PUT** `/api/v1/payment-management/payment/{payment_id}` - Update payment
3. **DELETE** `/api/v1/payment-management/payment/{payment_id}` - Delete payment
4. **GET** `/api/v1/payment-management/recent-modifications` - View recent changes

### 📊 Reporting Flow
1. **GET** `/api/v1/customer-ledger/customer/{customer_id}/statement` - Customer statement
2. **GET** `/api/v1/daybook/daily-summary` - Daily transaction summary
3. **GET** `/api/v1/receipts/summary` - Payment receipt summaries

---

## 🎯 HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|--------|
| 200 | OK | Successful GET, PUT requests |
| 201 | Created | Successful POST requests |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation errors |
| 500 | Internal Server Error | Server-side errors |

---

## 🔧 Common Query Parameters

### Pagination Parameters
- `skip` - Number of records to skip (default: 0)
- `limit` - Maximum number of records to return (default: 100)

### Filtering Parameters
- `company_id` - Filter by company ID
- `customer_id` - Filter by customer ID
- `start_date` - Start date for date range queries
- `end_date` - End date for date range queries
- `is_active` - Filter by active status (true/false)

### Sorting Parameters
- `sort_by` - Field to sort by
- `sort_order` - Sort order (asc/desc)

---

## 📝 Request/Response Examples

### Authentication Example
```bash
# Login to get access token
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Create Customer Example
```bash
curl -X POST "http://localhost:8000/customers" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "phone": "9876543210",
    "address": "123 Main St",
    "company_id": 1
  }'
```

### Multiple Pledge Payment Example
```bash
curl -X POST "http://localhost:8000/api/v1/pledge-payments/customers/1/multiple-payment" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pledge_payments": [
      {"pledge_id": 1, "amount": 1000.00, "payment_type": "interest"},
      {"pledge_id": 2, "amount": 500.00, "payment_type": "partial"}
    ],
    "total_amount": 1500.00,
    "payment_method": "cash"
  }'
```

---

## 🚨 Important Notes

### Security
- All endpoints except `/health` and `/token` require authentication
- Use Bearer token in Authorization header
- Tokens expire after configured time period

### Rate Limiting
- API may implement rate limiting in production
- Recommended to implement client-side retry logic with exponential backoff

### Data Validation
- All POST/PUT requests validate input data
- Validation errors return 422 status with detailed error messages
- Required fields must be provided

### Transaction Integrity
- Payment operations are atomic
- Failed transactions are automatically rolled back
- Accounting entries maintain double-entry bookkeeping

---

**Documentation Last Updated:** October 18, 2025  
**API Version:** 1.0  
**Contact:** PawnSoft Development Team
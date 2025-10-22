# API Structure Documentation

## 🏗️ Proper API Organization Structure

### 📁 Current API Structure:

```
src/core/
├── main.py                  # Main FastAPI app + core endpoints
├── coa_api.py              # Chart of Accounts API
├── daybook_api.py          # Daybook/Transaction Reports API  
├── pledge_payment_api.py   # Pledge Payment Operations API (NEW!)
└── database.py             # Database connection
```

### 🎯 API Modules Overview:

#### 1. **Chart of Accounts API** (`coa_api.py`)
- **Prefix**: `/api/v1/coa`
- **Purpose**: Account management, account hierarchy
- **Endpoints**:
  - `GET /api/v1/coa/accounts` - List all accounts
  - `POST /api/v1/coa/accounts` - Create new account
  - `PUT /api/v1/coa/accounts/{id}` - Update account
  - `DELETE /api/v1/coa/accounts/{id}` - Delete account

#### 2. **Daybook API** (`daybook_api.py`) 
- **Prefix**: `/api/v1/daybook`
- **Purpose**: Daily transaction reports, summaries
- **Endpoints**:
  - `GET /api/v1/daybook/summary` - Daily summary
  - `GET /api/v1/daybook/transactions` - Transaction list
  - `GET /api/v1/daybook/balance-sheet` - Balance sheet report

#### 3. **Pledge Payment API** (`pledge_payment_api.py`) ⭐ **NEW!**
- **Prefix**: `/api/v1/pledge-payments` 
- **Purpose**: Pledge payment operations
- **Endpoints**:
  - `GET /api/v1/pledge-payments/customers/{id}/pending` - Pending pledges
  - `POST /api/v1/pledge-payments/customers/{id}/multiple-payment` - Multiple payment

#### 4. **Receipt API** (`receipt_api.py`) ⭐ **NEW!**
- **Prefix**: `/api/v1/receipts`
- **Purpose**: Payment receipt management and retrieval
- **Endpoints**:
  - `GET /api/v1/receipts/` - List all receipts with pagination
  - `GET /api/v1/receipts/receipt/{receipt_no}` - Get receipt by number
  - `GET /api/v1/receipts/payment/{payment_id}` - Get receipt by payment ID
  - `GET /api/v1/receipts/customer/{customer_id}` - Get customer receipts
  - `GET /api/v1/receipts/pledge/{pledge_id}` - Get pledge receipts
  - `POST /api/v1/receipts/search` - Advanced receipt search
  - `GET /api/v1/receipts/summary` - Receipt analytics
  - `GET /api/v1/receipts/latest` - Latest receipts

#### 5. **Main API** (`main.py`)
- **Purpose**: Core business operations (pledges, customers, schemes)
- **Contains**: Customer management, pledge creation, scheme management

---

## 🚀 New API Endpoints Available

### 🔗 Updated Endpoint URLs:

**Before (in main.py):**
```
GET /customers/{id}/pending-pledges
POST /customers/{id}/multiple-pledge-payment
```

**After (in pledge_payment_api.py):**
```
GET /api/v1/pledge-payments/customers/{id}/pending
POST /api/v1/pledge-payments/customers/{id}/multiple-payment
```

### 🎯 Benefits of Separation:

1. **Organized Code**: Each API module handles specific functionality
2. **Easy Maintenance**: Find and update APIs quickly
3. **Clear Documentation**: Grouped by business function
4. **Scalability**: Add new modules easily
5. **Team Development**: Different developers can work on different modules

---

## 📋 How to Test New Separated APIs

### 1. **Pending Pledges** (Moved to pledge_payment_api.py):
```bash
GET http://localhost:8000/api/v1/pledge-payments/customers/3/pending
```

### 2. **Multiple Payment** (Moved to pledge_payment_api.py):
```bash
POST http://localhost:8000/api/v1/pledge-payments/customers/3/multiple-payment
```

### 3. **Chart of Accounts**:
```bash
GET http://localhost:8000/api/v1/coa/accounts
```

### 4. **Daybook**:
```bash
GET http://localhost:8000/api/v1/daybook/summary
```

---

## 🛠️ How to Create More API Modules

### Example: Customer API Module

```python
# src/core/customer_api.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/customers", tags=["Customers"])

@router.get("/")
def get_customers():
    pass

@router.post("/")  
def create_customer():
    pass
```

### Add to main.py:
```python
from src.core.customer_api import router as customer_router
app.include_router(customer_router)
```

---

## 📖 Swagger Documentation

Visit: `http://localhost:8000/docs`

APIs are now organized by tags:
- **Chart of Accounts** - COA operations
- **Daybook** - Transaction reports  
- **Pledge Payments** - Payment operations ⭐ NEW!
- **Default** - Core operations (customers, pledges, schemes)

---

This structure makes your API much more professional and maintainable! 🎯
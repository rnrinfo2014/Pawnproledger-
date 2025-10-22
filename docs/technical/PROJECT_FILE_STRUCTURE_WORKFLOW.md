"""
📁 PAWNSOFT PROJECT - FILE STRUCTURE & WORKFLOW DETAILED
========================================================

🎯 PROJECT மு FILE-ல என்னா இருக்கு?
====================================

Let me explain each file-ன் purpose and how they work together:

📁 ROOT DIRECTORY STRUCTURE:
===========================

PawnProApi/                          # Main project folder
├── 🎯 CORE API FILES
│   ├── main.py                      # ⭐ All API endpoints (மிக முக்கியம்)
│   ├── models.py                    # 🗃️ Database table definitions  
│   ├── database.py                  # 🔌 PostgreSQL connection
│   ├── auth.py                      # 🔐 JWT authentication system
│   └── config.py                    # ⚙️ App settings & environment
│
├── 🧠 BUSINESS LOGIC FILES  
│   ├── customer_coa_manager.py      # 👤 Customer accounting logic
│   ├── pledge_accounting_manager.py # 💰 Pledge accounting system
│   └── security_middleware.py       # 🛡️ Security & rate limiting
│
├── 🗃️ DATABASE FILES
│   ├── create_tables.py             # 🏗️ Initial database setup
│   ├── migrate_*.py                 # 🔄 Database schema updates
│   └── *.sql                        # 📜 SQL scripts
│
├── 🧪 TESTING & UTILITIES
│   ├── test_*.py                    # 🧪 Test scripts
│   ├── clear_*.py                   # 🧹 Data cleanup utilities
│   └── setup_*.py                   # ⚙️ Setup scripts
│
└── 📋 CONFIGURATION
    ├── requirements.txt             # 📦 Python dependencies
    ├── pyproject.toml              # 🔧 Project metadata
    └── README.md                   # 📖 Documentation

🔍 DETAILED FILE BREAKDOWN:
==========================

1. 🎯 MAIN.PY (Entry Point - 3847 lines!)
-------------------------------------------
இதுல தான் எல்லா API endpoints இருக்கு:

FILE STRUCTURE:
```python
# IMPORTS SECTION
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session  
from models import Customer, Pledge, Payment
from auth import get_current_user
from customer_coa_manager import create_customer_coa_account

# APP CREATION
app = FastAPI(title="PawnSoft API")

# MIDDLEWARE SETUP
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

# AUTHENTICATION ENDPOINTS
@app.post("/token")                  # Login
@app.post("/register")               # User registration

# CUSTOMER MANAGEMENT 
@app.post("/customers/")             # Create customer
@app.get("/customers/")              # List customers  
@app.get("/customers/{id}")          # Get specific customer
@app.put("/customers/{id}")          # Update customer
@app.delete("/customers/{id}")       # Delete customer

# PLEDGE MANAGEMENT
@app.post("/pledges/")               # Create new pledge
@app.get("/pledges/")                # List pledges
@app.get("/pledges/{id}")            # Get specific pledge
@app.put("/pledges/{id}")            # Update pledge

# PAYMENT PROCESSING  
@app.post("/pledge-payments/")       # Record payment
@app.get("/pledge-payments/")        # List payments
@app.get("/pledge-payments/{id}")    # Get payment details

# REPORTING ENDPOINTS
@app.get("/reports/daily-summary")   # Daily reports
@app.get("/reports/customer-balance") # Customer balances

# UTILITY ENDPOINTS
@app.get("/health")                  # Health check
@app.get("/")                        # Welcome message
```

WORKFLOW IN MAIN.PY:
```
Request comes in → Route matching → Authentication check → 
Business logic → Database operation → Response sent back
```

2. 🗃️ MODELS.PY (Database Schema)
----------------------------------
எல்லா database table-களும் இங்க define பண்ணியிருக்கு:

```python
# Base class for all models
Base = declarative_base()

# Company table (multi-tenant support)
class Company(Base):
    __tablename__ = "companies"
    company_id = Column(Integer, primary_key=True)
    company_name = Column(String(200))

# User table (authentication)  
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(255))
    company_id = Column(Integer, ForeignKey("companies.company_id"))

# Customer table (main business entity)
class Customer(Base):
    __tablename__ = "customers" 
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(15))
    address = Column(Text)
    coa_account_id = Column(Integer, ForeignKey("master_accounts.id"))
    company_id = Column(Integer, ForeignKey("companies.company_id"))

# Chart of Accounts (accounting structure)
class MasterAccount(Base):
    __tablename__ = "master_accounts"
    id = Column(Integer, primary_key=True)  
    account_code = Column(String(20), unique=True)
    account_name = Column(String(200))
    account_type = Column(String(50))  # Asset, Liability, Income, Expense

# Pledge table (core business logic)
class Pledge(Base):
    __tablename__ = "pledges"
    pledge_id = Column(Integer, primary_key=True)
    pledge_no = Column(String(20), unique=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    loan_amount = Column(Numeric(15,2))
    interest_rate = Column(Numeric(5,2)) 
    final_amount = Column(Numeric(15,2))
    status = Column(String(20), default="active")

# Payment table (transaction records)
class PledgePayment(Base):
    __tablename__ = "pledge_payments"
    payment_id = Column(Integer, primary_key=True)
    pledge_id = Column(Integer, ForeignKey("pledges.pledge_id"))
    amount = Column(Numeric(15,2))
    balance_amount = Column(Numeric(15,2))
    payment_method = Column(String(20))

# Accounting entries (double-entry bookkeeping)
class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    entry_id = Column(Integer, primary_key=True)
    voucher_id = Column(Integer, ForeignKey("voucher_master.voucher_id"))
    account_id = Column(Integer, ForeignKey("master_accounts.id"))
    debit = Column(Numeric(15,2), default=0)
    credit = Column(Numeric(15,2), default=0)
    reference_type = Column(String(20))  # 'pledge', 'payment'
    reference_id = Column(Integer)
```

3. 🔌 DATABASE.PY (Connection Management)
-----------------------------------------
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

# Database URL from environment
DATABASE_URL = settings.database_url

# Create engine (connection pool)
engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # Connection pool size
    max_overflow=30,        # Additional connections
    pool_recycle=3600      # Recycle connections hourly
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False, 
    bind=engine
)

# Dependency for FastAPI
def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db           # Provide session to endpoint
    finally:
        db.close()         # Always close session
```

4. 🔐 AUTH.PY (Security System)
-------------------------------
```python
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"])

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""  
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    # Token validation logic
    # Return user object
```

5. 👤 CUSTOMER_COA_MANAGER.PY (Customer Accounting)
--------------------------------------------------
```python
def create_customer_coa_account(db: Session, customer_id: int, customer_name: str, company_id: int):
    """
    Auto-create Chart of Accounts entry for new customer
    
    Creates account like: 2001-001, 2001-002, etc.
    Account name: "Customer Name - Customer Account"
    """
    
    # Find next account number
    last_account = db.query(MasterAccount).filter(
        MasterAccount.account_code.like("2001-%"),
        MasterAccount.company_id == company_id
    ).order_by(MasterAccount.account_code.desc()).first()
    
    # Generate new account code
    if last_account:
        last_num = int(last_account.account_code.split("-")[1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    account_code = f"2001-{new_num:03d}"
    
    # Create account  
    coa_account = MasterAccount(
        account_code=account_code,
        account_name=f"{customer_name} - Customer Account",
        account_type="Asset",
        company_id=company_id
    )
    
    db.add(coa_account)
    db.flush()
    
    return {"account_id": coa_account.id, "account_code": account_code}
```

6. 💰 PLEDGE_ACCOUNTING_MANAGER.PY (Transaction Logic)
-----------------------------------------------------
```python
def create_complete_pledge_accounting(db: Session, pledge: Pledge, customer: Customer):
    """
    Create double-entry bookkeeping for pledge creation
    
    Entries:
    1. Customer Account Dr. (customer owes us)
    2. Cash Account Cr. (we gave cash)  
    3. Interest Income Cr. (if first payment exists)
    """
    
    # Create voucher
    voucher = VoucherMaster(
        voucher_date=pledge.created_at.date(),
        voucher_type="pledge",
        description=f"Pledge {pledge.pledge_no} created for {customer.name}",
        total_amount=pledge.loan_amount
    )
    db.add(voucher)
    db.flush()
    
    # Entry 1: Customer owes us (Asset increase)
    customer_entry = LedgerEntry(
        voucher_id=voucher.voucher_id,
        account_id=customer.coa_account_id,
        debit=pledge.loan_amount,
        credit=0,
        description=f"Pledge {pledge.pledge_no} - Loan given",
        reference_type="pledge",
        reference_id=pledge.pledge_id
    )
    
    # Entry 2: Cash given (Asset decrease)  
    cash_account = db.query(MasterAccount).filter(
        MasterAccount.account_code == "1001"  # Cash account
    ).first()
    
    cash_entry = LedgerEntry(
        voucher_id=voucher.voucher_id,
        account_id=cash_account.id,
        debit=0,
        credit=pledge.loan_amount,
        description=f"Pledge {pledge.pledge_no} - Cash disbursed",
        reference_type="pledge", 
        reference_id=pledge.pledge_id
    )
    
    db.add_all([customer_entry, cash_entry])
    db.commit()
```

🔄 COMPLETE REQUEST WORKFLOW:
============================

Let's trace a CUSTOMER CREATION request:

STEP 1: Request Arrives
```
POST /customers/
{
  "name": "ராமு",
  "phone": "9876543210"
}
```

STEP 2: FastAPI Route Matching (main.py)
```python
@app.post("/customers/", response_model=Customer)
def create_customer(
    customer: CustomerCreate,                              # ← Pydantic validation
    db: Session = Depends(get_db),                        # ← Database session
    current_user: UserModel = Depends(get_current_user)   # ← Authentication
):
```

STEP 3: Dependency Injection
```
get_db() → Creates database session
get_current_user() → Validates JWT token → Returns user object  
CustomerCreate → Validates input data → Creates Pydantic model
```

STEP 4: Business Logic Execution  
```python
# Create customer record
db_customer = CustomerModel(
    name=customer.name,
    phone=customer.phone,
    company_id=current_user.company_id  # Multi-tenant isolation
)

# Save to database  
db.add(db_customer)
db.flush()  # Get auto-generated ID

# Create COA account (customer_coa_manager.py)
coa_result = create_customer_coa_account(
    db=db,
    customer_id=db_customer.id, 
    customer_name=customer.name,
    company_id=current_user.company_id
)

# Link customer to COA account
db_customer.coa_account_id = coa_result['account_id']

# Commit transaction
db.commit()
db.refresh(db_customer)  # Reload from DB with all fields
```

STEP 5: Database Operations
```sql
-- Insert customer
INSERT INTO customers (name, phone, company_id) 
VALUES ('ராமு', '9876543210', 1);

-- Insert COA account  
INSERT INTO master_accounts (account_code, account_name, account_type, company_id)
VALUES ('2001-015', 'ராமு - Customer Account', 'Asset', 1);

-- Update customer with COA reference
UPDATE customers SET coa_account_id = 78 WHERE id = 156;
```

STEP 6: Response Generation
```python
return db_customer  # FastAPI automatically converts to JSON
```

STEP 7: Response Sent
```json
{
  "id": 156,
  "name": "ராமு", 
  "phone": "9876543210",
  "coa_account_id": 78,
  "company_id": 1,
  "created_at": "2025-10-13T15:30:00"
}
```

📊 FILE DEPENDENCIES MAP:
========================

```
main.py
├── imports models.py          (database tables)
├── imports database.py        (DB connection) 
├── imports auth.py            (authentication)
├── imports config.py          (settings)
├── imports customer_coa_manager.py      (customer logic)
├── imports pledge_accounting_manager.py (accounting logic)
└── imports security_middleware.py       (security)

models.py
├── imports database.py        (Base class)
└── defines all table relationships

customer_coa_manager.py  
├── imports models.py          (Customer, MasterAccount)
└── imports database.py        (Session)

pledge_accounting_manager.py
├── imports models.py          (all accounting models)  
└── imports database.py        (Session)

auth.py
├── imports models.py          (User model)
└── imports config.py          (JWT settings)
```

🎯 KEY WORKFLOW PATTERNS:
========================

1. **AUTHENTICATION FLOW**:
   Request → Check Authorization header → Validate JWT → Get user → Continue

2. **DATABASE FLOW**:  
   Endpoint → Get DB session → Business logic → Commit/Rollback → Close session

3. **ACCOUNTING FLOW**:
   Business event → Create voucher → Create ledger entries → Validate balance → Save

4. **ERROR HANDLING FLOW**:
   Exception occurs → Rollback transaction → Return HTTP error → Log details

5. **VALIDATION FLOW**:
   Request data → Pydantic validation → Business rules → Database constraints → Success

💡 UNDERSTANDING TIPS:
=====================

1. **Start Reading Order**:
   config.py → database.py → models.py → auth.py → main.py

2. **Follow the Data**:
   Track how data flows from request to database and back

3. **Understand Dependencies**:  
   See how files import and use each other

4. **Trace Endpoints**:
   Pick one endpoint and follow its complete execution path

இந்த detailed explanation உங்களுக்கு clear-ஆ இருக்கா? எந்த specific file-ல deep dive பண்ணனும்? 😊
"""
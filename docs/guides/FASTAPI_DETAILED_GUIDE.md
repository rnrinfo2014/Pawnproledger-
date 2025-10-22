"""
🐍 PYTHON FASTAPI - COMPLETE BEGINNER'S GUIDE
=============================================

FastAPI என்னா? (What is FastAPI?)
=================================
- Python-ல web APIs build பண்ணுகிற modern framework
- Very fast and easy to use
- Automatic API documentation generate பண்ணும்
- Type hints support பண்ணும்

🏗️ BASIC FASTAPI STRUCTURE:
===========================

SIMPLE EXAMPLE:
```python
from fastapi import FastAPI

app = FastAPI()  # Create app instance

@app.get("/")    # HTTP GET method
def hello():
    return {"message": "Hello World"}

@app.post("/users/")  # HTTP POST method  
def create_user(name: str):
    return {"user": name}
```

🌐 HTTP METHODS EXPLAINED:
==========================
- GET: Data retrieve பண்ணுவதுக்கு (படிக்கறதுக்கு)
- POST: New data create பண்ணுவதுக்கு
- PUT: Data update பண்ணுவதுக்கு  
- DELETE: Data delete பண்ணுவதுக்கு

🎯 FASTAPI DECORATORS:
=====================

@app.get("/path")     # GET request
@app.post("/path")    # POST request  
@app.put("/path")     # PUT request
@app.delete("/path")  # DELETE request

Example:
```python
@app.get("/customers/")        # Get all customers
@app.get("/customers/{id}")    # Get specific customer
@app.post("/customers/")       # Create new customer
@app.put("/customers/{id}")    # Update customer
@app.delete("/customers/{id}") # Delete customer
```

📁 FASTAPI PROJECT FILE STRUCTURE:
==================================

TYPICAL STRUCTURE:
```
ProjectName/
├── main.py              # 🎯 Entry point (server start)
├── models.py            # 🗃️ Database models  
├── database.py          # 🔌 DB connection
├── auth.py              # 🔐 Authentication
├── config.py            # ⚙️ Settings
├── requirements.txt     # 📦 Dependencies
├── routers/             # 📂 Route modules
│   ├── users.py
│   ├── products.py
│   └── orders.py
├── schemas/             # 📋 Pydantic models
│   ├── user.py
│   └── product.py
├── services/            # 🔧 Business logic
│   ├── user_service.py
│   └── auth_service.py
└── utils/               # 🛠️ Helper functions
    ├── helpers.py
    └── validators.py
```

🏗️ OUR PAWNSOFT PROJECT STRUCTURE:
==================================

```
PawnProApi/
├── main.py                      # 🎯 All API endpoints
├── models.py                    # 🗃️ SQLAlchemy models
├── database.py                  # 🔌 PostgreSQL connection
├── auth.py                      # 🔐 JWT authentication
├── config.py                    # ⚙️ App configuration
├── customer_coa_manager.py      # 👤 Customer accounting
├── pledge_accounting_manager.py # 💰 Pledge accounting
├── security_middleware.py       # 🛡️ Security layers
├── requirements.txt             # 📦 Python packages
├── create_tables.py            # 🏗️ Database setup
├── migrate_*.py                # 🔄 Database migrations
└── test_*.py                   # 🧪 Test scripts
```

📄 EACH FILE EXPLANATION:
========================

1. 📄 MAIN.PY (மிக முக்கியம்):
```python
from fastapi import FastAPI

app = FastAPI(title="PawnSoft API")

# All endpoints defined here
@app.post("/customers/")
@app.post("/pledges/")  
@app.post("/pledge-payments/")
@app.get("/customers/")
# ... மற்ற endpoints
```

2. 📄 MODELS.PY (Database Tables):
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    phone = Column(String(15))
```

3. 📄 DATABASE.PY (DB Connection):
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

4. 📄 AUTH.PY (Authentication):
```python
from fastapi.security import OAuth2PasswordBearer
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    # JWT token creation
    pass

def verify_token(token: str):
    # Token verification
    pass
```

🔄 FASTAPI REQUEST WORKFLOW:
===========================

STEP 1: CLIENT REQUEST
```
Browser/Mobile App
       ↓
HTTP Request (GET/POST/PUT/DELETE)
```

STEP 2: FASTAPI RECEIVES
```python
@app.post("/customers/")  # Route matching
def create_customer(customer_data):
    # Function called
```

STEP 3: DEPENDENCY INJECTION
```python
def create_customer(
    customer: CustomerCreate,           # Request body
    db: Session = Depends(get_db),      # Database session
    current_user = Depends(get_user)    # Authentication
):
```

STEP 4: BUSINESS LOGIC
```python
# Validate data
# Process business rules  
# Database operations
# Return response
```

STEP 5: RESPONSE
```python
return {
    "id": 123,
    "name": "Customer Name", 
    "status": "created"
}
```

🎯 PRACTICAL EXAMPLE - OUR PROJECT:
==================================

CUSTOMER CREATION WORKFLOW:

1. 🌐 Frontend Request:
```javascript
fetch('/customers/', {
    method: 'POST',
    body: JSON.stringify({
        name: 'ராமு',
        phone: '9876543210'
    })
})
```

2. 🐍 FastAPI Endpoint (main.py):
```python
@app.post("/customers/", response_model=Customer)
def create_customer(
    customer: CustomerCreate,                    # Input validation
    db: Session = Depends(get_db),              # DB session
    current_user: UserModel = Depends(get_current_user)  # Auth
):
    # Step 1: Create customer record
    db_customer = CustomerModel(
        name=customer.name,
        phone=customer.phone,
        company_id=current_user.company_id
    )
    
    # Step 2: Save to database
    db.add(db_customer)
    db.flush()  # Get ID
    
    # Step 3: Create COA account (accounting)
    coa_result = create_customer_coa_account(
        db=db,
        customer_id=db_customer.id,
        customer_name=customer.name,
        company_id=current_user.company_id
    )
    
    # Step 4: Update customer with COA account
    db_customer.coa_account_id = coa_result['account_id']
    
    # Step 5: Commit and return
    db.commit()
    db.refresh(db_customer)
    
    return db_customer
```

3. 🗃️ Database Operations:
```sql
-- customers table insert
INSERT INTO customers (name, phone, company_id) 
VALUES ('ராமு', '9876543210', 1);

-- master_accounts table insert (COA)
INSERT INTO master_accounts (account_code, account_name, company_id)
VALUES ('2001-101', 'ராமு - Customer Account', 1);

-- Update customer with COA ID
UPDATE customers SET coa_account_id = 201 WHERE id = 101;
```

4. 📤 Response:
```json
{
    "id": 101,
    "name": "ராமு",
    "phone": "9876543210", 
    "coa_account_id": 201,
    "company_id": 1,
    "created_at": "2025-10-13T10:30:00"
}
```

🛠️ FASTAPI KEY FEATURES:
========================

1. **AUTOMATIC DOCS**: 
   - http://localhost:8000/docs (Swagger UI)
   - http://localhost:8000/redoc (ReDoc)

2. **TYPE HINTS**:
```python
def create_user(name: str, age: int) -> dict:
    return {"name": name, "age": age}
```

3. **PYDANTIC MODELS** (Data Validation):
```python
from pydantic import BaseModel

class CustomerCreate(BaseModel):
    name: str
    phone: str
    address: Optional[str] = None
```

4. **DEPENDENCY INJECTION**:
```python
def get_database():
    # Database connection logic
    pass

@app.get("/users/")
def get_users(db = Depends(get_database)):
    # db automatically injected
    pass
```

5. **MIDDLEWARE**:
```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Custom-Header"] = "Value"
    return response
```

🚀 HOW TO RUN FASTAPI:
=====================

1. **Install FastAPI**:
```bash
pip install fastapi uvicorn
```

2. **Basic App** (app.py):
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello World"}
```

3. **Run Server**:
```bash
uvicorn app:app --reload
```

4. **Access**:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

📊 FASTAPI VS OTHER FRAMEWORKS:
===============================

| Feature | FastAPI | Flask | Django |
|---------|---------|-------|---------|
| Speed | ⚡ Very Fast | 🐌 Slow | 🚶 Medium |
| Auto Docs | ✅ Built-in | ❌ Manual | ❌ Manual |
| Type Hints | ✅ Native | ⚠️ Extra | ⚠️ Extra |
| Async Support | ✅ Native | ⚠️ Limited | ✅ Good |
| Learning Curve | 📈 Easy | 📈 Easy | 📈 Steep |

🎯 ADVANCED FASTAPI CONCEPTS:
============================

1. **Background Tasks**:
```python
from fastapi import BackgroundTasks

def send_email(email: str):
    # Send email logic
    pass

@app.post("/send-notification/")
def create_item(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email)
    return {"message": "Email queued"}
```

2. **File Uploads**:
```python
from fastapi import File, UploadFile

@app.post("/upload/")
def upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}
```

3. **WebSockets**:
```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Hello WebSocket!")
```

4. **Custom Exceptions**:
```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in database:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id}
```

💡 BEST PRACTICES:
==================

1. **Project Structure**:
   - Separate routers for different modules
   - Keep business logic in service files
   - Use Pydantic models for validation

2. **Error Handling**:
```python
try:
    # Business logic
    pass
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

3. **Database Sessions**:
```python
# Always use dependency injection for DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

4. **Environment Variables**:
```python
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")
    secret_key: str = os.getenv("SECRET_KEY")
```

🔍 HOW TO DEBUG FASTAPI:
=======================

1. **Enable Debug Mode**:
```python
app = FastAPI(debug=True)
```

2. **Logging**:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/test/")
def test_endpoint():
    logger.info("Test endpoint called")
    return {"status": "ok"}
```

3. **Print Debugging**:
```python
@app.post("/debug/")
def debug_endpoint(data: dict):
    print(f"Received data: {data}")  # Console output
    return {"received": data}
```

இந்த explanation clear-ஆ இருக்கா? எந்த specific part detail-ல தெரிஞ்சுக்கணும்? 😊

- FastAPI decorators எப்படி work ஆகும்?
- Database integration எப்படி பண்ணுவது?
- Authentication எப்படி implement பண்ணுவது?
- Error handling எப்படி பண்ணுவது?
"""
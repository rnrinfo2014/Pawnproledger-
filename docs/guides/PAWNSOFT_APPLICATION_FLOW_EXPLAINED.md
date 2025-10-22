"""
🏪 PAWNSOFT PROJECT - COMPLETE APPLICATION FLOW EXPLAINED
========================================================

என்ன இது? (What is this?)
==========================
இது ஒரு Pawn Shop (அடகு கடை) management system. பொருள்களை அடகு வைத்து பணம் கொடுக்கும் business-ஐ manage பண்ணும் software.

📱 APPLICATION ARCHITECTURE (எப்படி இந்த app work ஆகும்?)
=========================================================

1. FRONTEND (முன்பகுதி) - User Interface
   ┌─────────────────────────────────────┐
   │  🖥️  WEB BROWSER / MOBILE APP       │
   │  (Customer-ஐ பார்க்கும் பகுதி)        │
   │  - Login form                       │
   │  - Customer registration            │
   │  - Pledge creation                  │
   │  - Payment forms                    │
   └─────────────────────────────────────┘
                    ↕️ HTTP Requests
   
2. BACKEND (பின்பகுதி) - Business Logic  
   ┌─────────────────────────────────────┐
   │  🐍 PYTHON FastAPI SERVER          │
   │  (main.py file - எல்லா logic இங்க) │
   │  - API endpoints                    │
   │  - Authentication                   │
   │  - Business rules                   │
   │  - Accounting calculations          │
   └─────────────────────────────────────┘
                    ↕️ SQL Queries

3. DATABASE (தரவுத்தளம்) - Data Storage
   ┌─────────────────────────────────────┐
   │  🐘 PostgreSQL DATABASE             │
   │  (எல்லா data store ஆகும் இடம்)      │
   │  - Customer details                 │
   │  - Pledge information               │
   │  - Payment records                  │
   │  - Accounting entries               │
   └─────────────────────────────────────┘

🔄 COMPLETE USER JOURNEY (User எப்படி use பண்ணுவாங்க)
=====================================================

STEP 1: AUTHENTICATION (அடையாளம்)
----------------------------------
User → Login page → Username/Password → Backend checks → Database verification → Token generated

📝 Files involved:
   - auth.py (authentication logic)
   - main.py (login endpoint)

STEP 2: CUSTOMER MANAGEMENT (வாடிக்கையாளர்)
------------------------------------------
Staff → Add customer → Fill form → Backend validates → Database saves → COA account auto-created

🏃‍♂️ Flow:
   Frontend form → POST /customers/ → customer_coa_manager.py → Database

📝 Files involved:
   - main.py (customer endpoints)
   - models.py (Customer model)
   - customer_coa_manager.py (accounting integration)

STEP 3: PLEDGE CREATION (அடகு வைப்பு)
------------------------------------
Customer brings gold → Staff evaluates → Creates pledge → System calculates interest → Database saves

🏃‍♂️ Flow:
   1. Staff fills pledge form (amount, items, duration)
   2. System calculates final amount (principal + interest)
   3. Creates pledge record
   4. Creates accounting entries (double-entry bookkeeping)
   5. Generates pledge number

📝 Files involved:
   - main.py (pledge endpoints)
   - models.py (Pledge, PledgeItem models)
   - pledge_accounting_manager.py (accounting logic)

STEP 4: PAYMENT PROCESSING (பணம் செலுத்துதல்)
-------------------------------------------
Customer pays → Staff records payment → System updates balance → Creates accounting entries

🏃‍♂️ Flow:
   1. Staff enters payment amount
   2. System calculates remaining balance
   3. Updates pledge status (active/partial_paid/redeemed)
   4. Creates accounting entries:
      - Cash account increases (Debit)
      - Customer debt decreases (Credit)
      - Interest income recorded (Credit)

📝 Files involved:
   - main.py (payment endpoints)
   - pledge_accounting_manager.py (payment accounting)

🗃️ DATABASE STRUCTURE (எப்படி data store ஆகும்?)
================================================

முக்கிய Tables:
1. companies - கம்பெனி details
2. users - login பண்ணும் staff
3. customers - வாடிக்கையாளர்கள்
4. master_accounts - Chart of Accounts (accounting structure)
5. pledges - அடகு records
6. pledge_items - அடகு பொருள்கள்
7. pledge_payments - பணம் செலுத்துதல்
8. ledger_entries - accounting entries (debit/credit)
9. voucher_master - accounting vouchers

🏗️ CODE ARCHITECTURE (Code எப்படி organize பண்ணியிருக்கு?)
==========================================================

📁 Project Structure:
PawnProApi/
├── main.py                    # 🎯 Main API endpoints (எல்லா routes)
├── models.py                  # 🗃️ Database table definitions
├── database.py                # 🔌 Database connection
├── auth.py                    # 🔐 Authentication & security
├── config.py                  # ⚙️ App settings
├── customer_coa_manager.py    # 👤 Customer accounting logic
├── pledge_accounting_manager.py # 💰 Pledge accounting logic
└── requirements.txt           # 📦 Python packages needed

🎯 MAIN.PY FLOW (முக்கிய file எப்படி work ஆகும்?)
================================================

1. IMPORTS:
   ```python
   from fastapi import FastAPI        # Web framework
   from models import Customer        # Database models
   from auth import authenticate      # Security functions
   ```

2. APP CREATION:
   ```python
   app = FastAPI()                    # Create web application
   ```

3. ENDPOINTS (API Routes):
   ```python
   @app.post("/customers/")           # Customer creation
   @app.post("/pledges/")             # Pledge creation  
   @app.post("/pledge-payments/")     # Payment processing
   @app.get("/customers/")            # Get customer list
   ```

🔄 REQUEST-RESPONSE CYCLE (ஒரு request எப்படி process ஆகும்?)
============================================================

Example: Customer Creation

1. 🌐 Frontend sends request:
   ```
   POST /customers/
   {
     "name": "ராமு",
     "phone": "9876543210", 
     "address": "சென்னை"
   }
   ```

2. 🐍 Backend receives (main.py):
   ```python
   @app.post("/customers/")
   def create_customer(customer: CustomerCreate, db: Session):
       # Validate data
       # Create customer record
       # Create COA account
       # Return response
   ```

3. 🗃️ Database operations:
   ```sql
   INSERT INTO customers (name, phone, address) 
   VALUES ('ராமு', '9876543210', 'சென்னை');
   
   INSERT INTO master_accounts (account_code, account_name)
   VALUES ('2001-001', 'ராமு - Customer Account');
   ```

4. 📤 Response sent back:
   ```json
   {
     "id": 123,
     "name": "ராமு",
     "phone": "9876543210",
     "coa_account_id": 456,
     "status": "active"
   }
   ```

💰 ACCOUNTING SYSTEM (கணக்கு system எப்படி?)
============================================

இது Double-Entry Bookkeeping system:

PLEDGE CREATION:
- Customer Account Dr. (வாடிக்கையாளர் நமக்கு கடன்பட்டார்)
- Cash Account Cr. (நாம் cash கொடுத்தோம்)

PAYMENT RECEIVED:
- Cash Account Dr. (நமக்கு cash வந்தது)
- Customer Account Cr. (வாடிக்கையாளர் கடன் குறைந்தது)

🚀 HOW TO START THE APPLICATION (எப்படி start பண்ணுவது?)
========================================================

1. 📦 Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. 🗃️ Setup database:
   ```bash
   python create_tables.py
   ```

3. 🏃‍♂️ Start server:
   ```bash
   uvicorn main:app --reload
   ```

4. 🌐 Open browser:
   ```
   http://localhost:8000/docs
   ```

🔧 IMPORTANT FILES EXPLANATION:
===============================

📄 models.py:
   - எல்லா database table-களும் இங்க define பண்ணியிருக்கு
   - Customer, Pledge, Payment எல்லாம் classes ஆக இருக்கு

📄 main.py:
   - எல்லா API endpoints இங்க இருக்கு
   - Frontend-ல இருந்து வரும் எல்லா requests இங்க handle ஆகும்

📄 auth.py:
   - Login/logout logic
   - Password hashing
   - JWT token generation

📄 pledge_accounting_manager.py:
   - Pledge-க்கு accounting entries create பண்ணும்
   - Double-entry bookkeeping logic

🎯 SUMMARY FOR BEGINNERS:
=========================

1. இது ஒரு web application (website போன்றது)
2. Python FastAPI-ல built பண்ணியிருக்கு
3. PostgreSQL database use பண்ணுது data store பண்ண
4. Accounting system integrated பண்ணியிருக்கு
5. REST API endpoints எல்லாம் main.py-ல இருக்கு
6. Frontend-ல இருந்து API calls பண்ணி data get/post பண்ணலாம்

🤔 எப்படி learn பண்ணுவது?
==========================
1. Python basics கத்துக்கோங்க
2. FastAPI documentation படிங்க
3. Database concepts (SQL) கத்துக்கோங்க
4. இந்த project-ல ஒவ்வொரு file-ஐயும் line by line படிங்க
5. API endpoints-ஐ test பண்ணி பாருங்க

Hope this helps! Any specific part-ஐ detail-ல explain பண்ணனுமா? 😊
"""
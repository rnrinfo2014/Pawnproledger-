"""
🔄 PAWNSOFT - SIMPLE FLOW DIAGRAM
=================================

நீங்க beginner-ஆ இருக்கீங்க-னு சொன்னீங்க, அதனால simple-ஆ explain பண்றேன்:

📱 USER INTERACTION FLOW:
========================

1. STAFF LOGIN:
   Staff → Enter username/password → System checks → Login success/fail

2. CUSTOMER MANAGEMENT:
   Staff → Add new customer → Fill form → System saves → Auto creates account

3. PLEDGE CREATION (மிக முக்கியமான part):
   Customer brings gold → Staff evaluates → Creates pledge → Money given

4. PAYMENT:
   Customer pays money → Staff records → System updates balance

🗂️ WHAT HAPPENS IN EACH STEP:
=============================

STEP 1: CUSTOMER COMES TO SHOP
┌─────────────────────────┐
│   👤 CUSTOMER           │
│   Brings gold jewelry   │
│   Needs cash loan       │
└─────────────────────────┘
            ↓
┌─────────────────────────┐
│   👨‍💼 STAFF             │  
│   Evaluates gold        │
│   Decides loan amount   │
└─────────────────────────┘

STEP 2: SYSTEM ENTRY
┌─────────────────────────┐
│   💻 STAFF ENTERS DATA  │
│   - Customer details    │
│   - Item details        │
│   - Loan amount         │
│   - Interest rate       │
└─────────────────────────┘
            ↓
┌─────────────────────────┐
│   🤖 SYSTEM CALCULATES  │
│   - Final amount        │ 
│   - Due date           │
│   - Monthly interest    │
└─────────────────────────┘

STEP 3: DATABASE SAVES
┌─────────────────────────┐
│   💾 DATA SAVED         │
│   - Pledge record       │
│   - Customer record     │
│   - Accounting entries  │
└─────────────────────────┘

STEP 4: MONEY TRANSACTION
┌─────────────────────────┐
│   💰 CASH GIVEN         │
│   Customer gets money   │
│   Receipt printed       │
│   Gold kept safely      │
└─────────────────────────┘

🏗️ TECHNICAL ARCHITECTURE:
==========================

BROWSER (Frontend)
    ↕️ HTTP requests
PYTHON API (Backend)  
    ↕️ SQL queries
POSTGRESQL (Database)

🎯 MAIN FILES YOU NEED TO UNDERSTAND:
====================================

1. 📄 main.py (மிக முக்கியம்):
   - எல்லா API endpoints
   - Business logic
   - Request handling

2. 📄 models.py:
   - Database table structures
   - Data relationships

3. 📄 pledge_accounting_manager.py:
   - Accounting calculations
   - Financial entries

💡 BEGINNER-க்கு IMPORTANT TIPS:
===============================

1. START HERE: main.py file-ல இருக்கும் endpoints-ஐ பாருங்க
2. UNDERSTAND: Each @app.post() or @app.get() is an API endpoint
3. TRACE: ஒரு request எப்படி flow ஆகுது-னு follow பண்ணுங்க
4. DATABASE: models.py-ல எப்படி data structure இருக்கு-னு பாருங்க

🔍 CODE READING ORDER FOR BEGINNERS:
===================================

1. First read: models.py (data structures புரிஞ்சுக்கோங்க)
2. Then read: main.py endpoints (API புரிஞ்சுக்கோங்க)  
3. Finally: accounting files (business logic புரிஞ்சுக்கோங்க)

🚀 HOW TO EXPLORE:
=================

1. Start the server: `uvicorn main:app --reload`
2. Open: http://localhost:8000/docs
3. Try the API endpoints one by one
4. See what data goes in and comes out

எந்த specific part detail-ல தெரிஞ்சுக்கனும்? 😊
"""
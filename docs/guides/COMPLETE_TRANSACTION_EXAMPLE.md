"""
🎯 COMPLETE TRANSACTION EXAMPLE - STEP BY STEP
==============================================

இந்த example-ல ராமு-னு ஒருத்தர் gold அடகு வைக்கற complete process-ஐ பார்ப்போம்:

👤 SCENARIO: 
ராமு-க்கு urgent-ஆ ₹50,000 வேணும். அவர் கிட்ட gold chain இருக்கு.

🔄 COMPLETE FLOW:
================

STEP 1: CUSTOMER REGISTRATION
-----------------------------
Staff computer-ல type பண்ணுவாங்க:

Frontend Request:
```json
POST /customers/
{
  "name": "ராமு",
  "phone": "9876543210", 
  "address": "T.Nagar, Chennai",
  "id_proof_type": "Aadhar",
  "id_proof_number": "1234 5678 9012"
}
```

System Response:
```json
{
  "id": 101,
  "name": "ராமு", 
  "coa_account_id": 201,
  "account_code": "2001-101",
  "status": "active"
}
```

Database-ல என்ன save ஆகும்:
```sql
-- customers table-ல
INSERT INTO customers VALUES (101, 'ராமு', '9876543210', 'T.Nagar, Chennai', 201);

-- master_accounts table-ல (automatic COA account)
INSERT INTO master_accounts VALUES (201, '2001-101', 'ராமு - Customer Account');
```

STEP 2: PLEDGE CREATION
-----------------------
Staff gold-ஐ evaluate பண்ணி details enter பண்ணுவாங்க:

Frontend Request:
```json
POST /pledges/
{
  "customer_id": 101,
  "loan_amount": 50000.0,
  "interest_rate": 2.0,
  "loan_period": 12,
  "gold_weight": 25.5,
  "gold_purity": "22K",
  "items": [
    {
      "item_name": "Gold Chain",
      "weight": 25.5,
      "description": "22K Gold Chain"
    }
  ]
}
```

System Calculations:
```python
# Final amount calculation
monthly_interest = 50000 * (2/100) = 1000
final_amount = 50000 + (1000 * 12) = 62000
```

Database-ல என்ன save ஆகும்:
```sql
-- pledges table
INSERT INTO pledges VALUES (
  1001, 'GL-1001', 101, 50000, 2.0, 12, 62000, 'active', '2025-10-13'
);

-- pledge_items table  
INSERT INTO pledge_items VALUES (
  5001, 1001, 'Gold Chain', 25.5, '22K Gold Chain'
);

-- Accounting entries (automatic):
-- 1. Customer owes us money
INSERT INTO ledger_entries VALUES (
  voucher_id, account_id=201, debit=50000, credit=0, 
  'Pledge GL-1001 - Loan given', 'pledge', 1001
);

-- 2. We gave cash
INSERT INTO ledger_entries VALUES (
  voucher_id, account_id=cash_account, debit=0, credit=50000,
  'Pledge GL-1001 - Cash given', 'pledge', 1001  
);
```

STEP 3: PAYMENT (2 months later)
--------------------------------
ராமு ₹5000 pay பண்ணுவார்:

Frontend Request:
```json
POST /pledge-payments/
{
  "pledge_id": 1001,
  "amount": 5000.0,
  "interest_amount": 2000.0,
  "principal_amount": 3000.0,
  "payment_method": "cash"
}
```

System Calculations:
```python
# Balance calculation
previous_payments = 0
remaining_balance = 62000 - 0 - 5000 = 57000
new_status = 'partial_paid'  # since balance > 0
```

Database Updates:
```sql
-- pledge_payments table
INSERT INTO pledge_payments VALUES (
  2001, 1001, 5000, 2000, 3000, 57000, 'cash', '2025-12-13'
);

-- Update pledge status
UPDATE pledges SET status = 'partial_paid' WHERE pledge_id = 1001;

-- Accounting entries (NEW - what I implemented):
-- 1. Cash received
INSERT INTO ledger_entries VALUES (
  voucher_id, account_id=cash_account, debit=5000, credit=0,
  'Payment received from ராமு for Pledge GL-1001', 'payment', 2001
);

-- 2. Customer debt reduced  
INSERT INTO ledger_entries VALUES (
  voucher_id, account_id=201, debit=0, credit=3000,
  'Principal payment for Pledge GL-1001', 'payment', 2001
);

-- 3. Interest income
INSERT INTO ledger_entries VALUES (
  voucher_id, account_id=interest_income, debit=0, credit=2000,
  'Interest income for Pledge GL-1001', 'payment', 2001
);
```

📊 ACCOUNTING SUMMARY:
=====================

After this transaction:

Customer Account (ராமு):
- Original debt: ₹50,000 Dr
- Payment received: ₹3,000 Cr  
- Current balance: ₹47,000 Dr (ராமு still owes us)

Cash Account:
- Original: ₹50,000 Cr (we gave cash)
- Payment received: ₹5,000 Dr
- Net: ₹45,000 Cr (net cash out)

Interest Income:
- Earned: ₹2,000 Cr (profit)

🎯 CODE FILES INVOLVED:
======================

1. main.py - எல்லா endpoints:
   ```python
   @app.post("/customers/")     # Customer creation
   @app.post("/pledges/")       # Pledge creation  
   @app.post("/pledge-payments/") # Payment processing
   ```

2. customer_coa_manager.py:
   ```python
   create_customer_coa_account()  # Auto COA account
   ```

3. pledge_accounting_manager.py:
   ```python
   create_complete_pledge_accounting()  # Pledge entries
   create_payment_accounting()          # Payment entries (NEW)
   ```

4. models.py:
   ```python
   class Customer(Base):      # Customer table
   class Pledge(Base):        # Pledge table
   class PledgePayment(Base): # Payment table
   class LedgerEntry(Base):   # Accounting table
   ```

🔍 HOW TO TRACE IN CODE:
=======================

1. Find the endpoint in main.py:
   ```python
   @app.post("/pledge-payments/")
   def create_pledge_payment(...)
   ```

2. See what it does:
   - Validates data
   - Calculates balance  
   - Saves payment record
   - Calls create_payment_accounting()
   - Updates pledge status

3. Follow the accounting function:
   ```python
   def create_payment_accounting():
       # Creates voucher
       # Creates ledger entries
       # Maintains double-entry balance
   ```

💡 KEY CONCEPTS FOR BEGINNERS:
=============================

1. **API Endpoint**: ஒரு URL-ல data send/receive பண்ணும் point
2. **Database Transaction**: Multiple table-களில் data save பண்ணும் process  
3. **Double Entry**: Every debit-க்கு equal credit இருக்கும்
4. **Business Logic**: Rules and calculations
5. **Data Flow**: Request → Validation → Processing → Database → Response

இந்த example clear-ஆ இருக்கா? எந்த part detail-ல தெரிஞ்சுக்கணும்? 😊
"""
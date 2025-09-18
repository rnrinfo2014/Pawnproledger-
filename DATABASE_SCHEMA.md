# 🗄️ Database Schema Documentation

Complete database schema for PawnSoft Pawn Shop Management System

## Database Overview

PawnSoft uses PostgreSQL as the primary database with SQLAlchemy ORM. The schema supports:
- Multi-tenant architecture (company-based)
- Double-entry bookkeeping
- Comprehensive audit trails
- Role-based access control
- File storage references

---

## 🔗 Entity Relationship Diagram

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  companies  │    │    users    │    │    areas    │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
       ├──────────────────┼──────────────────┤
       │                  │                  │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  customers  │    │   pledges   │    │    banks    │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │
       └──────────────────┘
       │
┌─────────────┐    ┌─────────────┐
│pledge_items │    │pledge_payments│
└─────────────┘    └─────────────┘

Accounting Tables:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│accounts_master│   │voucher_master│   │ledger_entries│
└─────────────┘    └─────────────┘    └─────────────┘
```

---

## 📊 Core Tables

### 1. Users Table
**Purpose**: System users with role-based access control

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user', -- 'admin', 'user'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

**Key Fields:**
- `password_hash`: bcrypt hashed password
- `role`: Admin users can create companies and users
- `is_active`: Soft delete functionality

### 2. Companies Table
**Purpose**: Multi-tenant company/branch management

```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100),
    pan_number VARCHAR(10),
    gst_number VARCHAR(15),
    license_number VARCHAR(50),
    logo_path VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Business Rules:**
- Each company operates independently
- All business data is company-scoped
- Logo upload supported via file API

### 3. Areas Table
**Purpose**: Geographic area management for branches

```sql
CREATE TABLE areas (
    id SERIAL PRIMARY KEY,
    area_name VARCHAR(100) NOT NULL,
    district VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. Customers Table
**Purpose**: Customer profiles with KYC information

```sql
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(200) NOT NULL,
    father_husband_name VARCHAR(200),
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    alt_phone_number VARCHAR(15),
    address TEXT,
    id_proof_type VARCHAR(50), -- 'Aadhaar', 'PAN', 'Voter ID', etc.
    id_proof_number VARCHAR(50),
    id_proof_file_path VARCHAR(500),
    photo_path VARCHAR(500),
    company_id INTEGER NOT NULL REFERENCES companies(id),
    area_id INTEGER REFERENCES areas(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id)
);
```

**Business Rules:**
- Phone number must be unique within company
- KYC documents stored as file references
- Customer tied to specific company and area

---

## 💎 Pledge Management Tables

### 5. Jewell Types Table
**Purpose**: Categories of jewelry (Gold, Silver, Diamond, etc.)

```sql
CREATE TABLE jewell_types (
    id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 6. Jewell Rates Table
**Purpose**: Daily gold/silver rate tracking

```sql
CREATE TABLE jewell_rates (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    jewell_type_id INTEGER NOT NULL REFERENCES jewell_types(id),
    rate DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER NOT NULL REFERENCES users(id)
);
```

### 7. Schemes Table
**Purpose**: Loan scheme configurations

```sql
CREATE TABLE schemes (
    id SERIAL PRIMARY KEY,
    scheme_name VARCHAR(100) NOT NULL,
    jewell_type_id INTEGER NOT NULL REFERENCES jewell_types(id),
    interest_rate DECIMAL(5,2) NOT NULL, -- Monthly interest rate
    max_loan_percentage DECIMAL(5,2) DEFAULT 75.00,
    penalty_rate DECIMAL(5,2) DEFAULT 0.00,
    min_amount DECIMAL(10,2) DEFAULT 0.00,
    max_amount DECIMAL(12,2),
    default_months INTEGER DEFAULT 12,
    is_active BOOLEAN DEFAULT true,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 8. Pledges Table
**Purpose**: Main pledge/loan records

```sql
CREATE TABLE pledges (
    pledge_id SERIAL PRIMARY KEY,
    pledge_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    company_id INTEGER NOT NULL REFERENCES companies(id),
    scheme_id INTEGER NOT NULL REFERENCES schemes(id),
    pledge_amount DECIMAL(12,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    penalty_rate DECIMAL(5,2) DEFAULT 0.00,
    months INTEGER NOT NULL,
    pledge_date DATE NOT NULL,
    due_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- active, settled, auctioned
    total_paid DECIMAL(12,2) DEFAULT 0.00,
    balance_amount DECIMAL(12,2),
    last_payment_date DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER NOT NULL REFERENCES users(id)
);
```

**Status Values:**
- `active`: Loan is ongoing
- `settled`: Fully paid and closed
- `auctioned`: Items sold due to non-payment

### 9. Pledge Items Table
**Purpose**: Individual items in each pledge

```sql
CREATE TABLE pledge_items (
    pledge_item_id SERIAL PRIMARY KEY,
    pledge_id INTEGER NOT NULL REFERENCES pledges(pledge_id) ON DELETE CASCADE,
    jewell_design_id INTEGER REFERENCES jewell_designs(id),
    jewell_condition VARCHAR(100) NOT NULL,
    gross_weight DECIMAL(8,3) NOT NULL,
    net_weight DECIMAL(8,3) NOT NULL,
    image VARCHAR(500),
    net_value DECIMAL(12,2) NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 10. Pledge Payments Table
**Purpose**: Payment history and tracking

```sql
CREATE TABLE pledge_payments (
    payment_id SERIAL PRIMARY KEY,
    pledge_id INTEGER NOT NULL REFERENCES pledges(pledge_id) ON DELETE CASCADE,
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    payment_type VARCHAR(20) NOT NULL, -- interest, principal, partial_redeem, full_redeem
    amount DECIMAL(12,2) NOT NULL,
    interest_amount DECIMAL(12,2) DEFAULT 0.00,
    principal_amount DECIMAL(12,2) DEFAULT 0.00,
    penalty_amount DECIMAL(12,2) DEFAULT 0.00,
    discount_amount DECIMAL(12,2) DEFAULT 0.00,
    balance_amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(20) DEFAULT 'cash', -- cash, bank_transfer, cheque
    bank_reference VARCHAR(100),
    receipt_no VARCHAR(50),
    remarks TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER NOT NULL REFERENCES users(id),
    company_id INTEGER NOT NULL REFERENCES companies(id)
);
```

---

## 📊 Accounting Tables

### 11. Accounts Master Table
**Purpose**: Chart of Accounts for double-entry bookkeeping

```sql
CREATE TABLE accounts_master (
    id SERIAL PRIMARY KEY,
    account_code VARCHAR(20) NOT NULL,
    account_name VARCHAR(200) NOT NULL,
    account_type VARCHAR(20) NOT NULL, -- Asset, Liability, Income, Expense, Equity
    group_name VARCHAR(100),
    parent_id INTEGER REFERENCES accounts_master(id),
    is_active BOOLEAN DEFAULT true,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(account_code, company_id)
);
```

**Account Types:**
- **Asset**: Cash, Bank, Inventory, Fixed Assets
- **Liability**: Customer Accounts, Loans Payable
- **Income**: Interest Income, Auction Income, Service Charges
- **Expense**: Staff Salary, Rent, Utilities, Office Expenses
- **Equity**: Owner's Capital, Retained Earnings

### 12. Voucher Master Table
**Purpose**: Transaction voucher headers

```sql
CREATE TABLE voucher_master (
    id SERIAL PRIMARY KEY,
    voucher_number VARCHAR(50) NOT NULL,
    voucher_type VARCHAR(50) NOT NULL, -- Pledge, Payment, Expense, Journal
    voucher_date DATE NOT NULL,
    reference_table VARCHAR(50), -- pledges, pledge_payments, etc.
    reference_id INTEGER,
    total_amount DECIMAL(15,2) NOT NULL,
    narration TEXT,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(voucher_number, company_id)
);
```

### 13. Ledger Entries Table
**Purpose**: Double-entry bookkeeping transactions

```sql
CREATE TABLE ledger_entries (
    id SERIAL PRIMARY KEY,
    voucher_id INTEGER NOT NULL REFERENCES voucher_master(id) ON DELETE CASCADE,
    account_id INTEGER NOT NULL REFERENCES accounts_master(id),
    transaction_date DATE NOT NULL,
    debit_amount DECIMAL(15,2) DEFAULT 0.00,
    credit_amount DECIMAL(15,2) DEFAULT 0.00,
    narration TEXT,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Double Entry Rules:**
- Every transaction has equal debits and credits
- Sum of all debits = Sum of all credits for each voucher
- Running balances calculated dynamically

---

## 🏦 Supporting Tables

### 14. Banks Table
**Purpose**: Bank account management

```sql
CREATE TABLE banks (
    id SERIAL PRIMARY KEY,
    bank_name VARCHAR(200) NOT NULL,
    branch_name VARCHAR(200),
    account_name VARCHAR(200),
    status VARCHAR(20) DEFAULT 'active',
    company_id INTEGER NOT NULL REFERENCES companies(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### 15. Jewell Designs Table
**Purpose**: Jewelry design catalog

```sql
CREATE TABLE jewell_designs (
    id SERIAL PRIMARY KEY,
    design_name VARCHAR(200) NOT NULL,
    jewell_type_id INTEGER NOT NULL REFERENCES jewell_types(id),
    description TEXT,
    image_path VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 16. Jewell Conditions Table
**Purpose**: Item condition standards

```sql
CREATE TABLE jewell_conditions (
    id SERIAL PRIMARY KEY,
    condition_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    percentage_deduction DECIMAL(5,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 📋 Indexes and Performance

### Primary Indexes
All tables have primary key indexes automatically created.

### Business Indexes
```sql
-- Customer search optimization
CREATE INDEX idx_customers_phone ON customers(phone_number);
CREATE INDEX idx_customers_company ON customers(company_id);

-- Pledge performance
CREATE INDEX idx_pledges_customer ON pledges(customer_id);
CREATE INDEX idx_pledges_status ON pledges(status);
CREATE INDEX idx_pledges_date ON pledges(pledge_date);

-- Payment tracking
CREATE INDEX idx_payments_pledge ON pledge_payments(pledge_id);
CREATE INDEX idx_payments_date ON pledge_payments(payment_date);

-- Accounting performance
CREATE INDEX idx_ledger_voucher ON ledger_entries(voucher_id);
CREATE INDEX idx_ledger_account ON ledger_entries(account_id);
CREATE INDEX idx_ledger_date ON ledger_entries(transaction_date);
```

---

## 🔒 Data Integrity Rules

### Foreign Key Constraints
- All relationships enforced with foreign keys
- Cascade deletes where appropriate (pledge items, ledger entries)
- Restrict deletes for master data (companies, accounts)

### Check Constraints
```sql
-- Ensure positive amounts
ALTER TABLE pledges ADD CONSTRAINT chk_pledge_amount_positive 
CHECK (pledge_amount > 0);

ALTER TABLE pledge_payments ADD CONSTRAINT chk_payment_amount_positive 
CHECK (amount > 0);

-- Ensure valid interest rates
ALTER TABLE schemes ADD CONSTRAINT chk_interest_rate_valid 
CHECK (interest_rate >= 0 AND interest_rate <= 100);

-- Ensure double entry balance
-- (Implemented at application level)
```

### Unique Constraints
```sql
-- Business rules
ALTER TABLE customers ADD CONSTRAINT uq_customer_phone_company 
UNIQUE (phone_number, company_id);

ALTER TABLE pledges ADD CONSTRAINT uq_pledge_number 
UNIQUE (pledge_number);

ALTER TABLE accounts_master ADD CONSTRAINT uq_account_code_company 
UNIQUE (account_code, company_id);
```

---

## 📊 Data Flow

### Pledge Creation Flow
1. Customer record created/verified
2. Pledge record with items created
3. Voucher master entry created
4. Ledger entries for double-entry:
   - Debit: Pledged Ornaments (Asset)
   - Credit: Customer Account (Liability)

### Payment Processing Flow
1. Payment record created
2. Pledge balance updated
3. Voucher master entry created
4. Ledger entries:
   - Debit: Cash/Bank (Asset)
   - Credit: Customer Account (Liability)
   - Credit: Interest Income (if applicable)

### Interest Calculation Flow
1. Monthly batch job identifies due pledges
2. Interest calculated based on scheme
3. Voucher and ledger entries created:
   - Debit: Customer Account (Liability)
   - Credit: Interest Income

---

## 🔧 Maintenance Procedures

### Regular Maintenance
1. **Daily**: Backup transaction logs
2. **Weekly**: Analyze query performance
3. **Monthly**: Update statistics and reindex
4. **Quarterly**: Archive old data

### Data Archival
- Settled pledges older than 7 years
- Payment records older than 7 years  
- Audit logs older than 3 years

### Performance Monitoring
- Monitor slow queries (> 1 second)
- Track table growth rates
- Monitor index usage statistics

---

## 📈 Scaling Considerations

### Horizontal Scaling
- Company-based partitioning possible
- Read replicas for reporting
- Separate OLTP/OLAP systems

### Vertical Scaling
- Connection pooling configured
- Query optimization ongoing
- Index tuning based on usage patterns

---

**Database Version**: PostgreSQL 12+
**ORM**: SQLAlchemy 1.4+
**Last Updated**: January 15, 2025
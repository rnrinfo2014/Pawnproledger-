-- =============================================
-- PawnPro Ledger - Optimized PostgreSQL Schema
-- =============================================

-- 1. Chart of Accounts (Unified Master and Sub Accounts)
CREATE TABLE accounts_master (
    account_id SERIAL PRIMARY KEY,
    account_name VARCHAR(255) NOT NULL,
    account_code VARCHAR(50) UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES accounts_master(account_id) ON DELETE CASCADE,
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('Asset', 'Liability', 'Income', 'Expense', 'Equity')),
    group_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    company_id INTEGER NOT NULL, -- Assuming multi-company support
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_account_type CHECK (account_type IN ('Asset', 'Liability', 'Income', 'Expense', 'Equity')),
    CONSTRAINT chk_parent_not_self CHECK (parent_id IS NULL OR parent_id != account_id)
);

-- 2. Voucher Master (Transaction Batches)
CREATE TABLE voucher_master (
    voucher_id SERIAL PRIMARY KEY,
    voucher_type VARCHAR(20) NOT NULL CHECK (voucher_type IN ('Pledge', 'Receipt', 'Payment', 'Journal', 'Auction')),
    voucher_date DATE NOT NULL DEFAULT CURRENT_DATE,
    narration TEXT,
    created_by INTEGER NOT NULL, -- FK to users table
    company_id INTEGER NOT NULL, -- Assuming multi-company support
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_voucher_type CHECK (voucher_type IN ('Pledge', 'Receipt', 'Payment', 'Journal', 'Auction'))
);

-- 3. Ledger Entries (Individual Transaction Lines)
CREATE TABLE ledger_entries (
    entry_id SERIAL PRIMARY KEY,
    voucher_id INTEGER NOT NULL REFERENCES voucher_master(voucher_id) ON DELETE CASCADE,
    account_id INTEGER NOT NULL REFERENCES accounts_master(account_id) ON DELETE CASCADE,
    dr_cr CHAR(1) NOT NULL CHECK (dr_cr IN ('D', 'C')),
    amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    narration TEXT,
    entry_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_dr_cr CHECK (dr_cr IN ('D', 'C')),
    CONSTRAINT chk_amount_positive CHECK (amount > 0)
);

-- =============================================
-- Indexes for Performance
-- =============================================

-- Accounts Master Indexes
CREATE INDEX idx_accounts_master_parent_id ON accounts_master(parent_id);
CREATE INDEX idx_accounts_master_account_type ON accounts_master(account_type);
CREATE INDEX idx_accounts_master_company_id ON accounts_master(company_id);
CREATE INDEX idx_accounts_master_account_code ON accounts_master(account_code);

-- Voucher Master Indexes
CREATE INDEX idx_voucher_master_voucher_type ON voucher_master(voucher_type);
CREATE INDEX idx_voucher_master_voucher_date ON voucher_master(voucher_date);
CREATE INDEX idx_voucher_master_company_id ON voucher_master(company_id);
CREATE INDEX idx_voucher_master_created_by ON voucher_master(created_by);

-- Ledger Entries Indexes
CREATE INDEX idx_ledger_entries_voucher_id ON ledger_entries(voucher_id);
CREATE INDEX idx_ledger_entries_account_id ON ledger_entries(account_id);
CREATE INDEX idx_ledger_entries_entry_date ON ledger_entries(entry_date);
CREATE INDEX idx_ledger_entries_dr_cr ON ledger_entries(dr_cr);

-- =============================================
-- Additional Constraints and Triggers
-- =============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_accounts_master_updated_at BEFORE UPDATE ON accounts_master
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_voucher_master_updated_at BEFORE UPDATE ON voucher_master
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- Sample Data (Optional)
-- =============================================

-- Insert root level accounts (Assets)
INSERT INTO accounts_master (account_name, account_code, account_type, group_name, company_id) VALUES
('Current Assets', '1000', 'Asset', 'Assets', 1),
('Fixed Assets', '2000', 'Asset', 'Assets', 1),
('Current Liabilities', '3000', 'Liability', 'Liabilities', 1),
('Capital', '4000', 'Equity', 'Equity', 1),
('Revenue', '5000', 'Income', 'Income', 1),
('Expenses', '6000', 'Expense', 'Expenses', 1);

-- Insert child accounts
INSERT INTO accounts_master (account_name, account_code, parent_id, account_type, group_name, company_id) VALUES
('Cash in Hand', '1001', 1, 'Asset', 'Current Assets', 1),
('Bank Account', '1002', 1, 'Asset', 'Current Assets', 1),
('Gold Inventory', '1003', 1, 'Asset', 'Current Assets', 1),
('Customer Loans', '3001', 3, 'Liability', 'Current Liabilities', 1),
('Pawn Interest Income', '5001', 5, 'Income', 'Revenue', 1),
('Administrative Expenses', '6001', 6, 'Expense', 'Expenses', 1);

-- =============================================
-- Migration Script: Current Structure → New Optimized Structure
-- =============================================

-- Step 1: Backup existing data (Run this first!)
CREATE TABLE backup_master_accounts AS SELECT * FROM master_accounts;
CREATE TABLE backup_sub_accounts AS SELECT * FROM sub_accounts;
CREATE TABLE backup_ledger_transactions AS SELECT * FROM ledger_transactions;

-- Step 2: Create new tables (from optimized_ledger_schema.sql)

-- Step 3: Migrate Master Accounts to accounts_master
INSERT INTO accounts_master (account_name, account_code, account_type, group_name, company_id, created_at)
SELECT
    name,
    CONCAT('MA-', LPAD(id::TEXT, 4, '0')), -- Generate account codes
    UPPER(type), -- Convert to uppercase
    type, -- Use type as group_name temporarily
    company_id,
    created_at
FROM master_accounts;

-- Step 4: Migrate Sub Accounts to accounts_master (as children)
INSERT INTO accounts_master (account_name, account_code, parent_id, account_type, group_name, company_id, created_at)
SELECT
    sa.name,
    COALESCE(sa.acc_code, CONCAT('SA-', LPAD(sa.id::TEXT, 4, '0'))),
    am.account_id, -- Parent ID from master accounts
    UPPER(ma.type),
    ma.type,
    sa.company_id,
    sa.created_at
FROM sub_accounts sa
JOIN master_accounts ma ON sa.master_account_id = ma.id
JOIN accounts_master am ON am.account_name = ma.name AND am.company_id = ma.company_id;

-- Step 5: Create vouchers for existing transactions
INSERT INTO voucher_master (voucher_type, voucher_date, narration, created_by, company_id, created_at)
SELECT
    CASE
        WHEN transaction_type = 'credit' THEN 'Receipt'
        WHEN transaction_type = 'debit' THEN 'Payment'
        ELSE 'Journal'
    END,
    transaction_date,
    COALESCE(narration, 'Migrated transaction'),
    created_by,
    company_id,
    created_at
FROM ledger_transactions
GROUP BY transaction_date, narration, created_by, company_id, created_at, transaction_type;

-- Step 6: Migrate ledger transactions to ledger_entries
INSERT INTO ledger_entries (voucher_id, account_id, dr_cr, amount, narration, entry_date, created_at)
SELECT
    vm.voucher_id,
    am.account_id,
    CASE
        WHEN lt.debit > 0 THEN 'D'
        WHEN lt.credit > 0 THEN 'C'
        ELSE 'D' -- Default to debit
    END,
    COALESCE(lt.debit, lt.credit, 0),
    lt.narration,
    lt.transaction_date,
    lt.created_at
FROM ledger_transactions lt
JOIN accounts_master am ON am.account_code = lt.account_code
JOIN voucher_master vm ON vm.voucher_date = lt.transaction_date
    AND vm.created_by = lt.created_by
    AND vm.company_id = lt.company_id;

-- Step 7: Update sequences (if needed)
SELECT setval('accounts_master_account_id_seq', (SELECT MAX(account_id) FROM accounts_master));
SELECT setval('voucher_master_voucher_id_seq', (SELECT MAX(voucher_id) FROM voucher_master));
SELECT setval('ledger_entries_entry_id_seq', (SELECT MAX(entry_id) FROM ledger_entries));

-- Step 8: Verify data integrity
-- Check that debits equal credits for each voucher
SELECT
    voucher_id,
    SUM(CASE WHEN dr_cr = 'D' THEN amount ELSE 0 END) as total_debit,
    SUM(CASE WHEN dr_cr = 'C' THEN amount ELSE 0 END) as total_credit,
    SUM(CASE WHEN dr_cr = 'D' THEN amount ELSE 0 END) - SUM(CASE WHEN dr_cr = 'C' THEN amount ELSE 0 END) as difference
FROM ledger_entries
GROUP BY voucher_id
HAVING SUM(CASE WHEN dr_cr = 'D' THEN amount ELSE 0 END) != SUM(CASE WHEN dr_cr = 'C' THEN amount ELSE 0 END);

-- Step 9: Drop old tables (ONLY AFTER VERIFYING MIGRATION SUCCESS)
-- DROP TABLE ledger_transactions;
-- DROP TABLE sub_accounts;
-- DROP TABLE master_accounts;

-- Step 10: Rename new tables to match old names (optional)
-- ALTER TABLE accounts_master RENAME TO master_accounts;
-- ALTER TABLE voucher_master RENAME TO vouchers;
-- ALTER TABLE ledger_entries RENAME TO ledger_transactions;

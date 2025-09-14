#!/usr/bin/env python3
"""
Migration script to update PawnPro database to new accounting structure
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from config import settings

def run_migration():
    # Database connection
    DATABASE_URL = settings.database_url
    engine = create_engine(DATABASE_URL)

    print("🔄 Starting database migration to new accounting structure...")

    try:
        with engine.connect() as conn:
            # Step 1: Backup existing data
            print("📦 Backing up existing data...")
            conn.execute(text("CREATE TABLE IF NOT EXISTS backup_master_accounts AS SELECT * FROM master_accounts;"))
            # Only backup sub_accounts if the table exists
            try:
                conn.execute(text("CREATE TABLE IF NOT EXISTS backup_sub_accounts AS SELECT * FROM sub_accounts;"))
                print("✅ Sub-accounts backup completed")
            except:
                print("ℹ️ Sub-accounts table not found, skipping backup")
            conn.execute(text("CREATE TABLE IF NOT EXISTS backup_ledger_transactions AS SELECT * FROM ledger_transactions;"))
            conn.commit()
            print("✅ Backup completed")

            # Step 2: Create new tables
            print("🏗️ Creating new tables...")

            # accounts_master table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS accounts_master (
                    account_id SERIAL PRIMARY KEY,
                    account_name VARCHAR(255) NOT NULL,
                    account_code VARCHAR(50) UNIQUE NOT NULL,
                    parent_id INTEGER REFERENCES accounts_master(account_id) ON DELETE CASCADE,
                    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('Asset', 'Liability', 'Income', 'Expense', 'Equity')),
                    group_name VARCHAR(100),
                    is_active BOOLEAN DEFAULT TRUE,
                    company_id INTEGER NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # voucher_master table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS voucher_master (
                    voucher_id SERIAL PRIMARY KEY,
                    voucher_type VARCHAR(20) NOT NULL CHECK (voucher_type IN ('Pledge', 'Receipt', 'Payment', 'Journal', 'Auction')),
                    voucher_date DATE NOT NULL DEFAULT CURRENT_DATE,
                    narration TEXT,
                    created_by INTEGER NOT NULL,
                    company_id INTEGER NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # ledger_entries table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS ledger_entries (
                    entry_id SERIAL PRIMARY KEY,
                    voucher_id INTEGER NOT NULL REFERENCES voucher_master(voucher_id) ON DELETE CASCADE,
                    account_id INTEGER NOT NULL REFERENCES accounts_master(account_id) ON DELETE CASCADE,
                    dr_cr CHAR(1) NOT NULL CHECK (dr_cr IN ('D', 'C')),
                    amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
                    narration TEXT,
                    entry_date DATE NOT NULL DEFAULT CURRENT_DATE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # Create indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_accounts_master_parent_id ON accounts_master(parent_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_accounts_master_account_type ON accounts_master(account_type);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_accounts_master_company_id ON accounts_master(company_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_accounts_master_account_code ON accounts_master(account_code);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_voucher_master_voucher_type ON voucher_master(voucher_type);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_voucher_master_voucher_date ON voucher_master(voucher_date);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_voucher_master_company_id ON voucher_master(company_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_voucher_master_created_by ON voucher_master(created_by);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ledger_entries_voucher_id ON ledger_entries(voucher_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ledger_entries_account_id ON ledger_entries(account_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ledger_entries_entry_date ON ledger_entries(entry_date);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ledger_entries_dr_cr ON ledger_entries(dr_cr);"))

            conn.commit()
            print("✅ New tables created successfully")

            # Step 3: Check if data exists and migrate
            result = conn.execute(text("SELECT COUNT(*) FROM master_accounts;"))
            master_count = result.fetchone()[0]

            if master_count > 0:
                print(f"📊 Found {master_count} master accounts to migrate...")

                # Migrate Master Accounts
                conn.execute(text("""
                    INSERT INTO accounts_master (account_name, account_code, account_type, group_name, company_id, created_at)
                    SELECT
                        name,
                        CONCAT('MA-', LPAD(id::TEXT, 4, '0')),
                        CASE LOWER(type)
                            WHEN 'asset' THEN 'Asset'
                            WHEN 'liability' THEN 'Liability'
                            WHEN 'income' THEN 'Income'
                            WHEN 'expense' THEN 'Expense'
                            WHEN 'equity' THEN 'Equity'
                            ELSE 'Asset'
                        END,
                        type,
                        company_id,
                        created_at
                    FROM master_accounts;
                """))

                # Migrate Sub Accounts (only if table exists)
                try:
                    result = conn.execute(text("SELECT COUNT(*) FROM sub_accounts;"))
                    row = result.fetchone()
                    sub_count = row[0] if row else 0
                    print(f"📊 Found {sub_count} sub accounts to migrate...")

                    if sub_count > 0:
                        conn.execute(text("""
                            INSERT INTO accounts_master (account_name, account_code, parent_id, account_type, group_name, company_id, created_at)
                            SELECT
                                sa.name,
                                COALESCE(sa.acc_code, CONCAT('SA-', LPAD(sa.id::TEXT, 4, '0'))),
                                am.account_id,
                                CASE LOWER(ma.type)
                                    WHEN 'asset' THEN 'Asset'
                                    WHEN 'liability' THEN 'Liability'
                                    WHEN 'income' THEN 'Income'
                                    WHEN 'expense' THEN 'Expense'
                                    WHEN 'equity' THEN 'Equity'
                                    ELSE 'Asset'
                                END,
                                ma.type,
                                sa.company_id,
                                sa.created_at
                            FROM sub_accounts sa
                            JOIN master_accounts ma ON sa.master_account_id = ma.id
                            JOIN accounts_master am ON am.account_name = ma.name AND am.company_id = ma.company_id;
                        """))
                        print("✅ Sub-accounts migrated")
                    else:
                        print("ℹ️ No sub-accounts found to migrate")
                except:
                    print("ℹ️ Sub-accounts table not found, skipping migration")

                # Migrate Transactions
                result = conn.execute(text("SELECT COUNT(*) FROM ledger_transactions;"))
                trans_count = result.fetchone()[0]
                print(f"📊 Found {trans_count} transactions to migrate...")

                # Create vouchers for transactions
                conn.execute(text("""
                    INSERT INTO voucher_master (voucher_type, voucher_date, narration, created_by, company_id, created_at)
                    SELECT DISTINCT
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
                    FROM ledger_transactions;
                """))

                # Migrate ledger entries
                conn.execute(text("""
                    INSERT INTO ledger_entries (voucher_id, account_id, dr_cr, amount, narration, entry_date, created_at)
                    SELECT
                        vm.voucher_id,
                        am.account_id,
                        CASE
                            WHEN lt.debit > 0 THEN 'D'
                            WHEN lt.credit > 0 THEN 'C'
                            ELSE 'D'
                        END,
                        COALESCE(GREATEST(lt.debit, lt.credit), 0),
                        lt.narration,
                        lt.transaction_date,
                        lt.created_at
                    FROM ledger_transactions lt
                    JOIN accounts_master am ON am.account_code = lt.account_code
                    JOIN voucher_master vm ON vm.voucher_date = lt.transaction_date
                        AND vm.created_by = lt.created_by
                        AND vm.company_id = lt.company_id;
                """))

                conn.commit()
                print("✅ Data migration completed successfully")

                # Verify migration
                result = conn.execute(text("SELECT COUNT(*) FROM accounts_master;"))
                new_accounts = result.fetchone()[0]
                result = conn.execute(text("SELECT COUNT(*) FROM voucher_master;"))
                new_vouchers = result.fetchone()[0]
                result = conn.execute(text("SELECT COUNT(*) FROM ledger_entries;"))
                new_entries = result.fetchone()[0]

                print(f"📈 Migration Summary:")
                print(f"   - Accounts migrated: {new_accounts}")
                print(f"   - Vouchers created: {new_vouchers}")
                print(f"   - Ledger entries: {new_entries}")

            else:
                print("ℹ️ No existing data found. Creating sample data...")

                # Insert sample chart of accounts
                conn.execute(text("""
                    INSERT INTO accounts_master (account_name, account_code, account_type, group_name, company_id) VALUES
                    ('Current Assets', '1000', 'Asset', 'Assets', 1),
                    ('Fixed Assets', '2000', 'Asset', 'Assets', 1),
                    ('Current Liabilities', '3000', 'Liability', 'Liabilities', 1),
                    ('Capital', '4000', 'Equity', 'Equity', 1),
                    ('Revenue', '5000', 'Income', 'Income', 1),
                    ('Expenses', '6000', 'Expense', 'Expenses', 1);
                """))

                # Insert sample child accounts
                conn.execute(text("""
                    INSERT INTO accounts_master (account_name, account_code, parent_id, account_type, group_name, company_id) VALUES
                    ('Cash in Hand', '1001', (SELECT account_id FROM accounts_master WHERE account_code = '1000'), 'Asset', 'Current Assets', 1),
                    ('Bank Account', '1002', (SELECT account_id FROM accounts_master WHERE account_code = '1000'), 'Asset', 'Current Assets', 1),
                    ('Gold Inventory', '1003', (SELECT account_id FROM accounts_master WHERE account_code = '1000'), 'Asset', 'Current Assets', 1),
                    ('Customer Loans', '3001', (SELECT account_id FROM accounts_master WHERE account_code = '3000'), 'Liability', 'Current Liabilities', 1),
                    ('Pawn Interest Income', '5001', (SELECT account_id FROM accounts_master WHERE account_code = '5000'), 'Income', 'Revenue', 1),
                    ('Administrative Expenses', '6001', (SELECT account_id FROM accounts_master WHERE account_code = '6000'), 'Expense', 'Expenses', 1);
                """))

                conn.commit()
                print("✅ Sample chart of accounts created")

            print("🎉 Migration completed successfully!")
            print("\n📝 Next steps:")
            print("1. Update your application code to use the new models")
            print("2. Test the new endpoints")
            print("3. Verify data integrity")
            print("4. Remove old tables when ready (after thorough testing)")

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_migration()

#!/usr/bin/env python3
"""
Create Bank table migration script
Run this script to create the banks table in your database.
"""

from sqlalchemy import create_engine, text
from config import settings

def create_bank_table():
    """Create the banks table"""
    
    # Create engine
    engine = create_engine(settings.database_url)
    
    # SQL to create banks table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS banks (
        id SERIAL PRIMARY KEY,
        bank_name VARCHAR(200) NOT NULL,
        branch_name VARCHAR(200),
        ifsc_code VARCHAR(15),
        account_number VARCHAR(50),
        account_holder_name VARCHAR(200),
        address TEXT,
        city VARCHAR(100),
        state VARCHAR(100),
        pincode VARCHAR(10),
        phone VARCHAR(15),
        email VARCHAR(100),
        manager_name VARCHAR(200),
        manager_phone VARCHAR(15),
        status VARCHAR(20) DEFAULT 'active',
        remarks TEXT,
        company_id INTEGER NOT NULL REFERENCES companies(id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE,
        
        -- Create indexes for better performance
        CONSTRAINT banks_company_bank_branch_unique UNIQUE (company_id, bank_name, branch_name)
    );
    
    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_banks_company_id ON banks(company_id);
    CREATE INDEX IF NOT EXISTS idx_banks_status ON banks(status);
    CREATE INDEX IF NOT EXISTS idx_banks_bank_name ON banks(bank_name);
    CREATE INDEX IF NOT EXISTS idx_banks_ifsc_code ON banks(ifsc_code);
    """
    
    try:
        with engine.connect() as connection:
            # Execute the create table statement
            connection.execute(text(create_table_sql))
            connection.commit()
            print("✅ Banks table created successfully!")
            print("📊 Created indexes for optimal performance")
            print("🔐 Added unique constraint for company + bank + branch combination")
            
    except Exception as e:
        print(f"❌ Error creating banks table: {e}")
        raise

if __name__ == "__main__":
    print("🏦 Creating Banks table...")
    create_bank_table()
    print("🎉 Bank table setup complete!")
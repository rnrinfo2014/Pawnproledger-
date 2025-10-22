#!/usr/bin/env python3
"""
Check existing voucher types and update constraint safely
"""

import psycopg2

def check_existing_voucher_types():
    """Check what voucher types exist in the database"""
    
    try:
        # Connect to database
        conn = psycopg2.connect('postgresql://postgres:rnrinfo@localhost:5432/pawnpro')
        cur = conn.cursor()
        
        print("🔍 Checking existing voucher types...")
        
        # Get all unique voucher types
        cur.execute("""
        SELECT voucher_type, COUNT(*) 
        FROM voucher_master 
        GROUP BY voucher_type 
        ORDER BY COUNT(*) DESC
        """)
        
        voucher_types = cur.fetchall()
        
        print("📊 Existing voucher types in database:")
        all_types = []
        for vtype, count in voucher_types:
            print(f"   {vtype}: {count} records")
            all_types.append(vtype)
        
        print(f"\n📋 All voucher types found: {all_types}")
        
        # Check current constraint
        cur.execute("""
        SELECT pg_get_constraintdef(oid) 
        FROM pg_constraint 
        WHERE conrelid = 'voucher_master'::regclass 
        AND conname = 'voucher_master_voucher_type_check'
        """)
        
        result = cur.fetchone()
        if result:
            print(f"\n🎯 Current constraint: {result[0]}")
        
        # Now create a new constraint that includes all existing types plus Income and Expense
        allowed_types = list(set(all_types + ['Income', 'Expense']))
        print(f"\n✨ Recommended allowed types: {allowed_types}")
        
        # Drop existing constraint
        print("\n🗑️ Dropping old constraint...")
        cur.execute("ALTER TABLE voucher_master DROP CONSTRAINT IF EXISTS voucher_master_voucher_type_check")
        
        # Create new constraint with all necessary types
        type_list = "', '".join(allowed_types)
        constraint_sql = f"""
        ALTER TABLE voucher_master 
        ADD CONSTRAINT voucher_master_voucher_type_check 
        CHECK (voucher_type IN ('{type_list}'))
        """
        
        print(f"➕ Adding new constraint...")
        print(f"   SQL: {constraint_sql}")
        
        cur.execute(constraint_sql)
        conn.commit()
        
        print("✅ Constraint updated successfully!")
        
        # Verify the new constraint
        cur.execute("""
        SELECT pg_get_constraintdef(oid) 
        FROM pg_constraint 
        WHERE conrelid = 'voucher_master'::regclass 
        AND conname = 'voucher_master_voucher_type_check'
        """)
        
        result = cur.fetchone()
        if result:
            print(f"\n🎉 New constraint: {result[0]}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    check_existing_voucher_types()
#!/usr/bin/env python3
"""
Check and fix voucher_type constraint in database
"""

import psycopg2

def check_and_fix_voucher_constraint():
    """Check and fix voucher_type constraint"""
    
    try:
        # Connect to database
        conn = psycopg2.connect('postgresql://postgres:rnrinfo@localhost:5432/pawnpro')
        cur = conn.cursor()
        
        print("🔍 Checking current voucher_master constraints...")
        
        # Check current constraints
        cur.execute("""
        SELECT conname, pg_get_constraintdef(oid) 
        FROM pg_constraint 
        WHERE conrelid = 'voucher_master'::regclass 
        AND contype = 'c'
        """)
        
        constraints = cur.fetchall()
        
        print("📋 Current constraints:")
        for name, definition in constraints:
            print(f"   {name}: {definition}")
        
        # Check if voucher_type_check constraint exists and what values it allows
        cur.execute("""
        SELECT pg_get_constraintdef(oid) 
        FROM pg_constraint 
        WHERE conrelid = 'voucher_master'::regclass 
        AND conname = 'voucher_master_voucher_type_check'
        """)
        
        result = cur.fetchone()
        
        if result:
            current_constraint = result[0]
            print(f"\n🎯 Current voucher_type constraint: {current_constraint}")
            
            # Check if Income and Expense are allowed
            if 'Income' not in current_constraint or 'Expense' not in current_constraint:
                print("\n⚠️ Need to update constraint to allow Income and Expense values")
                
                # Drop existing constraint
                print("🗑️ Dropping old constraint...")
                cur.execute("ALTER TABLE voucher_master DROP CONSTRAINT voucher_master_voucher_type_check")
                
                # Add new constraint with Income and Expense
                print("➕ Adding new constraint...")
                cur.execute("""
                ALTER TABLE voucher_master 
                ADD CONSTRAINT voucher_master_voucher_type_check 
                CHECK (voucher_type IN ('Receipt', 'Payment', 'Journal', 'Income', 'Expense'))
                """)
                
                conn.commit()
                print("✅ Constraint updated successfully!")
                
            else:
                print("✅ Constraint already allows Income and Expense values")
        
        else:
            print("\n❌ No voucher_type_check constraint found")
            
            # Add the constraint
            print("➕ Adding voucher_type constraint...")
            cur.execute("""
            ALTER TABLE voucher_master 
            ADD CONSTRAINT voucher_master_voucher_type_check 
            CHECK (voucher_type IN ('Receipt', 'Payment', 'Journal', 'Income', 'Expense'))
            """)
            
            conn.commit()
            print("✅ Constraint added successfully!")
        
        # Verify the fix
        print("\n🔍 Verifying updated constraints...")
        cur.execute("""
        SELECT conname, pg_get_constraintdef(oid) 
        FROM pg_constraint 
        WHERE conrelid = 'voucher_master'::regclass 
        AND contype = 'c'
        """)
        
        updated_constraints = cur.fetchall()
        
        print("📋 Updated constraints:")
        for name, definition in updated_constraints:
            print(f"   {name}: {definition}")
        
        cur.close()
        conn.close()
        
        print("\n🎉 Database constraint fix completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    check_and_fix_voucher_constraint()
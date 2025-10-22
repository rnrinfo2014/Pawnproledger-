#!/usr/bin/env python3
"""
Test imports and find the actual error
"""

try:
    print("Testing imports...")
    
    import sys
    import os
    os.chdir('PawnProApi')
    
    print("1. Testing pledge_accounting_manager import...")
    from pledge_accounting_manager import create_complete_pledge_accounting
    print("   SUCCESS: pledge_accounting_manager imported")
    
    print("2. Testing customer_coa_manager import...")
    from customer_coa_manager import create_customer_coa_account
    print("   SUCCESS: customer_coa_manager imported")
    
    print("3. Testing models import...")
    from models import Pledge, Customer, LedgerEntry
    print("   SUCCESS: models imported")
    
    print("4. Testing database connection...")
    from database import SessionLocal
    db = SessionLocal()
    print("   SUCCESS: database connection")
    db.close()
    
    print("\nAll imports successful! The error must be in the pledge creation logic.")
    
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
except Exception as e:
    print(f"OTHER ERROR: {e}")
    import traceback
    traceback.print_exc()
"""
Simple execution script for Customer COA setup
Run each step manually with proper error handling
"""

def main():
    print("🚀 Customer COA Integration Setup")
    print("=" * 50)
    
    print("\nPlease run the following steps manually:")
    print("\n1. Clear all data:")
    print("   python clear_all_data.py")
    
    print("\n2. Run database migration:")
    print("   python migrate_customer_coa.py")
    
    print("\n3. Start the server:")
    print("   python -m uvicorn main:app --reload")
    
    print("\n4. Initialize COA via API:")
    print("   POST http://localhost:8000/api/v1/coa/initialize/1")
    
    print("\n5. Create test customer via API:")
    print("   POST http://localhost:8000/customers")
    print("   {")
    print('     "name": "Test Customer",')
    print('     "phone": "+91-9876543210",')
    print('     "address": "123 Test Street",')
    print('     "company_id": 1,')
    print('     "created_by": 1')
    print("   }")
    
    print("\n6. Check customer balance:")
    print("   GET http://localhost:8000/customers/1/balance")
    
    print("\n✅ Customer COA integration features:")
    print("   - Auto COA account creation on customer create")
    print("   - COA account name update on customer update")  
    print("   - Safe COA account handling on customer delete")
    print("   - Customer balance inquiry")
    print("   - Migration for existing customers")

if __name__ == "__main__":
    main()
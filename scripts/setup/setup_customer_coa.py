"""
Complete Setup Script for Customer COA Integration
1. Clear all data
2. Create tables
3. Run migration
4. Initialize COA
5. Test customer creation with COA
"""

import os
import sys
from database import SessionLocal, engine
from models import Base
from clear_all_data import clear_all_data
from migrate_customer_coa import add_customer_coa_column, create_index_on_coa_account
from customer_coa_manager import migrate_existing_customers_to_coa

def create_tables():
    """Create all database tables"""
    try:
        print("🏗️ Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False

def initialize_coa(company_id: int = 1):
    """Initialize Chart of Accounts for a company"""
    try:
        print(f"📊 Initializing COA for company {company_id}...")
        
        # Import here to avoid circular imports
        from coa_api import initialize_coa_for_company
        
        db = SessionLocal()
        try:
            # Create a test company first
            from models import Company as CompanyModel
            company = CompanyModel(
                name="Test Pawn Shop",
                address="123 Main Street",
                city="Test City", 
                phone_number="+91-9876543210",
                license_no="TEST-LICENSE-001",
                status="active"
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            
            # Initialize COA
            result = initialize_coa_for_company(company.id, db)
            print("✅ COA initialized successfully!")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error initializing COA: {str(e)}")
        return False

def create_test_user():
    """Create a test admin user"""
    try:
        print("👤 Creating test admin user...")
        
        from models import User as UserModel
        from auth import get_password_hash
        
        db = SessionLocal()
        try:
            # Check if user exists
            existing_user = db.query(UserModel).filter(UserModel.username == "admin").first()
            if existing_user:
                print("✅ Admin user already exists")
                return True
            
            # Create admin user
            admin_user = UserModel(
                username="admin",
                email="admin@rnrinfo.dev",
                password_hash=get_password_hash("admin123"),
                role="admin",
                company_id=1
            )
            db.add(admin_user)
            db.commit()
            
            print("✅ Admin user created successfully!")
            print("   Username: admin")
            print("   Password: admin123")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        return False

def test_customer_creation():
    """Test customer creation with COA account"""
    try:
        print("🧪 Testing customer creation with COA...")
        
        from models import Customer as CustomerModel, Area as AreaModel
        from customer_coa_manager import create_customer_coa_account
        
        db = SessionLocal()
        try:
            # Create test area
            area = AreaModel(
                area_name="Test Area",
                city="Test City",
                status="active",
                company_id=1
            )
            db.add(area)
            db.commit()
            db.refresh(area)
            
            # Create test customer
            customer = CustomerModel(
                name="Test Customer",
                address="123 Test Street",
                city="Test City",
                area_id=area.id,
                phone="+91-9876543210",
                acc_code="C-0001",
                id_proof_type="Aadhaar",
                company_id=1,
                created_by=1
            )
            db.add(customer)
            db.flush()
            
            # Create COA account
            create_customer_coa_account(db, customer, 1)
            db.commit()
            
            print(f"✅ Test customer created: {customer.name} ({customer.acc_code})")
            print(f"   COA Account ID: {customer.coa_account_id}")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error testing customer creation: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Starting Customer COA Integration Setup...")
    print("=" * 60)
    
    # Step 1: Clear all data
    print("\n📋 Step 1: Clearing all data...")
    clear_all_data()
    
    # Step 2: Create tables
    print("\n📋 Step 2: Creating database tables...")
    if not create_tables():
        print("❌ Failed to create tables. Stopping setup.")
        return False
    
    # Step 3: Run migration (add COA column)
    print("\n📋 Step 3: Running database migration...")
    success1 = add_customer_coa_column()
    success2 = create_index_on_coa_account()
    
    if not (success1 and success2):
        print("❌ Migration failed. Stopping setup.")
        return False
    
    # Step 4: Create test user
    print("\n📋 Step 4: Creating test admin user...")
    if not create_test_user():
        print("❌ Failed to create admin user. Stopping setup.")
        return False
    
    # Step 5: Initialize COA
    print("\n📋 Step 5: Initializing Chart of Accounts...")
    if not initialize_coa():
        print("❌ Failed to initialize COA. Stopping setup.")
        return False
    
    # Step 6: Test customer creation
    print("\n📋 Step 6: Testing customer creation with COA...")
    if not test_customer_creation():
        print("❌ Failed to test customer creation. Stopping setup.")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Customer COA Integration Setup Completed Successfully!")
    print("\n📊 Summary:")
    print("   ✅ Database cleared and recreated")
    print("   ✅ Customer COA column added")
    print("   ✅ Admin user created (admin/admin123)")
    print("   ✅ Chart of Accounts initialized")
    print("   ✅ Test customer created with COA account")
    print("\n🚀 You can now start the server and test customer creation!")
    print("   python -m uvicorn main:app --reload")
    
    return True

if __name__ == "__main__":
    print("⚠️ WARNING: This will delete ALL data and recreate everything!")
    confirm = input("Type 'SETUP CUSTOMER COA' to confirm: ")
    
    if confirm == "SETUP CUSTOMER COA":
        main()
    else:
        print("❌ Setup cancelled.")
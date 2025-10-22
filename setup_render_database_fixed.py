#!/usr/bin/env python3
"""
Complete Render Database Setup - CORRECTED VERSION
Creates all tables, schema, and master data for fresh Render PostgreSQL database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import Base, engine, get_db
from src.core.models import *
from src.auth.auth import get_password_hash  # Import the correct password hashing function
from sqlalchemy.orm import Session
from datetime import datetime

def create_all_tables():
    """Create all tables using SQLAlchemy models"""
    print("🏗️  Creating all database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def setup_companies():
    """Setup company master data FIRST"""
    print("\n🏢 Setting up Companies...")
    
    try:
        db = next(get_db())
        
        # Check if company already exists
        existing = db.query(Company).filter_by(id=1).first()
        if not existing:
            company = Company(
                name='RNR Pawn Shop',
                address='123 Main Street, Chennai, Tamil Nadu',
                city='Chennai',
                phone_number='+91-9876543210'
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            print(f"✅ Company created with ID: {company.id}")
        else:
            print(f"✅ Company already exists with ID: {existing.id}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up companies: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def setup_users():
    """Setup user accounts"""
    print("\n👤 Setting up Users...")
    
    try:
        db = next(get_db())
        
        # Hash password using the same method as auth system
        password = "admin123"
        hashed_password = get_password_hash(password)
        
        existing = db.query(User).filter_by(username='admin').first()
        if not existing:
            user = User(
                username='admin',
                email='admin@rnrpawn.com',
                password_hash=hashed_password,
                role='admin',
                company_id=1
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Admin user created with ID: {user.id}")
            print("   Default login: admin / admin123")
        else:
            print(f"✅ Admin user already exists with ID: {existing.id}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up users: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def setup_chart_of_accounts():
    """Setup complete Chart of Accounts"""
    print("\n📊 Setting up Chart of Accounts...")
    
    accounts = [
        # Assets (1000-1999)
        {'account_code': '1001', 'account_name': 'Cash in Hand', 'account_type': 'Asset'},
        {'account_code': '1002', 'account_name': 'Bank Account', 'account_type': 'Asset'},
        {'account_code': '1003', 'account_name': 'Pledges Receivable', 'account_type': 'Asset'},
        {'account_code': '1004', 'account_name': 'Interest Receivable', 'account_type': 'Asset'},
        {'account_code': '1005', 'account_name': 'Auction Inventory', 'account_type': 'Asset'},
        
        # Liabilities (2000-2999)
        {'account_code': '2001', 'account_name': 'Accounts Payable', 'account_type': 'Liability'},
        {'account_code': '2002', 'account_name': 'Customer Deposits', 'account_type': 'Liability'},
        {'account_code': '2003', 'account_name': 'Tax Payable', 'account_type': 'Liability'},
        
        # Equity (3000-3999)
        {'account_code': '3001', 'account_name': 'Owner Equity', 'account_type': 'Equity'},
        {'account_code': '3002', 'account_name': 'Retained Earnings', 'account_type': 'Equity'},
        
        # Income (4000-4999)
        {'account_code': '4001', 'account_name': 'Pledge Interest Income', 'account_type': 'Income'},
        {'account_code': '4002', 'account_name': 'Auction Income', 'account_type': 'Income'},
        {'account_code': '4003', 'account_name': 'Service Charges Income', 'account_type': 'Income'},
        {'account_code': '4004', 'account_name': 'Penalty Income', 'account_type': 'Income'},
        {'account_code': '4005', 'account_name': 'Other Income', 'account_type': 'Income'},
        
        # Expenses (5000-5999)
        {'account_code': '5001', 'account_name': 'Staff Salaries', 'account_type': 'Expense'},
        {'account_code': '5002', 'account_name': 'Rent Expense', 'account_type': 'Expense'},
        {'account_code': '5003', 'account_name': 'Utility Bills', 'account_type': 'Expense'},
        {'account_code': '5004', 'account_name': 'Office Supplies', 'account_type': 'Expense'},
        {'account_code': '5005', 'account_name': 'Transportation', 'account_type': 'Expense'},
        {'account_code': '5006', 'account_name': 'Marketing Expense', 'account_type': 'Expense'},
        {'account_code': '5007', 'account_name': 'Legal & Professional', 'account_type': 'Expense'},
        {'account_code': '5008', 'account_name': 'Discount Expense', 'account_type': 'Expense'},
        
        # Customer Accounts (6000-6999)
        {'account_code': '6001', 'account_name': 'Customer Accounts', 'account_type': 'Asset'},
    ]
    
    try:
        db = next(get_db())
        created_count = 0
        
        for acc_data in accounts:
            # Check if account exists
            existing = db.query(MasterAccount).filter_by(account_code=acc_data['account_code']).first()
            if not existing:
                account = MasterAccount(
                    account_code=acc_data['account_code'],
                    account_name=acc_data['account_name'],
                    account_type=acc_data['account_type'],
                    company_id=1,
                    is_active=True
                )
                db.add(account)
                created_count += 1
        
        db.commit()
        print(f"✅ Chart of Accounts setup complete - {created_count} new accounts created")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up COA: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def setup_areas():
    """Setup areas/locations"""
    print("\n📍 Setting up Areas...")
    
    areas = [
        {'name': 'T. Nagar'},
        {'name': 'Anna Nagar'},
        {'name': 'Velachery'},
        {'name': 'Adyar'},
        {'name': 'Mylapore'},
    ]
    
    try:
        db = next(get_db())
        created_count = 0
        
        for area_data in areas:
            # Check if area exists
            existing = db.query(Area).filter_by(name=area_data['name']).first()
            if not existing:
                area = Area(
                    name=area_data['name'],
                    company_id=1,
                    status='active'
                )
                db.add(area)
                created_count += 1
        
        db.commit()
        print(f"✅ Areas setup complete - {created_count} new areas created")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up areas: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def setup_banks():
    """Setup bank master data"""
    print("\n🏦 Setting up Banks...")
    
    banks = [
        {'bank_name': 'State Bank of India', 'branch_name': 'T.Nagar Branch', 'account_name': 'RNR Pawn Shop'},
        {'bank_name': 'HDFC Bank', 'branch_name': 'Anna Nagar Branch', 'account_name': 'RNR Pawn Shop'},
        {'bank_name': 'ICICI Bank', 'branch_name': 'Velachery Branch', 'account_name': 'RNR Pawn Shop'},
    ]
    
    try:
        db = next(get_db())
        created_count = 0
        
        for bank_data in banks:
            # Check if bank exists
            existing = db.query(Bank).filter_by(bank_name=bank_data['bank_name'], branch_name=bank_data['branch_name']).first()
            if not existing:
                bank = Bank(
                    bank_name=bank_data['bank_name'],
                    branch_name=bank_data['branch_name'],
                    account_name=bank_data['account_name'],
                    company_id=1,
                    status='active'
                )
                db.add(bank)
                created_count += 1
        
        db.commit()
        print(f"✅ Banks setup complete - {created_count} new banks created")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up banks: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def setup_jewell_types():
    """Setup jewellery types"""
    print("\n💎 Setting up Jewellery Types...")
    
    jewell_types = [
        {'type_name': 'Gold'},
        {'type_name': 'Silver'},
        {'type_name': 'Diamond'},
        {'type_name': 'Platinum'},
    ]
    
    try:
        db = next(get_db())
        created_count = 0
        
        for jtype_data in jewell_types:
            existing = db.query(JewellType).filter_by(type_name=jtype_data['type_name']).first()
            if not existing:
                jtype = JewellType(
                    type_name=jtype_data['type_name'],
                    status='active'
                )
                db.add(jtype)
                created_count += 1
        
        db.commit()
        print(f"✅ Jewellery types setup complete - {created_count} new types created")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up jewellery types: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def verify_setup():
    """Verify the database setup"""
    print("\n🔍 Verifying Database Setup...")
    
    try:
        db = next(get_db())
        
        # Count records in each table
        tables = {
            'Companies': db.query(Company).count(),
            'Users': db.query(User).count(),
            'Accounts': db.query(MasterAccount).count(),
            'Areas': db.query(Area).count(),
            'Banks': db.query(Bank).count(),
            'Jewellery Types': db.query(JewellType).count(),
        }
        
        print("📊 Record counts:")
        for table, count in tables.items():
            print(f"   {table}: {count} records")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Starting Render Database Setup")
    print("=" * 50)
    
    steps = [
        ("Creating Tables", create_all_tables),
        ("Setting up Companies", setup_companies),
        ("Setting up Users", setup_users),
        ("Setting up Chart of Accounts", setup_chart_of_accounts),
        ("Setting up Areas", setup_areas),
        ("Setting up Banks", setup_banks),
        ("Setting up Jewellery Types", setup_jewell_types),
        ("Verifying Setup", verify_setup)
    ]
    
    success_count = 0
    
    for step_name, step_func in steps:
        try:
            if step_func():
                success_count += 1
            else:
                print(f"❌ {step_name} failed!")
        except Exception as e:
            print(f"❌ {step_name} failed with error: {e}")
    
    print(f"\n🎉 Setup Complete!")
    print(f"✅ {success_count}/{len(steps)} steps successful")
    
    if success_count == len(steps):
        print(f"\n🎯 Render Database is ready for testing!")
        print(f"🔑 Login credentials: admin / admin123")
        print(f"📋 Chart of Accounts: 24 accounts created")
        print(f"🏢 Company: RNR Pawn Shop (ID: 1)")
        print(f"📍 Areas: 5 locations created")
        print(f"🏦 Banks: 3 banks created")
        print(f"💎 Jewellery Types: 4 types created")
    else:
        print(f"\n⚠️  Some setup steps failed. Check errors above.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Complete Render Database Setup
Creates all tables, schema, and master data for fresh Render PostgreSQL database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import Base, engine, get_db
from src.core.models import *
from sqlalchemy.orm import Session
import bcrypt
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

def setup_chart_of_accounts():
    """Setup complete Chart of Accounts"""
    print("\n📊 Setting up Chart of Accounts...")
    
    accounts = [
        # Assets (1000-1999)
        {'account_code': '1001', 'account_name': 'Cash in Hand', 'account_type': 'Asset', 'company_id': 1},
        {'account_code': '1002', 'account_name': 'Bank Account', 'account_type': 'Asset', 'company_id': 1},
        {'account_id': 3, 'account_code': '1003', 'account_name': 'Pledges Receivable', 'account_type': 'Asset', 'parent_id': None},
        {'account_id': 4, 'account_code': '1004', 'account_name': 'Interest Receivable', 'account_type': 'Asset', 'parent_id': None},
        {'account_id': 5, 'account_code': '1005', 'account_name': 'Auction Inventory', 'account_type': 'Asset', 'parent_id': None},
        
        # Liabilities (2000-2999)
        {'account_id': 6, 'account_code': '2001', 'account_name': 'Accounts Payable', 'account_type': 'Liability', 'parent_id': None},
        {'account_id': 7, 'account_code': '2002', 'account_name': 'Customer Deposits', 'account_type': 'Liability', 'parent_id': None},
        {'account_id': 8, 'account_code': '2003', 'account_name': 'Tax Payable', 'account_type': 'Liability', 'parent_id': None},
        
        # Equity (3000-3999)
        {'account_id': 9, 'account_code': '3001', 'account_name': 'Owner Equity', 'account_type': 'Equity', 'parent_id': None},
        {'account_id': 10, 'account_code': '3002', 'account_name': 'Retained Earnings', 'account_type': 'Equity', 'parent_id': None},
        
        # Income (4000-4999)
        {'account_id': 11, 'account_code': '4001', 'account_name': 'Pledge Interest Income', 'account_type': 'Income', 'parent_id': None},
        {'account_id': 12, 'account_code': '4002', 'account_name': 'Auction Income', 'account_type': 'Income', 'parent_id': None},
        {'account_id': 13, 'account_code': '4003', 'account_name': 'Service Charges Income', 'account_type': 'Income', 'parent_id': None},
        {'account_id': 14, 'account_code': '4004', 'account_name': 'Penalty Income', 'account_type': 'Income', 'parent_id': None},
        {'account_id': 15, 'account_code': '4005', 'account_name': 'Other Income', 'account_type': 'Income', 'parent_id': None},
        
        # Expenses (5000-5999)
        {'account_id': 16, 'account_code': '5001', 'account_name': 'Staff Salaries', 'account_type': 'Expense', 'parent_id': None},
        {'account_id': 17, 'account_code': '5002', 'account_name': 'Rent Expense', 'account_type': 'Expense', 'parent_id': None},
        {'account_id': 18, 'account_code': '5003', 'account_name': 'Utility Bills', 'account_type': 'Expense', 'parent_id': None},
        {'account_id': 19, 'account_code': '5004', 'account_name': 'Office Supplies', 'account_type': 'Expense', 'parent_id': None},
        {'account_id': 20, 'account_code': '5005', 'account_name': 'Transportation', 'account_type': 'Expense', 'parent_id': None},
        {'account_id': 21, 'account_code': '5006', 'account_name': 'Marketing Expense', 'account_type': 'Expense', 'parent_id': None},
        {'account_id': 22, 'account_code': '5007', 'account_name': 'Legal & Professional', 'account_type': 'Expense', 'parent_id': None},
        {'account_id': 23, 'account_code': '5008', 'account_name': 'Discount Expense', 'account_type': 'Expense', 'parent_id': None},
        
        # Customer Accounts (6000-6999)
        {'account_id': 24, 'account_code': '6001', 'account_name': 'Customer Accounts', 'account_type': 'Asset', 'parent_id': None},
    ]
    
    try:
        db = next(get_db())
        
        for acc_data in accounts:
            # Check if account exists
            existing = db.query(MasterAccount).filter_by(account_code=acc_data['account_code']).first()
            if not existing:
                account = MasterAccount(**acc_data)
                db.add(account)
        
        db.commit()
        print(f"✅ Chart of Accounts setup complete - {len(accounts)} accounts")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up COA: {e}")
        return False

def setup_companies():
    """Setup company master data"""
    print("\n🏢 Setting up Companies...")
    
    companies = [
        {
            'company_id': 1,
            'company_name': 'RNR Pawn Shop',
            'address': '123 Main Street, Chennai, Tamil Nadu',
            'phone': '+91-9876543210',
            'email': 'info@rnrpawn.com',
            'gst_no': '33AAAAA0000A1Z5',
            'pan_no': 'AAAAA0000A'
        }
    ]
    
    try:
        db = next(get_db())
        
        for comp_data in companies:
            existing = db.query(Company).filter_by(company_id=comp_data['company_id']).first()
            if not existing:
                company = Company(**comp_data)
                db.add(company)
        
        db.commit()
        print(f"✅ Companies setup complete - {len(companies)} companies")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up companies: {e}")
        return False

def setup_users():
    """Setup user accounts"""
    print("\n👤 Setting up Users...")
    
    # Hash password for admin user
    password = "admin123"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    users = [
        {
            'user_id': 1,
            'username': 'admin',
            'email': 'admin@rnrpawn.com',
            'full_name': 'System Administrator',
            'hashed_password': hashed_password.decode('utf-8'),
            'is_active': True,
            'role': 'admin'
        }
    ]
    
    try:
        db = next(get_db())
        
        for user_data in users:
            existing = db.query(User).filter_by(username=user_data['username']).first()
            if not existing:
                user = User(**user_data)
                db.add(user)
        
        db.commit()
        print(f"✅ Users setup complete - {len(users)} users")
        print("   Default login: admin / admin123")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up users: {e}")
        return False

def setup_areas():
    """Setup areas/locations"""
    print("\n📍 Setting up Areas...")
    
    areas = [
        {'area_id': 1, 'area_name': 'T. Nagar', 'city': 'Chennai', 'state': 'Tamil Nadu', 'pincode': '600017'},
        {'area_id': 2, 'area_name': 'Anna Nagar', 'city': 'Chennai', 'state': 'Tamil Nadu', 'pincode': '600040'},
        {'area_id': 3, 'area_name': 'Velachery', 'city': 'Chennai', 'state': 'Tamil Nadu', 'pincode': '600042'},
        {'area_id': 4, 'area_name': 'Adyar', 'city': 'Chennai', 'state': 'Tamil Nadu', 'pincode': '600020'},
        {'area_id': 5, 'area_name': 'Mylapore', 'city': 'Chennai', 'state': 'Tamil Nadu', 'pincode': '600004'},
    ]
    
    try:
        db = next(get_db())
        
        for area_data in areas:
            existing = db.query(Area).filter_by(area_id=area_data['area_id']).first()
            if not existing:
                area = Area(**area_data)
                db.add(area)
        
        db.commit()
        print(f"✅ Areas setup complete - {len(areas)} areas")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up areas: {e}")
        return False

def setup_banks():
    """Setup bank master data"""
    print("\n🏦 Setting up Banks...")
    
    banks = [
        {'bank_id': 1, 'bank_name': 'State Bank of India', 'branch': 'T.Nagar Branch', 'ifsc': 'SBIN0001234'},
        {'bank_id': 2, 'bank_name': 'HDFC Bank', 'branch': 'Anna Nagar Branch', 'ifsc': 'HDFC0001235'},
        {'bank_id': 3, 'bank_name': 'ICICI Bank', 'branch': 'Velachery Branch', 'ifsc': 'ICIC0001236'},
    ]
    
    try:
        db = next(get_db())
        
        for bank_data in banks:
            existing = db.query(Bank).filter_by(bank_id=bank_data['bank_id']).first()
            if not existing:
                bank = Bank(**bank_data)
                db.add(bank)
        
        db.commit()
        print(f"✅ Banks setup complete - {len(banks)} banks")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up banks: {e}")
        return False

def verify_setup():
    """Verify the database setup"""
    print("\n🔍 Verifying Database Setup...")
    
    try:
        db = next(get_db())
        
        # Count records in each table
        tables = {
            'Accounts': db.query(MasterAccount).count(),
            'Companies': db.query(Company).count(),
            'Users': db.query(User).count(),
            'Areas': db.query(Area).count(),
            'Banks': db.query(Bank).count(),
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
        ("Setting up Chart of Accounts", setup_chart_of_accounts),
        ("Setting up Companies", setup_companies),
        ("Setting up Users", setup_users),
        ("Setting up Areas", setup_areas),
        ("Setting up Banks", setup_banks),
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
        print(f"\n🎯 Database is ready for testing!")
        print(f"🔑 Login credentials: admin / admin123")
        print(f"📋 Chart of Accounts: 24 accounts created")
        print(f"🏢 Company: RNR Pawn Shop")
    else:
        print(f"\n⚠️  Some setup steps failed. Check errors above.")

if __name__ == "__main__":
    main()
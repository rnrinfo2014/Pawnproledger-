#!/usr/bin/env python3
"""
Create admin user for testing the pledge accounting system
"""

from database import SessionLocal, Base, engine
from models import User, Company
from auth import get_password_hash

def create_admin_user():
    """Create admin user and company for testing"""
    db = SessionLocal()
    
    try:
        print("🏢 Creating test company...")
        # Create company first
        company = Company(
            name="Test Pawn Shop",
            address="123 Test Street",
            city="Test City",
            phone_number="+91-1234567890",
            license_no="22AAAAA0000A1Z5",
            status="active"
        )
        db.add(company)
        db.flush()  # Get company ID
        
        print("👤 Creating admin user...")
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@testpawnshop.com",
            password_hash=get_password_hash("admin123"),
            role="admin",
            company_id=company.id
        )
        db.add(admin_user)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   Company ID: {company.id}")
        print(f"   User ID: {admin_user.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creating Admin User for PawnSoft...")
    print("=" * 50)
    
    if create_admin_user():
        print("\n🎉 Setup complete! You can now login with:")
        print("   Username: admin")
        print("   Password: admin123")
    else:
        print("\n❌ Setup failed!")
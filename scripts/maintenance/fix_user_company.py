#!/usr/bin/env python3
"""
Update admin user to company 1 or create new user for company 1
"""

from database import SessionLocal
from models import User as UserModel

def fix_user_company():
    """Update admin user to company 1"""
    db = SessionLocal()
    
    try:
        # Find the admin user
        admin_user = db.query(UserModel).filter(UserModel.username == "admin").first()
        
        if not admin_user:
            print("Admin user not found")
            return False
        
        print(f"Current admin user company: {admin_user.company_id}")
        
        # Update to company 1
        admin_user.company_id = 1
        db.commit()
        
        print(f"Updated admin user to company 1")
        print("Now admin can access pledges and create payments in company 1")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Fixing user company assignment...")
    if fix_user_company():
        print("✅ Admin user now belongs to company 1")
        print("You can now create payments for pledges")
    else:
        print("❌ Failed to update user company")
#!/usr/bin/env python3
"""
Fix user password hash in Render database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import get_db
from src.core.models import User
from src.auth.auth import get_password_hash
from sqlalchemy.orm import Session

def fix_admin_password():
    """Fix admin user password hash"""
    print("🔧 Fixing admin user password hash...")
    
    try:
        db = next(get_db())
        
        # Find admin user
        admin_user = db.query(User).filter_by(username='admin').first()
        
        if admin_user:
            # Generate correct password hash
            correct_hash = get_password_hash("admin123")
            
            # Update password hash
            admin_user.password_hash = correct_hash
            db.commit()
            
            print("✅ Admin password hash fixed successfully!")
            print("🔑 Login: admin / admin123")
        else:
            print("❌ Admin user not found!")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing password: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

if __name__ == "__main__":
    fix_admin_password()
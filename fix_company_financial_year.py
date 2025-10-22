#!/usr/bin/env python3
"""
Fix company financial year dates
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import get_db
from src.core.models import Company
from sqlalchemy.orm import Session
from datetime import date

def fix_company_financial_year():
    """Fix company financial year dates"""
    print("🔧 Fixing company financial year dates...")
    
    try:
        db = next(get_db())
        
        # Find company
        company = db.query(Company).filter_by(id=1).first()
        
        if company:
            # Set standard financial year (April 1 to March 31)
            company.financial_year_start = date(2025, 4, 1)
            company.financial_year_end = date(2026, 3, 31)
            
            db.commit()
            
            print("✅ Company financial year dates fixed successfully!")
            print(f"   Financial Year Start: {company.financial_year_start}")
            print(f"   Financial Year End: {company.financial_year_end}")
        else:
            print("❌ Company not found!")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing financial year: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

if __name__ == "__main__":
    fix_company_financial_year()
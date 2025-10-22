from database import engine, Base, SessionLocal
from models import Company, User, MasterAccount, Area, GoldSilverRate, JewellDesign, JewellCondition, Scheme, Customer, Item, JewellType, JewellRate
from datetime import date
from auth import get_password_hash
from sqlalchemy import text
import sys


def create_tables_and_data():
    """Create tables and insert default data"""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Add new columns if not exist
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS city VARCHAR;"))
        conn.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS phone_number VARCHAR;"))
        conn.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS logo VARCHAR;"))
        conn.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS license_no VARCHAR;"))
        conn.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'active';"))
        conn.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS city VARCHAR;"))
        conn.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS area_id INTEGER REFERENCES areas(id);"))
        conn.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS acc_code VARCHAR;"))
        conn.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS id_proof_type VARCHAR;"))
        conn.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS id_image VARCHAR;"))
        conn.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'active';"))
        conn.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id);"))
        # Add jewell_type_id to schemes table
        conn.execute(text("ALTER TABLE schemes ADD COLUMN IF NOT EXISTS jewell_type_id INTEGER REFERENCES jewell_types(id);"))
        conn.commit()

    # Insert default data
    db = SessionLocal()
    try:
        # Check if default company exists
        existing_company = db.query(Company).filter(Company.name == "Default Company").first()
        
        if not existing_company:
            # Create default company
            company = Company(
                name="Default Company",
                address="123 Main St",
                city="Default City",
                phone_number="123-456-7890",
                logo="default_logo.png",
                license_no="LIC123456",
                status="active"
            )
            db.add(company)
            db.commit()
            print("Default company created.")
            
            # Check if admin user exists
            existing_admin = db.query(User).filter(User.username == "admin").first()
            if not existing_admin:
                admin = User(
                    username="admin",
                    email="admin@example.com",
                    password_hash=get_password_hash("admin"),  # Hashed password
                    role="admin",
                    company_id=company.id
                )
                db.add(admin)
                db.commit()
                print("Admin user created.")
                
            # Create default master accounts
            master_accounts = [
                MasterAccount(account_name="Assets", account_code="1000", account_type="Asset", group_name="Assets", company_id=company.id),
                MasterAccount(account_name="Liabilities", account_code="2000", account_type="Liability", group_name="Liabilities", company_id=company.id),
                MasterAccount(account_name="Equity", account_code="3000", account_type="Equity", group_name="Equity", company_id=company.id),
                MasterAccount(account_name="Income", account_code="4000", account_type="Income", group_name="Income", company_id=company.id),
                MasterAccount(account_name="Expenses", account_code="5000", account_type="Expense", group_name="Expenses", company_id=company.id)
            ]
            
            for acc in master_accounts:
                db.add(acc)
            db.commit()
            print("Default master accounts created.")
            
            # Create default areas
            areas = [
                Area(name="Downtown", status="active", company_id=company.id),
                Area(name="Uptown", status="active", company_id=company.id),
            ]
            for area in areas:
                db.add(area)
            db.commit()
            print("Default areas created.")
            
            # Create default gold silver rates
            admin_user = db.query(User).filter(User.username == "admin").first()
            if admin_user:
                rates = [
                    GoldSilverRate(date=date.today(), gold_rate_per_gram=5000.0, silver_rate_per_gram=70.0, company_id=company.id, created_by=admin_user.id),
                ]
                for rate in rates:
                    db.add(rate)
                db.commit()
                print("Default gold silver rates created.")
            
            # Create default jewell designs
            jewell_designs = [
                JewellDesign(design_name="Gold", status="active"),
                JewellDesign(design_name="Silver", status="active"),
                JewellDesign(design_name="Diamond", status="active"),
            ]
            for jd in jewell_designs:
                db.add(jd)
            db.commit()
            print("Default jewell designs created.")
            
            # Create default jewell conditions
            jewell_conditions = [
                JewellCondition(condition="New", status="active"),
                JewellCondition(condition="Used", status="active"),
                JewellCondition(condition="Damaged", status="active"),
            ]
            for jc in jewell_conditions:
                db.add(jc)
            db.commit()
            print("Default jewell conditions created.")

            # Insert default jewell types (Gold, Silver, Diamond)
            jewell_types = [
                JewellType(type_name="Gold", status="active"),
                JewellType(type_name="Silver", status="active"),
                JewellType(type_name="Diamond", status="active"),
            ]
            for jt in jewell_types:
                db.add(jt)
            db.commit()
            print("Default jewell types created.")

            # Insert a rate for Gold (you can add more as needed)
            gold_type = db.query(JewellType).filter_by(type_name="Gold").first()
            silver_type = db.query(JewellType).filter_by(type_name="Silver").first()
            diamond_type = db.query(JewellType).filter_by(type_name="Diamond").first()
            
            admin_user = db.query(User).filter(User.username == "admin").first()
            if gold_type and admin_user:
                rate = JewellRate(date=date.today(), jewell_type_id=gold_type.id, rate=5000.0, created_by=admin_user.id)
                db.add(rate)
                db.commit()
                print("Default jewell rate created.")
            
            # Update existing schemes with jewell_type_id based on jewell_category
            from models import Scheme
            existing_schemes = db.query(Scheme).filter(Scheme.jewell_type_id == None).all()
            if existing_schemes:
                for scheme in existing_schemes:
                    if scheme.jewell_category.lower() == "gold" and gold_type:
                        scheme.jewell_type_id = gold_type.id
                    elif scheme.jewell_category.lower() == "silver" and silver_type:
                        scheme.jewell_type_id = silver_type.id
                    elif scheme.jewell_category.lower() == "diamond" and diamond_type:
                        scheme.jewell_type_id = diamond_type.id
                
                db.commit()
                print(f"Updated {len(existing_schemes)} existing schemes with JewellType relationships.")
            
            # Create default schemes with JewellType relationships
            existing_gold_scheme = db.query(Scheme).filter(Scheme.scheme_name == "Gold Pawn Scheme").first()
            existing_silver_scheme = db.query(Scheme).filter(Scheme.scheme_name == "Silver Pawn Scheme").first()
            
            schemes_to_create = []
            if not existing_gold_scheme:
                schemes_to_create.append(Scheme(jewell_category="Gold", jewell_type_id=gold_type.id if gold_type else None, scheme_name="Gold Pawn Scheme", prefix="GP", interest_rate_monthly=2.5, duration=12, loan_allowed_percent=80.0, slippage_percent=5.0, acc_code="Sch-0001", company_id=company.id))
            if not existing_silver_scheme:
                schemes_to_create.append(Scheme(jewell_category="Silver", jewell_type_id=silver_type.id if silver_type else None, scheme_name="Silver Pawn Scheme", prefix="SP", interest_rate_monthly=3.0, duration=6, loan_allowed_percent=70.0, slippage_percent=10.0, acc_code="Sch-0002", company_id=company.id))
            
            for scheme in schemes_to_create:
                db.add(scheme)
            if schemes_to_create:
                db.commit()
                print("Default schemes created with JewellType relationships.")
            
        else:
            print("Default data already exists.")
            # Update admin password to hashed
            existing_admin = db.query(User).filter(User.username == "admin").first()
            if existing_admin and existing_admin.password_hash != get_password_hash("admin"):  # type: ignore
                existing_admin.password_hash = get_password_hash("admin")  # type: ignore
                db.commit()
                print("Admin password updated.")
            
            # Update company with new fields if NULL
            existing_company = db.query(Company).filter(Company.name == "Default Company").first()
            if existing_company:
                if existing_company.city is None:
                    existing_company.city = "Default City"  # type: ignore
                if existing_company.phone_number is None:
                    existing_company.phone_number = "123-456-7890"  # type: ignore
                if existing_company.logo is None:
                    existing_company.logo = "default_logo.png"  # type: ignore
                if existing_company.license_no is None:
                    existing_company.license_no = "LIC123456"  # type: ignore
                if existing_company.status is None:
                    existing_company.status = "active"  # type: ignore
                db.commit()
                print("Company updated with new fields.")
                
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating tables and inserting default data...")
    create_tables_and_data()
    print("✅ Tables created and default data inserted!")

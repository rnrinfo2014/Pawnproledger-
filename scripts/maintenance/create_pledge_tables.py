from database import engine
from models import Base

def create_pledge_tables():
    """Create the pledge and pledge_items tables"""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine, tables=[
            Base.metadata.tables['pledges'],
            Base.metadata.tables['pledge_items']
        ])
        print("✅ Pledge tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating pledge tables: {e}")

if __name__ == "__main__":
    create_pledge_tables()

#!/usr/bin/env python3
"""
Database connection test script for Render PostgreSQL
Run this script to test your database connection before deploying
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import settings

def test_database_connection():
    """Test database connection with current configuration"""
    print("Testing database connection...")
    print(f"Environment: {settings.environment}")
    
    # Mask password in URL for logging
    masked_url = settings.database_url
    if "@" in masked_url:
        parts = masked_url.split("@")
        user_pass = parts[0].split("://")[1]
        if ":" in user_pass:
            user, password = user_pass.split(":", 1)
            masked_url = masked_url.replace(f":{password}@", ":****@")
    
    print(f"Database URL: {masked_url}")
    
    try:
        # Create engine with SSL settings if needed
        engine_kwargs = {}
        if "render" in settings.database_url.lower() or settings.environment == "production":
            engine_kwargs["connect_args"] = {"sslmode": "require"}
            print("Using SSL connection for production/Render database")
        
        engine = create_engine(settings.database_url, **engine_kwargs)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version_row = result.fetchone()
            if version_row:
                version = version_row[0]
                print(f"✅ Database connection successful!")
                print(f"PostgreSQL version: {version}")
            
            # Test basic query
            result = connection.execute(text("SELECT 1 as test"))
            test_row = result.fetchone()
            if test_row:
                test_result = test_row[0]
                print(f"✅ Test query successful: {test_result}")
            
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Database connection failed:")
        print(f"Error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error:")
        print(f"Error: {str(e)}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("PawnSoft Database Connection Test")
    print("=" * 50)
    
    # Check if DATABASE_URL is set
    if not settings.database_url:
        print("❌ DATABASE_URL is not set!")
        print("Please set DATABASE_URL environment variable or update config.py")
        sys.exit(1)
    
    # Test connection
    success = test_database_connection()
    
    print("=" * 50)
    if success:
        print("✅ All tests passed! Database is ready.")
        sys.exit(0)
    else:
        print("❌ Tests failed! Check your database configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()
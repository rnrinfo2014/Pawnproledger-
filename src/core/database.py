# type: ignore
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from typing import Generator
import os
from dotenv import load_dotenv

# Fix import path for Render deployment
try:
    from src.core.config import settings
except ImportError:
    # Fallback for Render deployment structure
    from core.config import settings

load_dotenv()

# Get database URL from settings
DATABASE_URL = settings.database_url

# For Render PostgreSQL, ensure SSL is properly configured
engine_kwargs = {}
if "render" in DATABASE_URL.lower() or settings.environment == "production":
    # Render PostgreSQL requires SSL
    engine_kwargs["connect_args"] = {"sslmode": "require"}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get database session
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

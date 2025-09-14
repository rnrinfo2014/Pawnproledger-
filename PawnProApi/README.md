# PawnProApi

Backend API for PawnPro using FastAPI and PostgreSQL.

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set up PostgreSQL database and update `.env` with DATABASE_URL.
3. Run `python create_tables.py` to create tables.
4. Start the server: `uvicorn main:app --reload`

## API Endpoints

- GET / : Welcome message

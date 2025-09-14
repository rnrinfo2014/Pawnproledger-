# PawnSoft - Pawn Shop Management API

A comprehensive FastAPI-based backend system for managing pawn shop operations including customers, pledges, schemes, and inventory management.

## Features

- **Customer Management**: Create, update, search customers with phone validation
- **Pledge System**: Complete pledge lifecycle management with interest calculations
- **Scheme Management**: Flexible scheme configurations with jewell type bindings
- **Search APIs**: Advanced search for customers and jewell designs
- **File Upload**: Support for customer ID proofs and company logos
- **Authentication**: JWT-based secure API access

## API Endpoints

### Authentication
- `POST /token` - Get access token
- `POST /refresh` - Refresh access token

### Customer Management
- `GET /customers/` - List all customers
- `POST /customers/` - Create new customer
- `GET /customers/{id}` - Get customer details
- `PUT /customers/{id}` - Update customer
- `DELETE /customers/{id}` - Delete customer
- `GET /customers/search` - Search customers by name or phone

### Pledge Management
- `GET /pledges/` - List all pledges
- `POST /pledges/` - Create new pledge
- `GET /pledges/{id}` - Get pledge details
- `PUT /pledges/{id}` - Update pledge
- `DELETE /pledges/{id}` - Delete pledge

### Scheme Management
- `GET /schemes/` - List all schemes
- `POST /schemes/` - Create new scheme
- `GET /schemes/{id}` - Get scheme details
- `PUT /schemes/{id}` - Update scheme
- `DELETE /schemes/{id}` - Delete scheme

### Jewell Type & Rate Management
- `GET /jewell-types/` - List all jewell types
- `POST /jewell-types/` - Create new jewell type
- `GET /jewell-rates/` - List all jewell rates
- `POST /jewell-rates/` - Create new jewell rate

### Search & Utility
- `GET /jewell-designs/search` - Search jewell designs
- `POST /upload-file/` - Upload files (ID proofs, logos)

## Setup and Installation

### Prerequisites
- Python 3.8+
- PostgreSQL or SQLite database

### Installation

1. Clone the repository:
```bash
git clone https://github.com/rnrinfo2014/Pawnproledger-.git
cd Pawnproledger-
```

2. Create virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
cd PawnProApi
pip install -r requirements.txt
```

4. Configure database:
```bash
# Update database URL in config.py or set environment variable
# Run database creation script
python create_tables.py
```

5. Start the API server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Project Structure

```
PawnProApi/
├── main.py              # FastAPI application entry point
├── models.py            # SQLAlchemy database models
├── database.py          # Database configuration
├── auth.py              # Authentication utilities
├── config.py            # Application configuration
├── create_tables.py     # Database initialization
├── requirements.txt     # Python dependencies
├── uploads/             # File upload directory
└── README.md            # API documentation
```

## Database Schema

- **Users**: User authentication and roles
- **Customers**: Customer information with phone validation
- **Pledges**: Pledge records with interest calculations
- **Schemes**: Scheme configurations
- **JewellType**: Jewellery type definitions
- **JewellRate**: Rate configurations for different jewellery types
- **JewellDesign**: Jewellery design catalog

## Frontend Development

This repository contains only the backend API. The frontend is developed separately using Google AI Studio.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is proprietary software for pawn shop management.

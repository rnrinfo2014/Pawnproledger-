# 🏛️ PawnSoft - Complete Pawn Shop Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)

A comprehensive, production-ready API system for pawn shop management with advanced accounting, security features, and business automation.

## 📋 Table of Contents
- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [Business Workflows](#-business-workflows)
- [Security Features](#-security-features)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

## ✨ Features

### 🔐 Authentication & Security
- JWT-based authentication with role-based access control
- Rate limiting and security headers middleware
- Password hashing with bcrypt
- Admin and user role separation
- CORS protection with configurable origins

### 💼 Business Management
- **Customer Management**: Complete customer profiles with KYC
- **Pledge Management**: Loan tracking with automated interest calculation
- **Inventory Management**: Gold/Silver ornament tracking
- **Payment Processing**: Multiple payment methods and tracking
- **Interest Calculation**: Automated monthly interest and penalty calculation

### 📊 Accounting System
- **Chart of Accounts (COA)**: Hierarchical account structure with 33+ pawn shop specific accounts
- **Double Entry Bookkeeping**: Complete ledger entries for all transactions
- **Daybook Reports**: Daily, weekly, monthly transaction summaries
- **Financial Reports**: Balance Sheet, P&L, Cash Flow statements
- **Automated Transactions**: System-generated entries for pledges, payments, auctions

### 📈 Business Intelligence
- Real-time dashboard with key metrics
- Monthly/yearly financial reports
- Customer analytics and payment tracking
- Inventory valuation reports
- Auction management and profit tracking

### 🔧 System Features
- Multi-company support
- Area-wise branch management
- Bank integration for payments
- File upload and document management
- Automated backup and restore
- Audit trails for all transactions

## 🏗️ System Architecture

```
PawnSoft/
├── PawnProApi/               # Main API application
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # SQLAlchemy database models
│   ├── database.py          # Database configuration
│   ├── auth.py              # Authentication logic
│   ├── config.py            # Application configuration
│   ├── coa_api.py           # Chart of Accounts API
│   ├── daybook_api.py       # Daily transaction reports
│   ├── security_middleware.py # Security middleware
│   └── uploads/             # File storage directory
└── docs/                    # Documentation files
```

### Core APIs
1. **Authentication API** - User login, registration, role management
2. **Company Management** - Multi-tenant company setup
3. **Customer API** - Customer profiles and KYC management
4. **Pledge API** - Loan creation, tracking, settlement
5. **Payment API** - Payment processing and tracking
6. **Inventory API** - Gold/Silver item management
7. **Chart of Accounts API** - Financial account management
8. **Daybook API** - Transaction reporting and analytics
9. **Bank API** - Bank account and transaction management

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Git

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/rnrinfo2014/Pawnproledger-.git
cd PawnSoft
```

2. **Set Up Virtual Environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install Dependencies**
```bash
cd PawnProApi
pip install -r requirements.txt
```

4. **Environment Configuration**
Create `.env` file in PawnProApi directory:
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/pawnsoft_db

# Security Configuration
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_TITLE=PawnSoft API
API_DESCRIPTION=Complete Pawn Shop Management System
API_VERSION=1.0.0

# Environment
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://rnrinfo.dev

# Security Features
ENABLE_SECURITY_HEADERS=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
```

5. **Database Setup**
```bash
# Create database
python create_tables.py

# Initialize Chart of Accounts
python -c "
from coa_api import initialize_pawn_shop_coa
from database import SessionLocal
db = SessionLocal()
initialize_pawn_shop_coa(db, company_id=1)
db.close()
"
```

6. **Run the Application**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

7. **Access the Application**
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Main Application: http://localhost:8000/

### First Time Setup

1. **Create Admin User**
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@pawnsoft.com",
    "password": "secure_password_123",
    "role": "admin"
  }'
```

2. **Get Access Token**
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=secure_password_123"
```

3. **Create Company**
```bash
curl -X POST "http://localhost:8000/companies" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Your Pawn Shop",
    "address": "123 Main Street",
    "phone": "+1-234-567-8900",
    "email": "info@yourpawnshop.com"
  }'
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /token` - Login and get access token
- `GET /users/me` - Get current user profile
- `POST /users` - Register new user (admin only)

### Business Endpoints
- `GET /companies` - List all companies
- `POST /pledges` - Create new pledge
- `GET /pledges/{id}` - Get pledge details
- `POST /pledge_payments` - Record payment
- `GET /customers` - List customers

### Accounting Endpoints
- `GET /api/v1/coa/accounts` - Get chart of accounts
- `POST /api/v1/coa/accounts` - Create new account
- `GET /api/v1/daybook/daily_summary` - Get daily transaction summary
- `GET /api/v1/daybook/date_range` - Get transactions for date range

### Complete API Reference
Visit `/docs` when running the server for interactive API documentation with request/response examples.

## 🗄️ Database Schema

### Core Tables
- **users** - System users with role-based access
- **companies** - Multi-tenant company information
- **customers** - Customer profiles and KYC data
- **pledges** - Loan/pledge master records
- **pledge_items** - Individual items in each pledge
- **pledge_payments** - Payment history and tracking
- **accounts_master** - Chart of accounts
- **voucher_master** - Transaction vouchers
- **ledger_entries** - Double-entry bookkeeping records

### Relationships
```sql
customers --< pledges --< pledge_items
pledges --< pledge_payments
voucher_master --< ledger_entries
accounts_master --< ledger_entries
companies --< customers
companies --< pledges
```

## 💼 Business Workflows

### Pledge Creation Workflow
1. Customer registration/verification
2. Item appraisal and documentation
3. Pledge amount calculation based on item value
4. Interest rate determination
5. Pledge agreement creation
6. Automatic accounting entries

### Payment Processing
1. Payment recording (cash/bank/digital)
2. Interest calculation and application
3. Outstanding balance update
4. Receipt generation
5. Automatic ledger entries

### Settlement Process
1. Full payment verification
2. Item release authorization
3. Final interest calculation
4. Settlement documentation
5. Account closure

### Auction Process
1. Overdue pledge identification
2. Item transfer to auction inventory
3. Auction sale recording
4. Profit/loss calculation
5. Customer account settlement

## 🔒 Security Features

### Authentication
- JWT tokens with configurable expiration
- Password hashing using bcrypt
- Role-based access control (Admin/User)

### API Security
- Rate limiting (configurable requests per time window)
- CORS protection with domain whitelisting
- Security headers middleware
- Request/response logging
- Input validation and sanitization

### Data Protection
- SQL injection prevention with parameterized queries
- XSS protection with input validation
- CSRF protection for state-changing operations
- Audit trails for all critical operations

### Production Security
- Environment-based configuration
- Secret management with environment variables
- Database connection pooling
- Error handling without information disclosure

## 🚀 Deployment

### Production Deployment on rnrinfo.dev

1. **SSL Certificate Setup**
```bash
# Using Certbot for Let's Encrypt
sudo certbot --nginx -d rnrinfo.dev -d api.rnrinfo.dev
```

2. **Nginx Configuration**
```nginx
server {
    listen 443 ssl;
    server_name api.rnrinfo.dev;
    
    ssl_certificate /etc/letsencrypt/live/rnrinfo.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/rnrinfo.dev/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Docker Deployment**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

4. **Environment Variables for Production**
```env
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@prod-db:5432/pawnsoft
CORS_ORIGINS=https://rnrinfo.dev,https://app.rnrinfo.dev
ENABLE_SECURITY_HEADERS=true
```

### Monitoring and Maintenance
- Health check endpoint: `/health`
- Log monitoring and alerting
- Database backup automation
- Performance monitoring
- Security vulnerability scanning

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

### Development Guidelines
- Follow PEP 8 coding standards
- Write comprehensive tests
- Update documentation for new features
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

- **Email**: support@rnrinfo.dev
- **Documentation**: Visit `/docs` when running the server
- **Issues**: GitHub Issues for bug reports and feature requests

---

## 🏆 Key Benefits

✅ **Complete Business Solution** - End-to-end pawn shop management
✅ **Production Ready** - Security, monitoring, and scalability built-in
✅ **Accounting Integration** - Double-entry bookkeeping with automated transactions
✅ **Multi-tenant Architecture** - Support for multiple branches/companies
✅ **Real-time Reporting** - Live dashboards and financial reports
✅ **Regulatory Compliance** - Audit trails and data protection

**Built with ❤️ for the pawn shop industry**
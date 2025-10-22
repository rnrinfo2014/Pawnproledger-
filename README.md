# 🏪 PawnSoft - Pawn Shop Management System

A comprehensive Pawn Shop Management System built with Python FastAPI and PostgreSQL, featuring complete accounting integration and multi-tenant support.

## ✨ Features

- 👥 **Customer Management** - Complete customer lifecycle with auto COA accounts
- 💎 **Pledge Management** - Gold/jewelry pledging with item tracking  
- 💰 **Payment Processing** - Full payment system with accounting integration
- 📊 **Accounting System** - Double-entry bookkeeping with Chart of Accounts
- 🏢 **Multi-Company Support** - Multi-tenant architecture with data isolation
- 🔐 **JWT Authentication** - Secure API access with role-based permissions
- 📡 **RESTful API** - Complete REST API with auto-generated documentation

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Database
```bash
# Copy and edit configuration
cp config/.env.example .env

# Set up database tables
python scripts/database/create_tables.py
```

### 3. Run Application
```bash
# Start the development server
uvicorn src.core.main:app --reload
```

### 4. Access Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Documentation**: [docs/README.md](docs/README.md)

## 📁 Project Structure

```
PawnSoft/
├── 📂 src/                    # Source code
│   ├── core/                  # Core application (main.py, models, config)
│   ├── auth/                  # Authentication & security
│   └── managers/              # Business logic managers
│
├── 📂 docs/                   # 📚 Complete documentation
│   ├── api/                   # API documentation & guides
│   ├── guides/                # User & developer guides
│   └── technical/             # Technical documentation
│
├── 📂 scripts/                # 🔧 Utility scripts
│   ├── database/              # Database setup & migrations
│   ├── setup/                 # Initial setup scripts
│   └── maintenance/           # Maintenance & debug scripts
│
├── 📂 tests/                  # 🧪 Test files
├── 📂 config/                 # ⚙️ Configuration files
├── requirements.txt           # 📦 Python dependencies
└── README.md                  # 📖 This file
```

## 📚 Documentation

### 🎯 For Beginners
- [📖 Beginner Guide](docs/guides/BEGINNER_GUIDE.md) - Start here if you're new
- [🏗️ Application Flow](docs/guides/PAWNSOFT_APPLICATION_FLOW_EXPLAINED.md) - How it works
- [💻 FastAPI Guide](docs/guides/FASTAPI_DETAILED_GUIDE.md) - Framework basics

### 👨‍💻 For Developers  
- [📁 Project Structure](docs/technical/PROJECT_FILE_STRUCTURE_WORKFLOW.md) - Code organization
- [🎯 Complete Example](docs/guides/COMPLETE_TRANSACTION_EXAMPLE.md) - End-to-end workflow
- [📡 API Documentation](docs/api/API_DOCUMENTATION.md) - Complete API reference

### 🔧 For System Admins
- [🚀 Deployment Guide](docs/technical/DEPLOYMENT_GUIDE.md) - Production deployment
- [🔒 Security Guide](docs/technical/SECURITY_GUIDE.md) - Security best practices
- [🗃️ Database Schema](docs/technical/DATABASE_SCHEMA.md) - Database structure

## 💡 Key Concepts

**🔄 Complete Workflow:**
1. **Customer Registration** → Auto COA account creation
2. **Pledge Creation** → Double-entry accounting entries  
3. **Payment Processing** → Automatic balance updates & accounting
4. **Settlement** → Complete transaction closure

**📊 Accounting Integration:**
- Automatic Chart of Accounts management
- Double-entry bookkeeping for all transactions
- Customer-specific account tracking (2001-XXX series)
- Complete audit trail with voucher system

## 🛠️ Development

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Git

### Setup Development Environment
```bash
# Clone repository
git clone <repository-url>
cd PawnSoft

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
python scripts/database/create_tables.py

# Run tests
python -m pytest tests/

# Start development server
uvicorn src.core.main:app --reload --host 0.0.0.0 --port 8000
```

## 🤝 Contributing

1. Follow the existing code structure in `src/`
2. Add tests for new features in `tests/`
3. Update documentation in `docs/`
4. Follow Python PEP 8 style guidelines

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

- 📚 **Documentation**: [docs/README.md](docs/README.md)
- 🔧 **Troubleshooting**: [docs/technical/TROUBLESHOOTING_GUIDE.md](docs/technical/TROUBLESHOOTING_GUIDE.md)
- 📡 **API Reference**: [docs/api/API_DOCUMENTATION.md](docs/api/API_DOCUMENTATION.md)

---

Built with ❤️ using Python FastAPI & PostgreSQL
# 🔒 Security & Authentication Guide

Comprehensive security implementation for PawnSoft Pawn Shop Management System

## 🛡️ Security Overview

PawnSoft implements multiple layers of security to protect sensitive financial and customer data:

1. **Authentication & Authorization**
2. **API Security**
3. **Data Protection**
4. **Infrastructure Security**
5. **Compliance & Audit**

---

## 🔐 Authentication System

### JWT-Based Authentication

PawnSoft uses JSON Web Tokens (JWT) for stateless authentication with the following specifications:

```python
# Token Configuration
SECRET_KEY = "your-super-secret-key-here"  # 256-bit minimum
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

### Password Security

**Hashing Algorithm**: Argon2 with PBKDF2 fallback
```python
# Enhanced password hashing configuration
pwd_context = CryptContext(
    schemes=["argon2", "pbkdf2_sha256"], 
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,        # 3 iterations
    argon2__parallelism=1       # 1 thread
)
```

**Password Requirements**:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character
- Cannot contain username or email

### Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Database
    
    Client->>API: POST /token (username, password)
    API->>Database: Verify user credentials
    Database-->>API: User data
    API->>API: Generate JWT token
    API-->>Client: JWT token
    
    Client->>API: API request with Bearer token
    API->>API: Validate JWT token
    API->>Database: Get current user data
    API-->>Client: API response
```

### Implementation Example

```python
# Login endpoint
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected endpoint
@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

---

## 🛡️ Role-Based Access Control (RBAC)

### User Roles

#### Admin Role
- **Permissions**:
  - Create/manage companies
  - Create/manage users
  - Access all company data
  - System configuration
  - View audit logs

#### User Role  
- **Permissions**:
  - Access assigned company data
  - Manage customers within company
  - Create/manage pledges
  - Process payments
  - Generate reports

### Authorization Implementation

```python
def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Usage in endpoints
@app.post("/companies")
async def create_company(
    company: CompanyCreate,
    current_user: User = Depends(get_current_admin_user)
):
    # Only admins can create companies
    pass
```

---

## 🔒 API Security

### Rate Limiting

**Configuration**:
- 100 requests per minute per IP address
- Configurable via environment variables
- Different limits for different endpoint categories

```python
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, time_window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, List[float]] = defaultdict(list)
```

### Security Headers

All API responses include security headers:

```python
# Security headers applied
response.headers["X-Content-Type-Options"] = "nosniff"
response.headers["X-Frame-Options"] = "DENY"  # Allow for docs
response.headers["X-XSS-Protection"] = "1; mode=block"
response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

# HSTS for production
if settings.environment == "production":
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
```

### CORS Configuration

**Development**:
```python
CORS_ORIGINS = ["*"]  # Permissive for development
```

**Production**:
```python
CORS_ORIGINS = [
    "https://rnrinfo.dev",
    "https://app.rnrinfo.dev",
    "https://admin.rnrinfo.dev"
]
```

### Input Validation

All inputs are validated using Pydantic models:

```python
class CustomerCreate(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=200)
    phone_number: str = Field(..., regex=r'^\+?[1-9]\d{1,14}$')
    email: Optional[EmailStr] = None
    
    @validator('customer_name')
    def validate_name(cls, v):
        if not v.replace(' ', '').isalpha():
            raise ValueError('Name must contain only letters and spaces')
        return v.title()
```

---

## 🔐 Data Protection

### Database Security

**Connection Security**:
```python
# SSL connection for production
DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require"

# Connection pooling with limits
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=300
)
```

**SQL Injection Prevention**:
- All queries use parameterized statements
- SQLAlchemy ORM provides automatic protection
- Input sanitization at API level

### File Upload Security

```python
class FileUploadSecurity:
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def validate_file(file: UploadFile):
        # Check file extension
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(400, "File type not allowed")
        
        # Check file size
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(400, "File too large")
        
        # Check MIME type
        if not file.content_type.startswith(('image/', 'application/pdf')):
            raise HTTPException(400, "Invalid content type")
```

### Data Encryption

**At Rest**:
- Database encryption at storage level
- Sensitive fields encrypted using Fernet
- File storage encryption

**In Transit**:
- HTTPS/TLS 1.3 for all communications
- API endpoint encryption
- Database connection encryption

```python
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

---

## 📊 Audit & Logging

### Security Logging

```python
class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request details
        security_logger.info({
            "event": "api_request",
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        response = await call_next(request)
        
        # Log response details
        process_time = time.time() - start_time
        security_logger.info({
            "event": "api_response",
            "status_code": response.status_code,
            "process_time": process_time,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return response
```

### Audit Trail

All critical operations are logged:

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))  # CREATE, UPDATE, DELETE
    table_name = Column(String(50))
    record_id = Column(Integer)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

def create_audit_log(db: Session, user_id: int, action: str, table_name: str, 
                    record_id: int, old_values: dict = None, new_values: dict = None):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=get_client_ip(),
        user_agent=get_user_agent()
    )
    db.add(audit_log)
    db.commit()
```

---

## 🏗️ Infrastructure Security

### Environment Configuration

```bash
# Security Environment Variables
SECRET_KEY=generate-256-bit-key-here
DATABASE_URL=postgresql://user:pass@host:5432/db
ENVIRONMENT=production

# Security Features
ENABLE_SECURITY_HEADERS=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# CORS Configuration
CORS_ORIGINS=https://rnrinfo.dev,https://app.rnrinfo.dev

# SSL Configuration
SSL_CERT_PATH=/etc/ssl/certs/rnrinfo.dev.crt
SSL_KEY_PATH=/etc/ssl/private/rnrinfo.dev.key
```

### Production Deployment Security

**Nginx Configuration**:
```nginx
server {
    listen 443 ssl http2;
    server_name api.rnrinfo.dev;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/rnrinfo.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/rnrinfo.dev/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🚨 Incident Response

### Security Monitoring

**Alerts Configured For**:
- Failed login attempts (>5 in 5 minutes)
- Rate limit violations
- Unusual API access patterns
- Database connection failures
- File upload anomalies

**Monitoring Tools**:
- Application logs analysis
- Database query monitoring
- Network traffic analysis
- File integrity monitoring

### Incident Response Plan

1. **Detection**: Automated monitoring alerts
2. **Analysis**: Log analysis and threat assessment
3. **Containment**: Block malicious IPs, disable compromised accounts
4. **Eradication**: Fix vulnerabilities, update security measures
5. **Recovery**: Restore services, verify system integrity
6. **Lessons Learned**: Update security procedures

---

## ✅ Security Checklist

### Development Security
- [ ] All passwords hashed with Argon2
- [ ] JWT tokens properly configured
- [ ] Input validation on all endpoints
- [ ] SQL injection protection enabled
- [ ] File upload security implemented
- [ ] Rate limiting configured
- [ ] Security headers enabled
- [ ] CORS properly configured

### Production Security
- [ ] HTTPS/TLS 1.3 enabled
- [ ] Security headers enforced
- [ ] Database connections encrypted
- [ ] Regular security updates
- [ ] Firewall configured
- [ ] Intrusion detection enabled
- [ ] Backup encryption enabled
- [ ] Audit logging active

### Compliance Requirements
- [ ] Data retention policies
- [ ] User consent management
- [ ] Data encryption standards
- [ ] Access control documentation
- [ ] Incident response procedures
- [ ] Regular security assessments
- [ ] Vendor security reviews
- [ ] Staff security training

---

## 🛠️ Security Testing

### Automated Security Tests

```python
def test_authentication():
    # Test invalid credentials
    response = client.post("/token", data={"username": "invalid", "password": "wrong"})
    assert response.status_code == 401
    
    # Test valid credentials
    response = client.post("/token", data={"username": "admin", "password": "correct"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_authorization():
    # Test admin-only endpoint with user token
    response = client.post("/companies", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403
    
    # Test with admin token
    response = client.post("/companies", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200

def test_rate_limiting():
    # Test rate limit enforcement
    for i in range(101):
        response = client.get("/health")
        if i < 100:
            assert response.status_code == 200
        else:
            assert response.status_code == 429
```

### Security Scanning

**Tools Used**:
- OWASP ZAP for web application scanning
- Bandit for Python security issues
- SQLMap for SQL injection testing
- Nmap for network security scanning

**Regular Scans**:
- Weekly automated vulnerability scans
- Monthly penetration testing
- Quarterly third-party security audits

---

## 📞 Security Support

- **Security Issues**: security@rnrinfo.dev
- **Emergency Contact**: +1-xxx-xxx-xxxx
- **Bug Bounty Program**: security.rnrinfo.dev/bounty

---

**Last Updated**: January 15, 2025
**Security Version**: 1.0.0
**Compliance**: OWASP Top 10, NIST Cybersecurity Framework
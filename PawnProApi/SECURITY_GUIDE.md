# 🔒 PawnSoft API Security Guide

## 🚨 CRITICAL: Security Setup for Production

### 1. **Domain Configuration**

```bash
# For Windows PowerShell
.\setup-domain.ps1 yourdomain.com

# For Linux/Mac
./setup-domain.sh yourdomain.com
```

### 2. **Generate Strong Secret Keys**

```bash
# Generate a strong JWT secret key (256-bit)
openssl rand -hex 32

# Or use PowerShell (Windows)
-join ((1..64) | ForEach {'{0:X}' -f (Get-Random -Max 16)})
```

### 2. **Environment Configuration**

1. Copy `.env.template` to `.env`
2. **IMMEDIATELY** change these critical values:
   ```env
   JWT_SECRET_KEY=your-generated-256-bit-key-here
   SECRET_KEY=another-strong-secret-key
   CORS_ORIGINS=https://yourdomain.com
   ENVIRONMENT=production
   ```

### 3. **HTTPS Setup (REQUIRED for Production)**

```bash
# Option 1: Using Certbot (Let's Encrypt)
certbot certonly --standalone -d yourdomain.com

# Option 2: Using your SSL certificate
# Update .env file:
USE_HTTPS=true
SSL_CERT_FILE=/path/to/certificate.pem
SSL_KEY_FILE=/path/to/private_key.pem
```

### 4. **Production Deployment Command**

```bash
# Install security dependencies
pip install -r requirements.txt

# Run with HTTPS
uvicorn main:app --host 0.0.0.0 --port 443 --ssl-keyfile private_key.pem --ssl-certfile certificate.pem

# Or let the config handle it
python -m uvicorn main:app --host 0.0.0.0 --port 443
```

## 🛡️ Security Features Implemented

### ✅ **Authentication & Authorization**
- JWT token-based authentication
- Role-based access control (admin/user)
- Enhanced password hashing with Argon2
- Password strength validation

### ✅ **Rate Limiting**
- Configurable request limits per IP
- Prevents brute force attacks
- Automatic IP blocking for abuse

### ✅ **Security Headers**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HTTPS only)
- Content Security Policy (CSP)

### ✅ **CORS Protection**
- Restricted to specific domains in production
- No wildcard origins in production

### ✅ **Input Validation**
- File upload restrictions
- Request size limits
- Content type validation

### ✅ **Security Logging**
- Authentication attempts logging
- Failed login monitoring
- Sensitive endpoint access logging

## ⚠️ Security Checklist

### **Before Going Live:**

- [ ] **Change all default passwords and secret keys**
- [ ] **Set ENVIRONMENT=production in .env**
- [ ] **Configure CORS_ORIGINS to your actual domains**
- [ ] **Enable HTTPS with valid SSL certificate**
- [ ] **Set up monitoring and log analysis**
- [ ] **Configure firewall rules**
- [ ] **Set up database backup encryption**
- [ ] **Review and update rate limits**
- [ ] **Test all security features**

### **Regular Maintenance:**

- [ ] **Rotate JWT secret keys monthly**
- [ ] **Monitor security logs daily**
- [ ] **Update dependencies regularly**
- [ ] **Review access logs weekly**
- [ ] **Backup database with encryption**

## 🚨 Security Incidents Response

### **If You Suspect a Security Breach:**

1. **Immediately rotate all secret keys**
2. **Check security logs for suspicious activity**
3. **Review recent API access patterns**
4. **Update all user passwords**
5. **Consider temporarily blocking suspicious IPs**

### **Log Locations:**
- Security events: `security.log`
- API access: Check middleware logs
- Authentication: JWT token validation logs

## 📊 Monitoring Endpoints

- **Health Check**: `GET /health` (no auth required)
- **API Documentation**: `/docs` (disabled in production)
- **Metrics**: Monitor response times via `X-Process-Time` header

## 🔧 Advanced Security Configuration

### **Custom Rate Limits:**
```env
# For high-traffic applications
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_PERIOD=3600

# For APIs with sensitive data
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_PERIOD=3600
```

### **Strong Password Policy:**
```env
MIN_PASSWORD_LENGTH=14
REQUIRE_SPECIAL_CHARS=true
```

### **Database Security:**
- Use SSL connections: `?sslmode=require` in DATABASE_URL
- Rotate database passwords regularly
- Limit database user permissions

## 🆘 Support

For security questions or incidents:
1. Check logs first: `/var/log/pawnsoft/`
2. Review this documentation
3. Test in development environment first

**Remember: Security is an ongoing process, not a one-time setup!**
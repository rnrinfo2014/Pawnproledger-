# 🚀 Production Deployment Guide

Complete deployment instructions for PawnSoft on rnrinfo.dev with SSL and production optimizations

## 📋 Deployment Overview

This guide covers deploying PawnSoft to production on your rnrinfo.dev domain with:
- Ubuntu 20.04+ server
- Nginx reverse proxy
- SSL certificates (Let's Encrypt)
- PostgreSQL database
- Systemd service management
- Docker containerization (optional)

---

## 🖥️ Server Requirements

### Minimum System Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 50GB SSD
- **OS**: Ubuntu 20.04+
- **Network**: Public IP with domain pointing to server

### Recommended Production Requirements
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 100GB SSD
- **Backup**: Regular automated backups
- **Monitoring**: Application and infrastructure monitoring

---

## 🔧 Server Setup

### 1. Initial Server Configuration

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y software-properties-common curl wget git unzip

# Create application user
sudo adduser pawnsoft
sudo usermod -aG sudo pawnsoft

# Switch to application user
su - pawnsoft
```

### 2. Install Python 3.9+

```bash
# Install Python and dependencies
sudo apt install -y python3.9 python3.9-venv python3.9-dev python3-pip

# Create virtual environment
mkdir -p /home/pawnsoft/apps
cd /home/pawnsoft/apps
python3.9 -m venv pawnsoft-env
source pawnsoft-env/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install PostgreSQL

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql

# In PostgreSQL prompt:
CREATE DATABASE pawnsoft_db;
CREATE USER pawnsoft_user WITH ENCRYPTED PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE pawnsoft_db TO pawnsoft_user;
ALTER USER pawnsoft_user CREATEDB;
\q
```

### 4. Install Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

---

## 📁 Application Deployment

### 1. Clone and Setup Application

```bash
# Clone repository
cd /home/pawnsoft/apps
git clone https://github.com/rnrinfo2014/Pawnproledger-.git pawnsoft
cd pawnsoft/PawnProApi

# Activate virtual environment
source ../pawnsoft-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn uvicorn[standard]
```

### 2. Environment Configuration

```bash
# Create production environment file
cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://pawnsoft_user:secure_password_here@localhost:5432/pawnsoft_db

# Security Configuration
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_TITLE=PawnSoft API
API_DESCRIPTION=Complete Pawn Shop Management System
API_VERSION=1.0.0

# Environment
ENVIRONMENT=production
CORS_ORIGINS=https://rnrinfo.dev,https://app.rnrinfo.dev,https://api.rnrinfo.dev

# Security Features
ENABLE_SECURITY_HEADERS=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# File Upload
UPLOAD_DIR=/home/pawnsoft/apps/pawnsoft/PawnProApi/uploads
MAX_FILE_SIZE=10485760

# Logging
LOG_LEVEL=INFO
LOG_FILE=/home/pawnsoft/logs/pawnsoft.log
EOF

# Secure environment file
chmod 600 .env
```

### 3. Database Initialization

```bash
# Create database tables
python create_tables.py

# Initialize Chart of Accounts
python -c "
from coa_api import initialize_pawn_shop_coa
from database import SessionLocal
db = SessionLocal()
try:
    initialize_pawn_shop_coa(db, company_id=1)
    print('✅ Chart of Accounts initialized')
finally:
    db.close()
"

# Create initial admin user
python -c "
from database import SessionLocal
from models import User
from auth import get_password_hash
db = SessionLocal()
try:
    admin_user = User(
        username='admin',
        email='admin@rnrinfo.dev',
        password_hash=get_password_hash('admin_password_here'),
        role='admin'
    )
    db.add(admin_user)
    db.commit()
    print('✅ Admin user created')
except Exception as e:
    print(f'⚠️ Admin user creation: {e}')
finally:
    db.close()
"
```

### 4. Create Upload Directory

```bash
# Create upload directory with proper permissions
sudo mkdir -p /home/pawnsoft/apps/pawnsoft/PawnProApi/uploads
sudo chown -R pawnsoft:pawnsoft /home/pawnsoft/apps/pawnsoft/PawnProApi/uploads
sudo chmod 755 /home/pawnsoft/apps/pawnsoft/PawnProApi/uploads

# Create logs directory
sudo mkdir -p /home/pawnsoft/logs
sudo chown -R pawnsoft:pawnsoft /home/pawnsoft/logs
```

---

## 🔒 SSL Certificate Setup

### 1. Install Certbot

```bash
# Install Certbot for Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx

# Stop Nginx temporarily
sudo systemctl stop nginx
```

### 2. Obtain SSL Certificate

```bash
# Get SSL certificate for your domain
sudo certbot certonly --standalone -d rnrinfo.dev -d api.rnrinfo.dev

# Certificate files will be saved to:
# /etc/letsencrypt/live/rnrinfo.dev/fullchain.pem
# /etc/letsencrypt/live/rnrinfo.dev/privkey.pem
```

### 3. Setup Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Add cron job for auto-renewal
sudo crontab -e

# Add this line to crontab:
0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx
```

---

## 🌐 Nginx Configuration

### 1. Create Nginx Configuration

```bash
# Create site configuration
sudo tee /etc/nginx/sites-available/pawnsoft << EOF
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name rnrinfo.dev api.rnrinfo.dev;
    return 301 https://\$server_name\$request_uri;
}

# Main application server
server {
    listen 443 ssl http2;
    server_name api.rnrinfo.dev;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/rnrinfo.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/rnrinfo.dev/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-CHACHA20-POLY1305;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Rate Limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    # File Upload Limits
    client_max_body_size 10M;
    
    # API Proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
        proxy_connect_timeout 86400;
        proxy_send_timeout 86400;
    }
    
    # Static files for uploads
    location /uploads/ {
        alias /home/pawnsoft/apps/pawnsoft/PawnProApi/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check endpoint (bypass rate limiting)
    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        access_log off;
    }
}

# Frontend server (if you have a frontend)
server {
    listen 443 ssl http2;
    server_name rnrinfo.dev;
    
    # SSL Configuration (same as above)
    ssl_certificate /etc/letsencrypt/live/rnrinfo.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/rnrinfo.dev/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-CHACHA20-POLY1305;
    
    # Frontend files location
    root /home/pawnsoft/apps/frontend/dist;
    index index.html;
    
    # Try files or fallback to index.html for SPA
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/pawnsoft /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Start Nginx
sudo systemctl start nginx
sudo systemctl reload nginx
```

---

## 🏃‍♂️ Application Service

### 1. Create Systemd Service

```bash
# Create service file
sudo tee /etc/systemd/system/pawnsoft.service << EOF
[Unit]
Description=PawnSoft FastAPI Application
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=pawnsoft
Group=pawnsoft
WorkingDirectory=/home/pawnsoft/apps/pawnsoft/PawnProApi
Environment=PATH=/home/pawnsoft/apps/pawnsoft-env/bin
ExecStart=/home/pawnsoft/apps/pawnsoft-env/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/home/pawnsoft/apps/pawnsoft/PawnProApi/uploads /home/pawnsoft/logs
ProtectHome=yes

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl enable pawnsoft
sudo systemctl start pawnsoft

# Check status
sudo systemctl status pawnsoft
```

### 2. Create Gunicorn Configuration

```bash
# Create Gunicorn config file
cat > /home/pawnsoft/apps/pawnsoft/PawnProApi/gunicorn.conf.py << EOF
# Gunicorn configuration file

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
worker_tmp_dir = "/dev/shm"
timeout = 30
keepalive = 5

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
access_log = "/home/pawnsoft/logs/access.log"
error_log = "/home/pawnsoft/logs/error.log"
log_level = "info"
log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "pawnsoft"

# Daemon mode
daemon = False

# User and group to run as
user = "pawnsoft"
group = "pawnsoft"

# Preload app for memory efficiency
preload_app = True

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
EOF
```

---

## 🐳 Docker Deployment (Alternative)

### 1. Create Dockerfile

```dockerfile
# Multi-stage build for production
FROM python:3.9-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.9-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash pawnsoft

# Copy dependencies from builder
COPY --from=builder /root/.local /home/pawnsoft/.local

# Set environment variables
ENV PATH=/home/pawnsoft/.local/bin:$PATH
ENV PYTHONPATH=/app

# Copy application
WORKDIR /app
COPY --chown=pawnsoft:pawnsoft . .

# Create directories
RUN mkdir -p uploads logs && chown -R pawnsoft:pawnsoft uploads logs

# Switch to non-root user
USER pawnsoft

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["gunicorn", "main:app", "-c", "gunicorn.conf.py"]
```

### 2. Docker Compose

```yaml
version: '3.8'

services:
  pawnsoft-api:
    build: .
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://pawnsoft_user:password@db:5432/pawnsoft_db
      - ENVIRONMENT=production
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    depends_on:
      - db
    networks:
      - pawnsoft-network

  db:
    image: postgres:13
    restart: unless-stopped
    environment:
      - POSTGRES_DB=pawnsoft_db
      - POSTGRES_USER=pawnsoft_user
      - POSTGRES_PASSWORD=secure_password_here
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - pawnsoft-network

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - pawnsoft-api
    networks:
      - pawnsoft-network

volumes:
  postgres_data:

networks:
  pawnsoft-network:
    driver: bridge
```

---

## 📊 Monitoring & Logging

### 1. Application Logging

```bash
# Create log rotation configuration
sudo tee /etc/logrotate.d/pawnsoft << EOF
/home/pawnsoft/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 pawnsoft pawnsoft
    postrotate
        systemctl reload pawnsoft
    endscript
}
EOF
```

### 2. System Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Monitor application
sudo systemctl status pawnsoft
sudo journalctl -u pawnsoft -f

# Monitor database
sudo -u postgres psql -c "
SELECT 
    datname,
    numbackends,
    xact_commit,
    xact_rollback,
    blks_read,
    blks_hit
FROM pg_stat_database 
WHERE datname = 'pawnsoft_db';
"
```

### 3. Health Monitoring Script

```bash
# Create health check script
cat > /home/pawnsoft/scripts/health_check.sh << 'EOF'
#!/bin/bash

# Health check script for PawnSoft

API_URL="https://api.rnrinfo.dev/health"
LOG_FILE="/home/pawnsoft/logs/health_check.log"
EMAIL="admin@rnrinfo.dev"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check API health
if curl -f -s "$API_URL" > /dev/null; then
    log_message "✅ API is healthy"
else
    log_message "❌ API health check failed"
    echo "PawnSoft API health check failed at $(date)" | mail -s "PawnSoft Alert" "$EMAIL"
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
if [ "$DISK_USAGE" -gt 80 ]; then
    log_message "⚠️ Disk usage is ${DISK_USAGE}%"
    echo "Disk usage is ${DISK_USAGE}% on $(hostname)" | mail -s "PawnSoft Disk Alert" "$EMAIL"
fi

# Check memory usage
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ "$MEMORY_USAGE" -gt 80 ]; then
    log_message "⚠️ Memory usage is ${MEMORY_USAGE}%"
fi
EOF

chmod +x /home/pawnsoft/scripts/health_check.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/pawnsoft/scripts/health_check.sh") | crontab -
```

---

## 🔄 Backup & Recovery

### 1. Database Backup Script

```bash
# Create backup script
cat > /home/pawnsoft/scripts/backup_db.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/home/pawnsoft/backups"
DB_NAME="pawnsoft_db"
DB_USER="pawnsoft_user"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/pawnsoft_backup_$DATE.sql"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create database backup
pg_dump -h localhost -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Remove backups older than 30 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
EOF

chmod +x /home/pawnsoft/scripts/backup_db.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /home/pawnsoft/scripts/backup_db.sh") | crontab -
```

### 2. Application Backup

```bash
# Create application backup script
cat > /home/pawnsoft/scripts/backup_app.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/home/pawnsoft/backups"
APP_DIR="/home/pawnsoft/apps/pawnsoft"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/app_backup_$DATE.tar.gz"

# Create backup
tar -czf "$BACKUP_FILE" \
    --exclude="$APP_DIR/PawnProApi/__pycache__" \
    --exclude="$APP_DIR/PawnProApi/.env" \
    "$APP_DIR/PawnProApi/uploads" \
    "$APP_DIR/PawnProApi"/*.py \
    "$APP_DIR/PawnProApi"/*.md \
    "$APP_DIR/PawnProApi/requirements.txt"

echo "Application backup completed: $BACKUP_FILE"
EOF

chmod +x /home/pawnsoft/scripts/backup_app.sh
```

---

## 🔧 Maintenance

### 1. Update Procedure

```bash
# Create update script
cat > /home/pawnsoft/scripts/update_app.sh << 'EOF'
#!/bin/bash

APP_DIR="/home/pawnsoft/apps/pawnsoft"
VENV_DIR="/home/pawnsoft/apps/pawnsoft-env"

echo "🔄 Starting PawnSoft update..."

# Backup current version
/home/pawnsoft/scripts/backup_app.sh

# Stop application
sudo systemctl stop pawnsoft

# Pull latest changes
cd "$APP_DIR"
git pull origin master

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Update dependencies
cd "$APP_DIR/PawnProApi"
pip install -r requirements.txt

# Run database migrations (if any)
# python migrate_db.py

# Start application
sudo systemctl start pawnsoft

# Check status
sleep 5
if sudo systemctl is-active --quiet pawnsoft; then
    echo "✅ Update completed successfully"
else
    echo "❌ Update failed - check logs"
    sudo systemctl status pawnsoft
fi
EOF

chmod +x /home/pawnsoft/scripts/update_app.sh
```

### 2. SSL Certificate Renewal

```bash
# Test SSL renewal
sudo certbot renew --dry-run

# Manual renewal if needed
sudo certbot renew
sudo systemctl reload nginx
```

---

## 🧪 Deployment Testing

### 1. Post-Deployment Tests

```bash
# Test API endpoints
curl -X GET "https://api.rnrinfo.dev/health"
curl -X POST "https://api.rnrinfo.dev/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your_password"

# Test SSL certificate
openssl s_client -connect api.rnrinfo.dev:443 -servername api.rnrinfo.dev

# Test database connection
sudo -u postgres psql -c "\c pawnsoft_db; SELECT COUNT(*) FROM users;"
```

### 2. Performance Testing

```bash
# Install Apache Bench
sudo apt install -y apache2-utils

# Test API performance
ab -n 1000 -c 10 https://api.rnrinfo.dev/health

# Test with authentication
# (Create a script to get token and test authenticated endpoints)
```

---

## ⚠️ Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   sudo systemctl status pawnsoft
   sudo journalctl -u pawnsoft -f
   ```

2. **Database Connection Issues**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Test connection
   psql -h localhost -U pawnsoft_user -d pawnsoft_db
   ```

3. **SSL Certificate Issues**
   ```bash
   # Check certificate expiry
   sudo certbot certificates
   
   # Renew if needed
   sudo certbot renew --force-renewal
   ```

4. **Nginx Configuration Issues**
   ```bash
   # Test configuration
   sudo nginx -t
   
   # Check error logs
   sudo tail -f /var/log/nginx/error.log
   ```

---

## 📞 Support

- **Deployment Support**: deploy@rnrinfo.dev
- **Emergency Contact**: +1-xxx-xxx-xxxx
- **Documentation**: https://docs.rnrinfo.dev

---

**Last Updated**: January 15, 2025
**Deployment Version**: 1.0.0
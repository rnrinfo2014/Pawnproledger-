#!/bin/bash

# ==================================================================
# PAWNSOFT API DOMAIN SETUP SCRIPT
# ==================================================================
# This script helps you set up your custom domain for PawnSoft API

echo "🌐 PawnSoft API Domain Setup"
echo "=============================="

# Check if domain is provided
if [ -z "$1" ]; then
    echo "❌ Usage: $0 <your-domain.com>"
    echo "📝 Example: $0 mydomain.com"
    exit 1
fi

DOMAIN=$1
API_DOMAIN="api.$DOMAIN"
APP_DOMAIN="app.$DOMAIN"

echo "🔧 Setting up domain: $DOMAIN"
echo "📍 API will be at: https://$API_DOMAIN"
echo "🌍 App will be at: https://$APP_DOMAIN"

# Create production environment file
echo "📝 Creating production environment configuration..."
cat > .env << EOF
# Production Configuration for $DOMAIN
ENVIRONMENT=production
DOMAIN=$DOMAIN
API_SUBDOMAIN=api
FORCE_HTTPS=true

# CORS Configuration
CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN,https://$APP_DOMAIN

# Server Configuration
HOST=0.0.0.0
PORT=443
USE_HTTPS=true

# SSL Certificate paths (update these with your actual paths)
SSL_CERT_FILE=/etc/letsencrypt/live/$DOMAIN/fullchain.pem
SSL_KEY_FILE=/etc/letsencrypt/live/$DOMAIN/privkey.pem

# Security Settings (CHANGE THESE!)
JWT_SECRET_KEY=CHANGE-THIS-TO-A-SECURE-KEY
SECRET_KEY=CHANGE-THIS-TOO

# Database (update with your production database)
DATABASE_URL=postgresql://username:password@localhost/pawnpro

# Rate limiting for production
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_PERIOD=3600

# Security features
ENABLE_SECURITY_HEADERS=true
MIN_PASSWORD_LENGTH=12
REQUIRE_SPECIAL_CHARS=true

# File uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf
UPLOAD_DIR=uploads
EOF

echo "✅ Environment file created: .env"
echo ""
echo "🔐 SSL Certificate Setup:"
echo "-------------------------"
echo "For Let's Encrypt (recommended):"
echo "sudo apt update && sudo apt install certbot"
echo "sudo certbot certonly --standalone -d $DOMAIN -d $API_DOMAIN -d $APP_DOMAIN"
echo ""
echo "🚀 Nginx Configuration:"
echo "----------------------"
echo "Create /etc/nginx/sites-available/$DOMAIN:"
cat << 'EOF'

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

EOF
echo ""
echo "📋 Next Steps:"
echo "-------------"
echo "1. 🔑 Generate secure keys:"
echo "   openssl rand -hex 32"
echo ""
echo "2. 🗄️  Update database URL in .env"
echo ""
echo "3. 🔒 Set up SSL certificates"
echo ""
echo "4. ⚙️  Configure reverse proxy (Nginx/Apache)"
echo ""
echo "5. 🚀 Run the API:"
echo "   python -m uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
echo "6. 🧪 Test your API:"
echo "   curl https://$API_DOMAIN/health"
echo ""
echo "✨ Your API will be available at: https://$API_DOMAIN"
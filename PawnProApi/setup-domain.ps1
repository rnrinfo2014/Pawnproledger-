# ==================================================================
# PAWNSOFT API DOMAIN SETUP SCRIPT (Windows PowerShell)
# ==================================================================
# This script helps you set up your custom domain for PawnSoft API

param(
    [Parameter(Mandatory=$true)]
    [string]$Domain
)

Write-Host "🌐 PawnSoft API Domain Setup" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

$API_DOMAIN = "api.$Domain"
$APP_DOMAIN = "app.$Domain"

Write-Host "🔧 Setting up domain: $Domain" -ForegroundColor Green
Write-Host "📍 API will be at: https://$API_DOMAIN" -ForegroundColor Yellow
Write-Host "🌍 App will be at: https://$APP_DOMAIN" -ForegroundColor Yellow

# Create production environment file
Write-Host "📝 Creating production environment configuration..." -ForegroundColor Blue

$envContent = @"
# Production Configuration for $Domain
ENVIRONMENT=production
DOMAIN=$Domain
API_SUBDOMAIN=api
FORCE_HTTPS=true

# CORS Configuration
CORS_ORIGINS=https://$Domain,https://www.$Domain,https://$APP_DOMAIN

# Server Configuration
HOST=0.0.0.0
PORT=443
USE_HTTPS=true

# SSL Certificate paths (update these with your actual paths)
SSL_CERT_FILE=C:\certificates\$Domain\fullchain.pem
SSL_KEY_FILE=C:\certificates\$Domain\privkey.pem

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
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8

Write-Host "✅ Environment file created: .env" -ForegroundColor Green
Write-Host ""
Write-Host "🔐 Next Steps for Domain Setup:" -ForegroundColor Cyan
Write-Host "-------------------------------" -ForegroundColor Cyan
Write-Host "1. 🔑 Generate secure keys:" -ForegroundColor Yellow
Write-Host "   Use online generator or OpenSSL" -ForegroundColor White
Write-Host ""
Write-Host "2. 🗄️  Update database URL in .env file" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. 🔒 Get SSL certificates:" -ForegroundColor Yellow
Write-Host "   - From your hosting provider" -ForegroundColor White
Write-Host "   - Or use Cloudflare" -ForegroundColor White
Write-Host "   - Or use Let's Encrypt" -ForegroundColor White
Write-Host ""
Write-Host "4. ⚙️  Configure your web server/hosting:" -ForegroundColor Yellow
Write-Host "   - Point $API_DOMAIN to your server" -ForegroundColor White
Write-Host "   - Set up reverse proxy if needed" -ForegroundColor White
Write-Host ""
Write-Host "5. 🚀 Deploy and run:" -ForegroundColor Yellow
Write-Host "   python -m uvicorn main:app --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host ""
Write-Host "6. 🧪 Test your API:" -ForegroundColor Yellow
Write-Host "   Invoke-WebRequest https://$API_DOMAIN/health" -ForegroundColor White
Write-Host ""
Write-Host "✨ Your API will be available at: https://$API_DOMAIN" -ForegroundColor Green

# Generate a secure key example
Write-Host ""
Write-Host "🔑 Here's a sample secure key (generate your own!):" -ForegroundColor Cyan
$secureKey = -join ((1..64) | ForEach {'{0:X}' -f (Get-Random -Max 16)})
Write-Host $secureKey -ForegroundColor Yellow
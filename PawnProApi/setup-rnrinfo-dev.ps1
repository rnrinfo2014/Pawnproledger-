# ==================================================================
# PAWNSOFT API DOMAIN SETUP FOR RNRINFO.DEV
# ==================================================================
# Quick setup script for rnrinfo.dev domain

Write-Host "🌐 PawnSoft API Setup for rnrinfo.dev" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "🔧 Configuring for domain: rnrinfo.dev" -ForegroundColor Green
Write-Host "📍 API will be at: https://api.rnrinfo.dev" -ForegroundColor Yellow
Write-Host "🌍 App will be at: https://app.rnrinfo.dev" -ForegroundColor Yellow
Write-Host "🏠 Main site: https://rnrinfo.dev" -ForegroundColor Yellow

# Create production environment file
Write-Host "📝 Creating production environment configuration..." -ForegroundColor Blue

$envContent = @"
# Production Configuration for rnrinfo.dev
ENVIRONMENT=production
DOMAIN=rnrinfo.dev
API_SUBDOMAIN=api
FORCE_HTTPS=true

# CORS Configuration for rnrinfo.dev
CORS_ORIGINS=https://rnrinfo.dev,https://www.rnrinfo.dev,https://api.rnrinfo.dev,https://app.rnrinfo.dev

# Server Configuration
HOST=0.0.0.0
PORT=443
USE_HTTPS=true

# SSL Certificate paths for rnrinfo.dev
SSL_CERT_FILE=/etc/letsencrypt/live/rnrinfo.dev/fullchain.pem
SSL_KEY_FILE=/etc/letsencrypt/live/rnrinfo.dev/privkey.pem

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
Write-Host "🔐 Next Steps for rnrinfo.dev:" -ForegroundColor Cyan
Write-Host "------------------------------" -ForegroundColor Cyan
Write-Host "1. 🔑 Generate secure keys:" -ForegroundColor Yellow
$randomChars = @()
for ($i = 1; $i -le 64; $i++) {
    $randomChars += '{0:X}' -f (Get-Random -Max 16)
}
$secureKey = -join $randomChars
Write-Host "   Sample JWT key: $secureKey" -ForegroundColor White
Write-Host ""
Write-Host "2. 🗄️  Update database URL in .env file" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. 🔒 Get SSL certificates for rnrinfo.dev:" -ForegroundColor Yellow
Write-Host "   - Use Cloudflare (recommended for .dev domains)" -ForegroundColor White
Write-Host "   - Or Let's Encrypt: certbot --standalone -d rnrinfo.dev -d api.rnrinfo.dev -d app.rnrinfo.dev" -ForegroundColor White
Write-Host ""
Write-Host "4. ⚙️  DNS Configuration for rnrinfo.dev:" -ForegroundColor Yellow
Write-Host "   A     rnrinfo.dev          → YOUR_SERVER_IP" -ForegroundColor White
Write-Host "   A     api.rnrinfo.dev      → YOUR_SERVER_IP" -ForegroundColor White
Write-Host "   A     app.rnrinfo.dev      → YOUR_SERVER_IP" -ForegroundColor White
Write-Host "   CNAME www.rnrinfo.dev      → rnrinfo.dev" -ForegroundColor White
Write-Host ""
Write-Host "5. 🚀 Deploy and run:" -ForegroundColor Yellow
Write-Host "   python -m uvicorn main:app --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host ""
Write-Host "6. 🧪 Test your API endpoints:" -ForegroundColor Yellow
Write-Host "   Invoke-WebRequest https://api.rnrinfo.dev/health" -ForegroundColor White
Write-Host "   Invoke-WebRequest https://api.rnrinfo.dev/docs" -ForegroundColor White
Write-Host ""
Write-Host "✨ Your PawnSoft API will be available at:" -ForegroundColor Green
Write-Host "   🔗 API: https://api.rnrinfo.dev" -ForegroundColor Cyan
Write-Host "   📖 Docs: https://api.rnrinfo.dev/docs" -ForegroundColor Cyan
Write-Host "   💚 Health: https://api.rnrinfo.dev/health" -ForegroundColor Cyan
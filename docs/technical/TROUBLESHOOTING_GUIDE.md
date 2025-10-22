# 🛠️ Troubleshooting Guide

Complete troubleshooting guide for PawnSoft Pawn Shop Management System

## 📋 Quick Reference

### Emergency Contacts
- **System Admin**: admin@rnrinfo.dev
- **Emergency Phone**: +1-xxx-xxx-xxxx
- **Support Portal**: https://support.rnrinfo.dev

### Health Check Commands
```bash
# Quick system health check
curl -f https://api.rnrinfo.dev/health
sudo systemctl status pawnsoft
sudo systemctl status postgresql
sudo systemctl status nginx
```

---

## 🚨 Common Issues & Solutions

### 1. Application Won't Start

#### Symptoms
- Service fails to start
- API endpoints not responding
- 502 Bad Gateway from Nginx

#### Diagnosis Commands
```bash
# Check service status
sudo systemctl status pawnsoft

# Check logs
sudo journalctl -u pawnsoft -f --lines=50

# Check if port is in use
sudo netstat -tlnp | grep :8000

# Check Python environment
source /home/pawnsoft/apps/pawnsoft-env/bin/activate
python --version
pip list | grep fastapi
```

#### Common Causes & Solutions

**Database Connection Error**
```bash
# Error: "could not connect to server"
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Test database connection
psql -h localhost -U pawnsoft_user -d pawnsoft_db -c "SELECT 1;"
```

**Permission Issues**
```bash
# Error: "Permission denied"
# Fix file permissions
sudo chown -R pawnsoft:pawnsoft /home/pawnsoft/apps/pawnsoft
sudo chmod -R 755 /home/pawnsoft/apps/pawnsoft
sudo chmod 644 /home/pawnsoft/apps/pawnsoft/PawnProApi/.env
```

**Environment Variables Missing**
```bash
# Error: "KeyError: 'DATABASE_URL'"
# Check .env file
cat /home/pawnsoft/apps/pawnsoft/PawnProApi/.env

# Verify environment file format
# No spaces around = sign
# No quotes needed for simple values
DATABASE_URL=postgresql://user:pass@localhost:5432/db
```

**Port Already in Use**
```bash
# Error: "Address already in use"
# Find process using port 8000
sudo lsof -i :8000

# Kill process if needed
sudo kill -9 <PID>

# Restart service
sudo systemctl restart pawnsoft
```

#### Step-by-Step Resolution

1. **Check Environment**
   ```bash
   cd /home/pawnsoft/apps/pawnsoft/PawnProApi
   source ../pawnsoft-env/bin/activate
   python -c "from config import settings; print(settings.database_url)"
   ```

2. **Test Database Connection**
   ```bash
   python -c "
   from database import engine
   with engine.connect() as conn:
       result = conn.execute('SELECT 1')
       print('Database OK')
   "
   ```

3. **Start in Debug Mode**
   ```bash
   # Stop service first
   sudo systemctl stop pawnsoft
   
   # Run manually to see errors
   cd /home/pawnsoft/apps/pawnsoft/PawnProApi
   source ../pawnsoft-env/bin/activate
   python -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```

4. **Check Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### 2. Database Issues

#### Connection Timeouts

**Symptoms**
- Slow API responses
- Database connection errors
- Connection pool exhausted

**Diagnosis**
```bash
# Check active connections
sudo -u postgres psql -c "
SELECT 
    count(*),
    state
FROM pg_stat_activity 
WHERE datname = 'pawnsoft_db'
GROUP BY state;
"

# Check long-running queries
sudo -u postgres psql -c "
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
"
```

**Solutions**
```bash
# Restart PostgreSQL
sudo systemctl restart postgresql

# Kill long-running queries
sudo -u postgres psql -c "SELECT pg_terminate_backend(<pid>);"

# Tune PostgreSQL configuration
sudo nano /etc/postgresql/13/main/postgresql.conf
# Increase max_connections
# Adjust shared_buffers
# Optimize work_mem
```

#### Database Corruption

**Symptoms**
- Data inconsistency
- Query errors
- Constraint violations

**Diagnosis & Recovery**
```bash
# Check database integrity
sudo -u postgres psql pawnsoft_db -c "
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public';
"

# Run VACUUM and ANALYZE
sudo -u postgres psql pawnsoft_db -c "VACUUM ANALYZE;"

# Check for corruption
sudo -u postgres psql pawnsoft_db -c "
SELECT 
    schemaname,
    tablename,
    attname,
    null_frac,
    avg_width,
    n_distinct
FROM pg_stats
WHERE schemaname = 'public'
AND null_frac > 0.8;
"

# Restore from backup if needed
psql -h localhost -U pawnsoft_user -d pawnsoft_db < /path/to/backup.sql
```

### 3. Authentication Issues

#### JWT Token Problems

**Symptoms**
- Login fails with correct credentials
- Token expired errors
- Unauthorized access errors

**Diagnosis**
```bash
# Test token generation
curl -X POST "https://api.rnrinfo.dev/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your_password"

# Decode JWT token (for debugging)
python -c "
import jwt
token = 'your-jwt-token-here'
try:
    decoded = jwt.decode(token, options={'verify_signature': False})
    print(decoded)
except Exception as e:
    print(f'Error: {e}')
"
```

**Solutions**

1. **Check Secret Key**
   ```bash
   # Verify SECRET_KEY in .env
   grep SECRET_KEY /home/pawnsoft/apps/pawnsoft/PawnProApi/.env
   
   # Generate new secret key if needed
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Check Token Expiry**
   ```bash
   # Check token expiry setting
   grep ACCESS_TOKEN_EXPIRE_MINUTES /home/pawnsoft/apps/pawnsoft/PawnProApi/.env
   ```

3. **Password Hash Verification**
   ```bash
   python -c "
   from auth import verify_password, get_password_hash
   plain = 'your_password'
   hashed = get_password_hash(plain)
   print(f'Hash: {hashed}')
   print(f'Verify: {verify_password(plain, hashed)}')
   "
   ```

#### User Account Issues

**Account Locked/Disabled**
```sql
-- Check user status
SELECT id, username, email, is_active, role, created_at
FROM users 
WHERE username = 'problematic_user';

-- Reactivate user
UPDATE users 
SET is_active = true 
WHERE username = 'problematic_user';
```

**Password Reset**
```bash
python -c "
from database import SessionLocal
from models import User
from auth import get_password_hash

db = SessionLocal()
user = db.query(User).filter(User.username == 'username').first()
if user:
    user.password_hash = get_password_hash('new_password')
    db.commit()
    print('Password updated')
db.close()
"
```

### 4. Performance Issues

#### Slow API Responses

**Symptoms**
- High response times (>2 seconds)
- Timeout errors
- High CPU/memory usage

**Diagnosis**
```bash
# Monitor system resources
htop
iotop
nethogs

# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s "https://api.rnrinfo.dev/health"

# Create curl-format.txt
echo 'time_namelookup:  %{time_namelookup}
time_connect:     %{time_connect}
time_appconnect:  %{time_appconnect}
time_pretransfer: %{time_pretransfer}
time_redirect:    %{time_redirect}
time_starttransfer: %{time_starttransfer}
time_total:       %{time_total}' > curl-format.txt
```

**Database Performance Tuning**
```sql
-- Find slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;

-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_pledges_customer_status 
ON pledges(customer_id, status);

CREATE INDEX CONCURRENTLY idx_payments_date_pledge 
ON pledge_payments(payment_date, pledge_id);
```

**Application Performance Optimization**
```bash
# Increase Gunicorn workers
sudo nano /etc/systemd/system/pawnsoft.service

# Update ExecStart line
ExecStart=/home/pawnsoft/apps/pawnsoft-env/bin/gunicorn main:app -w 6 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000

# Restart service
sudo systemctl daemon-reload
sudo systemctl restart pawnsoft
```

#### Memory Issues

**Symptoms**
- Out of memory errors
- Application crashes
- Swap usage high

**Monitoring**
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Monitor memory over time
watch -n 5 'free -h && echo "---" && ps aux --sort=-%mem | head -5'

# Check swap usage
swapon -s
```

**Solutions**
```bash
# Add swap space if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Add to /etc/fstab for persistence
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Tune Gunicorn memory settings
# Add to gunicorn.conf.py
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

### 5. SSL/HTTPS Issues

#### Certificate Problems

**Symptoms**
- SSL certificate warnings
- HTTPS not working
- Certificate expired errors

**Diagnosis**
```bash
# Check certificate expiry
sudo certbot certificates

# Test SSL configuration
openssl s_client -connect api.rnrinfo.dev:443 -servername api.rnrinfo.dev

# Check certificate details
echo | openssl s_client -connect api.rnrinfo.dev:443 -servername api.rnrinfo.dev 2>/dev/null | openssl x509 -noout -dates
```

**Solutions**
```bash
# Renew certificates
sudo certbot renew

# Force renewal if needed
sudo certbot renew --force-renewal

# Test renewal process
sudo certbot renew --dry-run

# Check Nginx SSL configuration
sudo nginx -t
```

#### Mixed Content Issues

**Problem**: HTTPS site loading HTTP resources

**Solution**
```nginx
# Update Nginx configuration
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $server_name;
}
```

### 6. File Upload Issues

#### Upload Failures

**Symptoms**
- File upload returns errors
- Large files failing
- Permission denied errors

**Diagnosis**
```bash
# Check upload directory permissions
ls -la /home/pawnsoft/apps/pawnsoft/PawnProApi/uploads/

# Check disk space
df -h

# Test file upload
curl -X POST "https://api.rnrinfo.dev/upload_file" \
  -H "Authorization: Bearer your-token" \
  -F "file=@test-image.jpg" \
  -F "company_id=1" \
  -F "upload_type=test"
```

**Solutions**
```bash
# Fix permissions
sudo chown -R pawnsoft:pawnsoft /home/pawnsoft/apps/pawnsoft/PawnProApi/uploads/
sudo chmod -R 755 /home/pawnsoft/apps/pawnsoft/PawnProApi/uploads/

# Increase Nginx upload limits
sudo nano /etc/nginx/sites-available/pawnsoft
# Add: client_max_body_size 10M;

# Check FastAPI file size limits
grep MAX_FILE_SIZE /home/pawnsoft/apps/pawnsoft/PawnProApi/.env
```

### 7. Backup & Recovery Issues

#### Backup Failures

**Symptoms**
- Backup scripts failing
- Corrupted backup files
- Insufficient disk space

**Diagnosis**
```bash
# Check backup script logs
tail -f /home/pawnsoft/logs/backup.log

# Test backup manually
/home/pawnsoft/scripts/backup_db.sh

# Check backup file integrity
pg_restore --list /path/to/backup.sql.gz
```

**Solutions**
```bash
# Fix backup script permissions
chmod +x /home/pawnsoft/scripts/backup_db.sh

# Clean old backups
find /home/pawnsoft/backups -name "*.sql.gz" -mtime +30 -delete

# Test restore process
pg_restore -h localhost -U pawnsoft_user -d test_db /path/to/backup.sql.gz
```

#### Data Recovery

**Emergency Recovery Process**
```bash
# 1. Stop application
sudo systemctl stop pawnsoft

# 2. Create backup of current state
pg_dump -h localhost -U pawnsoft_user pawnsoft_db > emergency_backup.sql

# 3. Restore from known good backup
dropdb -h localhost -U pawnsoft_user pawnsoft_db
createdb -h localhost -U pawnsoft_user pawnsoft_db
pg_restore -h localhost -U pawnsoft_user -d pawnsoft_db latest_backup.sql.gz

# 4. Restart application
sudo systemctl start pawnsoft

# 5. Verify data integrity
python -c "
from database import SessionLocal
from models import User, Company, Customer
db = SessionLocal()
print(f'Users: {db.query(User).count()}')
print(f'Companies: {db.query(Company).count()}')
print(f'Customers: {db.query(Customer).count()}')
db.close()
"
```

---

## 🔧 Maintenance Procedures

### Daily Maintenance

```bash
#!/bin/bash
# Daily maintenance script

echo "🔄 Starting daily maintenance..."

# Check system health
echo "Checking system health..."
systemctl is-active --quiet pawnsoft && echo "✅ Application: Running" || echo "❌ Application: Down"
systemctl is-active --quiet postgresql && echo "✅ Database: Running" || echo "❌ Database: Down"
systemctl is-active --quiet nginx && echo "✅ Web Server: Running" || echo "❌ Web Server: Down"

# Check disk space
echo "Checking disk space..."
df -h / | awk 'NR==2 {print "Disk usage: " $5}'

# Check memory usage
echo "Checking memory usage..."
free -h | awk 'NR==2 {print "Memory usage: " $3 "/" $2}'

# Check recent errors
echo "Checking recent errors..."
journalctl -u pawnsoft --since "1 hour ago" --priority=err --no-pager | tail -5

# Backup database
echo "Running database backup..."
/home/pawnsoft/scripts/backup_db.sh

echo "✅ Daily maintenance completed"
```

### Weekly Maintenance

```bash
#!/bin/bash
# Weekly maintenance script

echo "🔄 Starting weekly maintenance..."

# Update system packages
sudo apt update && sudo apt list --upgradable

# Analyze database performance
psql -h localhost -U pawnsoft_user -d pawnsoft_db -c "ANALYZE;"

# Clean up old logs
find /home/pawnsoft/logs -name "*.log.*" -mtime +7 -delete

# Check SSL certificate expiry
certbot certificates | grep "Expiry Date"

# Generate weekly report
python /home/pawnsoft/scripts/weekly_report.py

echo "✅ Weekly maintenance completed"
```

### Monthly Maintenance

```bash
#!/bin/bash
# Monthly maintenance script

echo "🔄 Starting monthly maintenance..."

# Full database vacuum
psql -h localhost -U pawnsoft_user -d pawnsoft_db -c "VACUUM FULL;"

# Update statistics
psql -h localhost -U pawnsoft_user -d pawnsoft_db -c "
UPDATE pg_stat_statements_reset();
ANALYZE;
"

# Archive old data
python /home/pawnsoft/scripts/archive_old_data.py

# Security audit
/home/pawnsoft/scripts/security_audit.sh

# Performance report
/home/pawnsoft/scripts/performance_report.sh

echo "✅ Monthly maintenance completed"
```

---

## 📊 Monitoring & Alerting

### Log Monitoring

**Key Log Files**
```bash
# Application logs
tail -f /home/pawnsoft/logs/pawnsoft.log

# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log

# PostgreSQL logs
tail -f /var/log/postgresql/postgresql-13-main.log

# System logs
journalctl -u pawnsoft -f
```

**Log Analysis Scripts**
```bash
# Find API errors
grep "ERROR" /home/pawnsoft/logs/pawnsoft.log | tail -20

# Find 5xx errors in Nginx
awk '$9 >= 500' /var/log/nginx/access.log | tail -10

# Find slow database queries
grep "LOG:.*duration:" /var/log/postgresql/postgresql-13-main.log | tail -10
```

### Performance Monitoring

**System Metrics**
```bash
# Create monitoring script
cat > /home/pawnsoft/scripts/monitor.sh << 'EOF'
#!/bin/bash

LOG_FILE="/home/pawnsoft/logs/system_metrics.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# CPU usage
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)

# Memory usage
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')

# Disk usage
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)

# Database connections
DB_CONNECTIONS=$(psql -h localhost -U pawnsoft_user -d pawnsoft_db -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname='pawnsoft_db';" 2>/dev/null || echo "0")

# Log metrics
echo "$TIMESTAMP,CPU:${CPU_USAGE}%,Memory:${MEMORY_USAGE}%,Disk:${DISK_USAGE}%,DB_Conn:$DB_CONNECTIONS" >> "$LOG_FILE"

# Alert if thresholds exceeded
if [ "$CPU_USAGE" -gt 80 ] || [ "$MEMORY_USAGE" -gt 80 ] || [ "$DISK_USAGE" -gt 80 ]; then
    echo "ALERT: High resource usage detected at $TIMESTAMP" | mail -s "PawnSoft Alert" admin@rnrinfo.dev
fi
EOF

chmod +x /home/pawnsoft/scripts/monitor.sh

# Run every 5 minutes
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/pawnsoft/scripts/monitor.sh") | crontab -
```

---

## 🆘 Emergency Procedures

### System Down - Emergency Response

1. **Immediate Assessment**
   ```bash
   # Check if it's a network issue
   ping google.com
   
   # Check if server is responsive
   curl -I https://api.rnrinfo.dev/health
   
   # Check core services
   sudo systemctl status pawnsoft postgresql nginx
   ```

2. **Quick Recovery Attempts**
   ```bash
   # Restart application
   sudo systemctl restart pawnsoft
   
   # If database issues
   sudo systemctl restart postgresql
   
   # If web server issues
   sudo systemctl restart nginx
   ```

3. **If Quick Recovery Fails**
   ```bash
   # Check logs for root cause
   journalctl -u pawnsoft --since "10 minutes ago"
   
   # Check disk space
   df -h
   
   # Check memory
   free -h
   
   # Check processes
   ps aux --sort=-%cpu | head -10
   ```

### Data Loss Emergency

1. **Immediate Response**
   ```bash
   # Stop all write operations
   sudo systemctl stop pawnsoft
   
   # Assess damage
   psql -h localhost -U pawnsoft_user -d pawnsoft_db -c "
   SELECT 
       schemaname,
       tablename,
       n_tup_ins,
       n_tup_upd,
       n_tup_del
   FROM pg_stat_user_tables
   ORDER BY n_tup_del DESC;
   "
   ```

2. **Recovery Process**
   ```bash
   # Restore from latest backup
   pg_restore -h localhost -U pawnsoft_user -d pawnsoft_db_recovery /path/to/latest/backup.sql.gz
   
   # Compare data
   psql -h localhost -U pawnsoft_user -c "
   SELECT 'original' as db, count(*) from pawnsoft_db.users
   UNION ALL
   SELECT 'recovery' as db, count(*) from pawnsoft_db_recovery.users;
   "
   ```

### Security Incident Response

1. **Immediate Actions**
   ```bash
   # Block suspicious IPs
   sudo ufw deny from <suspicious_ip>
   
   # Change critical passwords
   # Reset admin passwords
   # Regenerate JWT secret keys
   
   # Review access logs
   grep "POST /token" /var/log/nginx/access.log | tail -50
   ```

2. **Investigation**
   ```bash
   # Check for unauthorized access
   grep "401\|403" /var/log/nginx/access.log | tail -20
   
   # Review user activities
   psql -h localhost -U pawnsoft_user -d pawnsoft_db -c "
   SELECT * FROM audit_logs 
   WHERE created_at > NOW() - INTERVAL '24 hours'
   ORDER BY created_at DESC
   LIMIT 50;
   "
   ```

---

## 📞 Support Escalation

### Level 1 Support (Basic Issues)
- **Time**: Immediate self-service
- **Issues**: Common errors, restarts, basic troubleshooting
- **Resources**: This guide, logs, system commands

### Level 2 Support (Technical Issues)
- **Contact**: technical-support@rnrinfo.dev
- **Time**: 2-4 hours response
- **Issues**: Performance problems, configuration changes, data issues

### Level 3 Support (Critical Issues)
- **Contact**: emergency@rnrinfo.dev
- **Phone**: +1-xxx-xxx-xxxx
- **Time**: 30 minutes response
- **Issues**: System down, data loss, security incidents

### Escalation Information to Provide

```
System Information:
- Server IP: xxx.xxx.xxx.xxx
- OS Version: Ubuntu 20.04
- Application Version: 1.0.0
- Database Version: PostgreSQL 13
- Last Working Time: YYYY-MM-DD HH:MM:SS

Issue Description:
- Error symptoms
- When did it start
- What changed recently
- Error messages
- Steps already tried

Impact Assessment:
- Users affected
- Business operations impact
- Data at risk
- Revenue impact
```

---

**Support Team**: Technical Operations
**Last Updated**: January 15, 2025
**Guide Version**: 1.0.0
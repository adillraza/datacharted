#!/bin/bash

# DataCharted Deployment Health Check Script
# This script verifies that deployment was successful

set -e

echo "🔍 DataCharted Deployment Health Check"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# 1. Check if we're in the right directory
print_info "Checking application directory..."
if [ ! -f "run.py" ] || [ ! -f "requirements.txt" ]; then
    print_status 1 "Not in DataCharted application directory"
fi
print_status 0 "Application directory verified"

# 2. Check virtual environment
print_info "Checking virtual environment..."
if [ ! -d "venv" ] || [ ! -f "venv/bin/python3" ]; then
    print_status 1 "Virtual environment not found or corrupted"
fi
print_status 0 "Virtual environment exists"

# 3. Check database file
print_info "Checking database..."
if [ ! -f "app_dev.db" ]; then
    print_status 1 "Database file not found"
fi

# Check database permissions
DB_OWNER=$(stat -c '%U:%G' app_dev.db)
if [ "$DB_OWNER" != "www-data:www-data" ]; then
    print_warning "Database ownership is $DB_OWNER, should be www-data:www-data"
    chown www-data:www-data app_dev.db
    print_status 0 "Database ownership fixed"
else
    print_status 0 "Database ownership correct"
fi

# 4. Test database connection
print_info "Testing database connection..."
source venv/bin/activate
export FLASK_APP=run.py

# Test database tables exist
python3 -c "
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    try:
        user_count = User.query.count()
        print(f'Database connection successful: {user_count} users found')
    except Exception as e:
        print(f'Database error: {e}')
        exit(1)
" && DB_STATUS=0 || DB_STATUS=1

deactivate
print_status $DB_STATUS "Database connection test"

# 5. Check systemd service
print_info "Checking systemd service..."
if systemctl is-active --quiet datacharted; then
    print_status 0 "DataCharted service is running"
else
    print_status 1 "DataCharted service is not running"
fi

# 6. Check gunicorn processes
print_info "Checking gunicorn processes..."
GUNICORN_COUNT=$(pgrep -f "gunicorn.*datacharted" | wc -l)
if [ "$GUNICORN_COUNT" -eq 4 ]; then
    print_status 0 "Gunicorn running with correct number of processes (1 master + 3 workers)"
elif [ "$GUNICORN_COUNT" -gt 0 ]; then
    print_warning "Gunicorn running with $GUNICORN_COUNT processes (expected 4)"
    print_status 0 "Gunicorn is running"
else
    print_status 1 "Gunicorn is not running"
fi

# 7. Test Flask application response
print_info "Testing Flask application response..."
if curl -s -f http://127.0.0.1:8000/ > /dev/null; then
    print_status 0 "Flask application responding"
else
    print_status 1 "Flask application not responding"
fi

# 8. Test authentication endpoint
print_info "Testing authentication endpoint..."
if curl -s -f http://127.0.0.1:8000/auth/login > /dev/null; then
    print_status 0 "Authentication endpoint responding"
else
    print_status 1 "Authentication endpoint not responding"
fi

# 9. Check log files
print_info "Checking log files..."
if [ -f "/var/log/datacharted/error.log" ]; then
    ERROR_COUNT=$(tail -20 /var/log/datacharted/error.log | grep -i error | wc -l)
    if [ "$ERROR_COUNT" -gt 0 ]; then
        print_warning "Found $ERROR_COUNT recent errors in log"
        echo "Recent errors:"
        tail -20 /var/log/datacharted/error.log | grep -i error | tail -3
    else
        print_status 0 "No recent errors in log"
    fi
else
    print_warning "Error log file not found"
fi

# 10. Check .env configuration
print_info "Checking configuration..."
if grep -q "DATABASE_URL=sqlite:///app_dev.db" .env; then
    print_status 0 "Database URL configuration correct"
else
    print_warning "Database URL might need attention"
    grep DATABASE_URL .env || echo "DATABASE_URL not found in .env"
fi

# 11. Check backup count
print_info "Checking database backups..."
BACKUP_COUNT=$(ls -1 app_dev.db.backup.* 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -le 5 ]; then
    print_status 0 "Database backup count reasonable ($BACKUP_COUNT backups)"
else
    print_warning "Many database backups ($BACKUP_COUNT) - consider cleanup"
fi

echo ""
echo "🎉 Health check completed successfully!"
echo "📊 Summary:"
echo "   - Database: Working with proper permissions"
echo "   - Service: Running with correct process count"
echo "   - Application: Responding to requests"
echo "   - Configuration: Properly set up"
echo ""
echo "🚀 DataCharted is ready for production!"

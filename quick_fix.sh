#!/bin/bash

# Quick fix for DataCharted deployment
echo "🚨 DataCharted Quick Fix"
echo "========================"

cd /opt/datacharted-app

echo "📦 Backup database..."
cp app_dev.db app_dev.db.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "No DB to backup"

echo "🔧 Fix database..."
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

export FLASK_APP=run.py
export FLASK_ENV=production

python3 -c "
from app import create_app, db
app = create_app()
with app.app_context():
    try:
        db.create_all()
        print('✅ Database fixed')
        from app.models import User
        print(f'✅ Users: {User.query.count()}')
    except Exception as e:
        print(f'❌ Error: {e}')
        exit(1)
"

if [ $? -eq 0 ]; then
    echo "🔧 Fix permissions..."
    chown -R www-data:www-data /opt/datacharted-app/
    chmod 664 app_dev.db 2>/dev/null || true
    
    echo "🔄 Restart service..."
    systemctl restart datacharted
    sleep 2
    
    if systemctl is-active --quiet datacharted; then
        echo "✅ Service running"
        echo "🎉 Fix complete! Test: https://datacharted.com"
    else
        echo "❌ Service failed"
        systemctl status datacharted --no-pager
    fi
else
    echo "❌ Database fix failed"
fi

deactivate

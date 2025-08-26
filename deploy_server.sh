#!/bin/bash

# DataCharted Manual Server Deployment Script
# Use this ONLY for manual deployments (GitHub Actions handles automatic deployments)
# This script safely deploys updates while preserving email configuration

echo "🚀 DataCharted Manual Server Deployment"
echo "========================================"
echo "⚠️  Note: This is for manual deployment only"
echo "    GitHub Actions automatically deploys when you push to main"
echo ""
echo "Continue? (y/N)"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

# Navigate to app directory
cd /opt/datacharted-app

echo "📦 Backing up current .env file..."
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

echo "📥 Pulling latest changes from GitHub..."
git pull origin main

echo "📧 Checking email configuration..."
if ! grep -q "MAIL_PASSWORD=zzqh tfur yocr whhk" .env; then
    echo "⚠️  Email configuration missing, restoring..."
    python3 setup_live_email.py
else
    echo "✅ Email configuration is intact"
fi

echo "📦 Installing/updating dependencies..."
source venv/bin/activate
pip3 install -r requirements.txt

# Backup database before migration
echo "📦 Backing up database before migration..."
if [ -f "app_dev.db" ]; then
    cp app_dev.db app_dev.db.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Database backup created"
fi

echo "🗄️  Running database migrations..."
export FLASK_APP=run.py
export FLASK_ENV=production

echo "Current migration: $(flask db current)"

if flask db upgrade; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migration failed - stopping deployment"
    deactivate
    exit 1
fi

echo "New migration: $(flask db current)"
deactivate

echo "🔄 Restarting service..."
systemctl restart datacharted

# Verify service started successfully
if systemctl is-active --quiet datacharted; then
    echo "✅ Service restarted successfully"
else
    echo "❌ Service failed to start"
    systemctl status datacharted --no-pager
    exit 1
fi

echo "✅ Checking service status..."
systemctl status datacharted --no-pager

echo "🎉 Deployment complete!"
echo "📧 Email functionality preserved"
echo "🔗 Your app is live at: https://app.datacharted.com"

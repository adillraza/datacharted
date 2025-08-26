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

echo "🗄️  Running database migrations..."
export FLASK_APP=run.py
flask db upgrade

echo "🔄 Restarting service..."
systemctl restart datacharted

echo "✅ Checking service status..."
systemctl status datacharted --no-pager

echo "🎉 Deployment complete!"
echo "📧 Email functionality preserved"
echo "🔗 Your app is live at: https://app.datacharted.com"

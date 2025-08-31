#!/bin/bash

# DataCharted Domain Redirect Setup Script
# This script sets up nginx to redirect datacharted.com -> app.datacharted.com
# Run this on your VPS server (165.232.38.9)

set -e  # Exit on any error

echo "🔄 DataCharted Domain Redirect Setup"
echo "===================================="
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)"
   exit 1
fi

echo "📋 Step 1: Installing Nginx..."
apt update
apt install nginx -y
systemctl enable nginx

echo "✅ Nginx installed successfully"
echo ""

echo "📋 Step 2: Creating redirect configuration..."

# Create the nginx configuration
cat > /etc/nginx/sites-available/datacharted-redirect << 'EOF'
# DataCharted Domain Redirect Configuration
# Purpose: Redirect all traffic from datacharted.com to app.datacharted.com

# HTTP Redirect (Port 80)
server {
    listen 80;
    listen [::]:80;
    server_name datacharted.com www.datacharted.com;
    
    # Log access for monitoring
    access_log /var/log/nginx/datacharted-redirect.access.log;
    error_log /var/log/nginx/datacharted-redirect.error.log;
    
    # Permanent redirect (301) to app.datacharted.com with HTTPS
    return 301 https://app.datacharted.com$request_uri;
}
EOF

echo "✅ Configuration file created: /etc/nginx/sites-available/datacharted-redirect"
echo ""

echo "📋 Step 3: Enabling the configuration..."

# Enable the site
ln -sf /etc/nginx/sites-available/datacharted-redirect /etc/nginx/sites-enabled/

# Remove default nginx site if it exists
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
    echo "✅ Removed default nginx site"
fi

echo "✅ Configuration enabled"
echo ""

echo "📋 Step 4: Testing nginx configuration..."
if nginx -t; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration has errors"
    exit 1
fi

echo ""
echo "📋 Step 5: Starting/restarting nginx..."
systemctl restart nginx
systemctl status nginx --no-pager -l

echo ""
echo "🎉 Domain redirect setup complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Update your DNS records to point datacharted.com to this server (165.232.38.9)"
echo "2. Wait for DNS propagation (5-60 minutes)"
echo "3. Test the redirect: curl -I http://datacharted.com"
echo "4. Optional: Set up SSL certificates with: certbot --nginx -d datacharted.com -d www.datacharted.com"
echo ""
echo "🔍 Monitoring:"
echo "- Access logs: tail -f /var/log/nginx/datacharted-redirect.access.log"
echo "- Error logs: tail -f /var/log/nginx/datacharted-redirect.error.log"
echo "- Nginx status: systemctl status nginx"
echo ""
echo "✅ All done! Your domain redirect is now active."

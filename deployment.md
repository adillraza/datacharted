# DataCharted Deployment Guide

This guide covers deploying the DataCharted Flask application to production, including server setup, database configuration, and deployment automation.

## 🚀 Quick Start Deployment

### 1. Server Requirements

- **OS**: Ubuntu 20.04 LTS or newer
- **RAM**: Minimum 2GB (4GB recommended)
- **Storage**: 20GB minimum
- **CPU**: 2 cores minimum
- **Network**: Public IP with ports 80, 443, and 22 open

### 2. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# Create deployment user
sudo adduser datacharted
sudo usermod -aG sudo datacharted
sudo su - datacharted
```

### 3. Install Python and Dependencies

```bash
# Install Python 3.9+
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Nginx
sudo apt install -y nginx

# Install Redis (for future session management)
sudo apt install -y redis-server
```

## 🗄️ Database Setup

### 1. PostgreSQL Configuration

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE datacharted_app;
CREATE USER datacharted_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE datacharted_app TO datacharted_user;
ALTER USER datacharted_user CREATEDB;
\q

# Configure PostgreSQL for remote connections (if needed)
sudo nano /etc/postgresql/*/main/postgresql.conf
# Uncomment and modify: listen_addresses = '*'

sudo nano /etc/postgresql/*/main/pg_hba.conf
# Add: host datacharted_app datacharted_user 0.0.0.0/0 md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### 2. Database Initialization

```bash
# Clone repository
git clone <your-repo-url> /opt/datacharted
cd /opt/datacharted

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp env.example .env
nano .env

# Initialize database
flask init-db
```

## 🌐 Application Deployment

### 1. Application Configuration

```bash
# Create systemd service file
sudo nano /etc/systemd/system/datacharted.service
```

Add the following content:

```ini
[Unit]
Description=DataCharted Flask Application
After=network.target

[Service]
User=datacharted
Group=datacharted
WorkingDirectory=/opt/datacharted
Environment="PATH=/opt/datacharted/venv/bin"
Environment="FLASK_ENV=production"
Environment="DATABASE_URL=postgresql://datacharted_user:password@localhost/datacharted_app"
ExecStart=/opt/datacharted/venv/bin/gunicorn --workers 3 --bind unix:datacharted.sock -m 007 run:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Start Application Service

```bash
# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl start datacharted
sudo systemctl enable datacharted

# Check status
sudo systemctl status datacharted
```

### 3. Nginx Configuration

```bash
# Create Nginx site configuration
sudo nano /etc/nginx/sites-available/datacharted
```

Add the following content:

```nginx
server {
    listen 80;
    server_name app.datacharted.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/opt/datacharted/datacharted.sock;
    }

    location /static {
        alias /opt/datacharted/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
```

### 4. Enable Nginx Site

```bash
# Enable site and restart Nginx
sudo ln -s /etc/nginx/sites-available/datacharted /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 SSL Configuration

### 1. Install Certbot

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d app.datacharted.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### 2. Auto-renewal Setup

```bash
# Add to crontab
sudo crontab -e

# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring and Logging

### 1. Application Logs

```bash
# View application logs
sudo journalctl -u datacharted -f

# Log rotation
sudo nano /etc/logrotate.d/datacharted
```

### 2. Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

### 3. Database Monitoring

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Monitor database connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

## 🔄 Deployment Automation

### 1. Deployment Script

Create `/opt/datacharted/deploy.sh`:

```bash
#!/bin/bash

# Deployment script for DataCharted
set -e

echo "Starting deployment..."

# Pull latest changes
cd /opt/datacharted
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run database migrations
flask db upgrade

# Restart application
sudo systemctl restart datacharted

echo "Deployment completed successfully!"
```

### 2. Make Script Executable

```bash
chmod +x /opt/datacharted/deploy.sh
```

### 3. Automated Deployment with Webhook

```bash
# Install webhook handler
sudo apt install -y webhook

# Create webhook configuration
sudo nano /etc/webhook.conf
```

Add webhook configuration:

```json
[
  {
    "id": "deploy-datacharted",
    "execute-command": "/opt/datacharted/deploy.sh",
    "command-working-directory": "/opt/datacharted"
  }
]
```

## 🚨 Security Hardening

### 1. Firewall Configuration

```bash
# Install UFW
sudo apt install -y ufw

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. SSH Security

```bash
# Edit SSH configuration
sudo nano /etc/ssh/sshd_config

# Recommended settings:
# Port 22 (or change to non-standard port)
# PermitRootLogin no
# PasswordAuthentication no (use SSH keys)
# MaxAuthTries 3
# ClientAliveInterval 300
# ClientAliveCountMax 2

# Restart SSH
sudo systemctl restart sshd
```

### 3. Fail2ban Setup

```bash
# Install Fail2ban
sudo apt install -y fail2ban

# Configure for SSH and Nginx
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 📈 Performance Optimization

### 1. Gunicorn Optimization

```bash
# Optimize Gunicorn workers
# Number of workers = (2 x CPU cores) + 1
# For 2 CPU cores: 5 workers

# Update systemd service file
sudo nano /etc/systemd/system/datacharted.service

# Modify ExecStart line:
ExecStart=/opt/datacharted/venv/bin/gunicorn --workers 5 --worker-class gevent --bind unix:datacharted.sock -m 007 run:app
```

### 2. Nginx Optimization

```bash
# Edit Nginx configuration
sudo nano /etc/nginx/nginx.conf

# Add to http block:
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
```

### 3. Database Optimization

```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/*/main/postgresql.conf

# Recommended settings for 2GB RAM:
shared_buffers = 512MB
effective_cache_size = 1536MB
maintenance_work_mem = 128MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
```

## 🔍 Troubleshooting

### Common Issues

1. **Application won't start**
   - Check systemd logs: `sudo journalctl -u datacharted -f`
   - Verify environment variables in `.env`
   - Check database connectivity

2. **Nginx errors**
   - Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`
   - Verify socket file exists: `ls -la /opt/datacharted/datacharted.sock`
   - Check Nginx configuration: `sudo nginx -t`

3. **Database connection issues**
   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check connection string in `.env`
   - Verify database user permissions

### Health Checks

```bash
# Application health
curl -f http://localhost/api/health

# Database connectivity
sudo -u postgres psql -d datacharted_app -c "SELECT 1;"

# Nginx status
sudo systemctl status nginx
```

## 📚 Additional Resources

- [Flask Deployment Documentation](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [PostgreSQL Tuning](https://www.postgresql.org/docs/current/runtime-config-resource.html)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

## 🆘 Support

For deployment issues:
1. Check application logs
2. Verify configuration files
3. Test individual components
4. Contact support team

---

**Happy Deploying! 🚀**

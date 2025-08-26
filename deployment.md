# DataCharted Deployment Guide

## 🚀 **GitHub-Based Deployment (Recommended)**

### **Prerequisites:**
1. GitHub repository with your code
2. SSH access to your VPS (already configured)
3. GitHub Actions enabled

### **Step 1: GitHub Repository Setup**

1. **Create a new repository** on GitHub (e.g., `datacharted-app`)
2. **Push your code** to the repository:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/datacharted-app.git
   git branch -M main
   git push -u origin main
   ```

### **Step 2: Configure GitHub Secrets**

Go to your GitHub repository → Settings → Secrets and variables → Actions, and add:

- **`VPS_HOST`**: `165.232.38.9`
- **`VPS_USERNAME`**: `root`
- **`VPS_SSH_KEY`**: Your private SSH key content
- **`VPS_PORT`**: `22`

### **Step 3: GitHub Webhook (Alternative Method)**

If you prefer webhook-based deployment instead of GitHub Actions:

1. **Go to your repository** → Settings → Webhooks
2. **Add webhook**:
   - **Payload URL**: `http://app.datacharted.com:8080/api/webhook/deploy`
   - **Content type**: `application/json`
   - **Secret**: Generate a secure secret (e.g., `your-webhook-secret-123`)
   - **Events**: Select `Just the push event`

3. **Set environment variable** on your VPS:
   ```bash
   echo 'GITHUB_WEBHOOK_SECRET=your-webhook-secret-123' >> /opt/datacharted-app/.env
   systemctl restart datacharted
   ```

### **Step 4: Test Deployment**

1. **Make a change** to your code
2. **Commit and push**:
   ```bash
   git add .
   git commit -m "Test deployment"
   git push origin main
   ```
3. **Check deployment** in GitHub Actions or webhook logs

## 🔧 **Manual Deployment (Fallback)**

### **SCP Method:**
```bash
# Deploy specific files
scp app/api/routes.py root@165.232.38.9:/opt/datacharted-app/app/api/
scp config.py root@165.232.38.9:/opt/datacharted-app/

# Restart service
ssh root@165.232.38.9 "systemctl restart datacharted"
```

### **Full Deployment:**
```bash
# Deploy entire application
scp -r app/ root@165.232.38.9:/opt/datacharted-app/
scp config.py run.py requirements.txt root@165.232.38.9:/opt/datacharted-app/

# Update dependencies and restart
ssh root@165.232.38.9 "cd /opt/datacharted-app && source venv/bin/activate && pip install -r requirements.txt && systemctl restart datacharted"
```

## 📊 **Database Access**

### **PostgreSQL (Flask App):**
- **Adminer**: `http://165.232.38.9:8081/adminer.php`
- **Server**: `localhost`
- **Username**: `datacharted_user`
- **Password**: `datacharted_password`
- **Database**: `datacharted_db`

### **MariaDB (WordPress):**
- **phpMyAdmin**: `http://datacharted.com/phpmyadmin/`
- **Server**: `localhost`
- **Username**: `root` (or create new user)
- **Password**: Check server configuration

## 🔒 **Security Notes**

1. **Change default passwords** in production
2. **Use strong webhook secrets**
3. **Limit SSH access** to trusted IPs
4. **Regular security updates**
5. **Monitor logs** for suspicious activity

## 📝 **Troubleshooting**

### **API Endpoints Not Working:**
```bash
# Check service status
systemctl status datacharted

# Check logs
tail -f /var/log/datacharted/error.log

# Test locally
curl http://127.0.0.1:8000/api/health
```

### **Database Connection Issues:**
```bash
# Test PostgreSQL connection
PGPASSWORD=datacharted_password psql -h localhost -U datacharted_user -d datacharted_db

# Check PostgreSQL status
systemctl status postgresql
```

### **Deployment Failures:**
```bash
# Check deployment script
/opt/deploy/deploy.sh

# Check webhook logs
tail -f /var/log/datacharted/access.log
```

## 🎯 **Next Steps**

1. **Set up SSL certificates** for `app.datacharted.com`
2. **Configure domain** to point to port 8080 (remove `:8080` from URL)
3. **Set up monitoring** and logging
4. **Implement data source integrations** (Google Ads, Meta Ads, etc.)
5. **Add automated testing** to deployment pipeline

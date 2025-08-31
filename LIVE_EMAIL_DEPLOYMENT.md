# 🚀 Live Server Email Deployment Guide

## 📧 **Quick Setup for Live Server**

### **Step 1: Transfer Files to Server**

1. **Copy the setup script to your server:**
   ```bash
   scp -i ~/.ssh/github_actions_deploy_key setup_live_email.py root@165.232.38.9:/root/
   ```

2. **SSH into your server:**
   ```bash
   ssh -i ~/.ssh/github_actions_deploy_key root@165.232.38.9
   ```

### **Step 2: Run Email Setup Script**

1. **Navigate to your app directory:**
   ```bash
   cd /var/www/datacharted  # or wherever your app is located
   ```

2. **Run the email setup script:**
   ```bash
   python3 /root/setup_live_email.py
   ```

3. **The script will:**
   - ✅ Create/update your `.env` file
   - ✅ Add email configuration
   - ✅ Test the configuration
   - ✅ Provide next steps

### **Step 3: Restart Flask Service**

```bash
sudo systemctl restart datacharted
```

### **Step 4: Test Email Functionality**

1. **Test New User Registration:**
   - Go to `https://app.datacharted.com/auth/register`
   - Create a new account with a real email
   - Check inbox for welcome email from `support@datacharted.com`

2. **Test Password Reset:**
   - Go to `https://app.datacharted.com/auth/reset_password_request`
   - Enter your email address
   - Check inbox for password reset email with new password

## 🔧 **Manual Setup (Alternative)**

If you prefer to set up manually:

### **1. Create/Update .env File**
```bash
nano .env
```

### **2. Add Email Configuration**
```bash
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=support@datacharted.com
MAIL_PASSWORD=zzqh tfur yocr whhk
MAIL_DEFAULT_SENDER=support@datacharted.com
MAIL_MAX_EMAILS=10
```

### **3. Save and Exit**
- Press `Ctrl + X`
- Press `Y` to confirm
- Press `Enter` to save

## 🧪 **Testing Commands**

### **Test Email Configuration**
```bash
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print(f'Mail Server: {os.getenv(\"MAIL_SERVER\")}')
print(f'Mail Username: {os.getenv(\"MAIL_USERNAME\")}')
print(f'Mail Password: {\"✅ Set\" if os.getenv(\"MAIL_PASSWORD\") else \"❌ Not set\"}')
"
```

### **Test Flask App Loading**
```bash
python3 -c "
from app import create_app
from config import Config
app = create_app(Config)
print('✅ Flask app loaded successfully')
print(f'Mail Server: {app.config.get(\"MAIL_SERVER\")}')
"
```

## 📋 **What to Expect**

### **Welcome Email Features:**
- Professional DataCharted branding
- Platform features and benefits
- "Get Started Now" button
- Sent from: `support@datacharted.com`

### **Password Reset Email Features:**
- New secure password (12 characters)
- Security tips and recommendations
- Login link to your app
- Professional formatting

## 🚨 **Troubleshooting**

### **Common Issues:**

#### **1. "Module not found" errors**
```bash
# Install required packages
pip3 install python-dotenv Flask-Mail
```

#### **2. "Permission denied" errors**
```bash
# Check file permissions
ls -la .env
chmod 600 .env
```

#### **3. "Service restart failed"**
```bash
# Check service status
sudo systemctl status datacharted
# Check logs
sudo journalctl -u datacharted -f
```

#### **4. "Email not sending"**
```bash
# Check email configuration
python3 /root/setup_live_email.py
# Verify .env file
cat .env | grep MAIL
```

## ✅ **Verification Checklist**

- [ ] Setup script runs without errors
- [ ] `.env` file contains email configuration
- [ ] Flask service restarts successfully
- [ ] Welcome email sends on new user registration
- [ ] Password reset email sends on reset request
- [ ] Emails arrive in inbox (not spam)

## 🎯 **Success Indicators**

When everything is working correctly:
- ✅ New users receive welcome emails immediately
- ✅ Password reset requests generate new passwords
- ✅ All emails come from `support@datacharted.com`
- ✅ Professional branding in all emails
- ✅ No errors in Flask service logs

---

**Need Help?** Check the logs: `sudo journalctl -u datacharted -f`

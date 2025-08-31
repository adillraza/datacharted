# 🚀 DataCharted Deployment Guide

## 📧 **Email Configuration Protection**

Your server email configuration is preserved during deployments. Here's how it works:

### ✅ **What's Protected:**
- Email credentials in `.env` file
- Gmail app password for `support@datacharted.com`
- All email settings (MAIL_SERVER, MAIL_PORT, etc.)

### 🔧 **Safe Deployment Process:**

1. **Automatic GitHub Actions Deployment (Preferred):**
   ```bash
   # Your normal workflow - GitHub Actions handles everything automatically!
   git add .
   git commit -m "Your changes"
   git push origin main
   
   # That's it! GitHub Actions will:
   # ✅ Deploy to server automatically
   # ✅ Preserve email configuration  
   # ✅ Backup database before migration
   # ✅ Run database migrations safely
   # ✅ Verify migration success
   # ✅ Restart the service
   # ✅ Verify service health
   ```

2. **Manual Server Deployment (Emergency Only):**
   ```bash
   # Only use this if GitHub Actions fails
   ssh root@165.232.38.9
   cd /opt/datacharted-app
   bash deploy_server.sh
   ```

### 🛡️ **Protection Mechanisms:**

1. **`.env` file is in `.gitignore`** - Never gets overwritten by git
2. **Backup system** - Each deployment backs up current `.env`
3. **Auto-restore** - Deployment script checks and restores email config if missing

### 🗄️ **Database Migration Protection:**

1. **Automatic backup** - Database is backed up before every migration
2. **Migration verification** - Shows before/after migration status  
3. **Error handling** - Deployment stops if migration fails
4. **Service verification** - Confirms service starts after migration
5. **Rollback capability** - Can restore from backup if needed

### 📁 **File Structure:**
```
/opt/datacharted-app/
├── .env                    # Email credentials (preserved)
├── .env.backup.*          # Automatic .env backups
├── app_dev.db             # Single database file (absolute path)
├── app_dev.db.backup.*    # Automatic database backups
├── deploy_server.sh       # Safe deployment script
└── setup_live_email.py    # Email config restoration
```

### 🧪 **Testing After Deployment:**

After any deployment, test:
1. **User Registration** - Should send welcome emails
2. **Password Reset** - Should send reset emails
3. **No Internal Errors** - All functionality intact

### 🚨 **If Email Breaks:**

If email stops working after a deployment:
```bash
# SSH into server
ssh root@165.232.38.9
cd /opt/datacharted-app

# Restore email configuration
python3 setup_live_email.py

# Restart service
systemctl restart datacharted

# Test email functionality
```

### ✅ **Deployment Checklist:**

- [ ] Code changes committed and pushed
- [ ] Email configuration intact
- [ ] Database backup created automatically
- [ ] Database migrations applied successfully
- [ ] Service restarted successfully
- [ ] Registration and password reset working
- [ ] Welcome emails being sent
- [ ] No internal server errors

---

## 🎯 **The Bottom Line:**

Your email configuration is now **deployment-proof**. You can safely make changes locally and push to GitHub without worrying about breaking email functionality! 🎉

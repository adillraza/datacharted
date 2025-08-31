# 🚀 DataCharted Domain Redirect Deployment Instructions

## 📋 **Complete Deployment Checklist**

This guide walks you through the complete process of redirecting `datacharted.com` to `app.datacharted.com`.

## 🎯 **Pre-Deployment Checklist**

- [ ] **Backup WordPress site** (if you want to keep it)
- [ ] **Verify app.datacharted.com is working** properly
- [ ] **Have SSH access** to VPS (`ssh root@165.232.38.9`)
- [ ] **Domain registrar access** for DNS changes
- [ ] **Plan deployment time** (off-peak hours recommended)

## 📅 **Deployment Timeline**

| Phase | Duration | Description |
|-------|----------|-------------|
| Phase 1 | 10 minutes | Server configuration |
| Phase 2 | 5 minutes | DNS updates |
| Phase 3 | 5-60 minutes | DNS propagation |
| Phase 4 | 5 minutes | Testing & verification |
| **Total** | **25-80 minutes** | Complete deployment |

## 🔧 **Phase 1: Server Configuration (10 minutes)**

### **Step 1.1: Connect to VPS**
```bash
ssh root@165.232.38.9
```

### **Step 1.2: Download Setup Script**
```bash
# Download the setup script from your local machine
# Option A: Copy from local machine
scp /Users/pmru/datacharted/setup_domain_redirect.sh root@165.232.38.9:/root/

# Option B: Create directly on server
nano /root/setup_domain_redirect.sh
# Copy the contents from setup_domain_redirect.sh file
```

### **Step 1.3: Make Script Executable**
```bash
chmod +x /root/setup_domain_redirect.sh
```

### **Step 1.4: Run Setup Script**
```bash
cd /root
./setup_domain_redirect.sh
```

**Expected Output:**
```
🔄 DataCharted Domain Redirect Setup
====================================

📋 Step 1: Installing Nginx...
✅ Nginx installed successfully

📋 Step 2: Creating redirect configuration...
✅ Configuration file created: /etc/nginx/sites-available/datacharted-redirect

📋 Step 3: Enabling the configuration...
✅ Configuration enabled

📋 Step 4: Testing nginx configuration...
✅ Nginx configuration is valid

📋 Step 5: Starting/restarting nginx...
✅ All done! Your domain redirect is now active.
```

### **Step 1.5: Verify Nginx Status**
```bash
systemctl status nginx
nginx -t
```

## 🌐 **Phase 2: DNS Configuration (5 minutes)**

### **Step 2.1: Access Domain Registrar**
Log into your domain registrar where `datacharted.com` is managed.

### **Step 2.2: Update DNS Records**
**Add these A records:**

| Type | Name/Host | Value | TTL |
|------|-----------|-------|-----|
| A    | @         | 165.232.38.9 | 300 |
| A    | www       | 165.232.38.9 | 300 |

### **Step 2.3: Remove Old Records**
Delete any existing A records or CNAME records for:
- `@` (root domain)
- `www`

### **Step 2.4: Verify app Subdomain**
Ensure this record exists and is correct:

| Type | Name/Host | Value | TTL |
|------|-----------|-------|-----|
| A    | app       | 165.232.38.9 | 300 |

## ⏱️ **Phase 3: DNS Propagation (5-60 minutes)**

### **Step 3.1: Monitor Propagation**
Use these tools to check DNS propagation:

**Online Tools:**
- https://www.whatsmydns.net/
- https://dnschecker.org/

**Command Line:**
```bash
# Test from your local machine
nslookup datacharted.com
nslookup www.datacharted.com

# Test from different DNS servers
nslookup datacharted.com 8.8.8.8
nslookup datacharted.com 1.1.1.1
```

### **Step 3.2: Expected Results**
You should see:
```
datacharted.com.        300     IN      A       165.232.38.9
www.datacharted.com.    300     IN      A       165.232.38.9
```

### **Step 3.3: Wait for Full Propagation**
- **Minimum wait:** 5 minutes
- **Typical wait:** 15-30 minutes  
- **Maximum wait:** 60 minutes

## 🧪 **Phase 4: Testing & Verification (5 minutes)**

### **Step 4.1: Test HTTP Redirect**
```bash
# Test root domain redirect
curl -I http://datacharted.com

# Expected response:
# HTTP/1.1 301 Moved Permanently
# Location: https://app.datacharted.com/

# Test www subdomain redirect
curl -I http://www.datacharted.com

# Expected response:
# HTTP/1.1 301 Moved Permanently  
# Location: https://app.datacharted.com/
```

### **Step 4.2: Test Browser Access**
1. **Open browser** and go to `http://datacharted.com`
2. **Verify redirect** to `https://app.datacharted.com`
3. **Test www version:** `http://www.datacharted.com`
4. **Check URL preservation:** Try `http://datacharted.com/some/path`

### **Step 4.3: Test Path Preservation**
```bash
# Test that URL paths are preserved
curl -I http://datacharted.com/test/path

# Expected response:
# HTTP/1.1 301 Moved Permanently
# Location: https://app.datacharted.com/test/path
```

### **Step 4.4: Monitor Logs**
```bash
# On your VPS, monitor redirect logs
tail -f /var/log/nginx/datacharted-redirect.access.log
tail -f /var/log/nginx/datacharted-redirect.error.log
```

## 🔒 **Optional: SSL Certificate Setup**

If you want HTTPS support for `datacharted.com` (recommended):

### **Step 5.1: Install Certbot**
```bash
apt install certbot python3-certbot-nginx -y
```

### **Step 5.2: Get SSL Certificate**
```bash
certbot --nginx -d datacharted.com -d www.datacharted.com
```

### **Step 5.3: Test SSL Redirect**
```bash
curl -I https://datacharted.com

# Expected response:
# HTTP/2 301
# Location: https://app.datacharted.com/
```

## 📊 **Monitoring & Maintenance**

### **Log Files to Monitor**
```bash
# Access logs (successful redirects)
tail -f /var/log/nginx/datacharted-redirect.access.log

# Error logs (any issues)
tail -f /var/log/nginx/datacharted-redirect.error.log

# Nginx service status
systemctl status nginx
```

### **Regular Checks**
- **Weekly:** Check redirect is working
- **Monthly:** Review access logs for traffic patterns
- **Quarterly:** Renew SSL certificates (auto-renewal should handle this)

## 🚨 **Troubleshooting**

### **Common Issues & Solutions**

**Issue: DNS not propagating**
```bash
# Solution: Clear local DNS cache
sudo dscacheutil -flushcache  # macOS
sudo systemctl restart systemd-resolved  # Ubuntu
```

**Issue: Nginx not starting**
```bash
# Check configuration
nginx -t

# Check logs
journalctl -u nginx -f

# Restart service
systemctl restart nginx
```

**Issue: Redirect not working**
```bash
# Check nginx configuration
cat /etc/nginx/sites-enabled/datacharted-redirect

# Test configuration
nginx -t

# Check if site is enabled
ls -la /etc/nginx/sites-enabled/
```

**Issue: SSL certificate problems**
```bash
# Check certificate status
certbot certificates

# Renew certificates
certbot renew --dry-run
```

## 🔄 **Rollback Plan**

If you need to rollback:

### **Step 1: Revert DNS**
1. Change A records back to original WordPress hosting IP
2. Wait for DNS propagation (5-60 minutes)

### **Step 2: Disable Nginx Redirect**
```bash
# Disable the redirect site
rm /etc/nginx/sites-enabled/datacharted-redirect

# Restart nginx
systemctl restart nginx
```

## ✅ **Post-Deployment Checklist**

- [ ] `http://datacharted.com` redirects to `https://app.datacharted.com`
- [ ] `http://www.datacharted.com` redirects to `https://app.datacharted.com`
- [ ] URL paths are preserved in redirects
- [ ] `https://app.datacharted.com` still works normally
- [ ] DNS propagation is complete globally
- [ ] SSL certificates are working (if configured)
- [ ] Nginx logs show successful redirects
- [ ] No error logs in nginx
- [ ] WordPress site is no longer accessible (expected)

## 🎉 **Success Indicators**

**You'll know the deployment is successful when:**

1. **Browser test:** Typing `datacharted.com` takes you to `app.datacharted.com`
2. **URL bar:** Shows `app.datacharted.com` after redirect
3. **HTTP status:** `curl -I http://datacharted.com` returns `301 Moved Permanently`
4. **Logs:** Nginx access logs show redirect requests
5. **Global access:** Users worldwide can access via main domain

## 📞 **Support**

If you encounter issues:

1. **Check logs:** Review nginx error logs
2. **Verify DNS:** Use online DNS checkers
3. **Test configuration:** Run `nginx -t`
4. **Monitor propagation:** Wait for full DNS propagation

---

**🎯 Estimated Total Time: 25-80 minutes (depending on DNS propagation)**

**🚀 Ready to deploy? Start with Phase 1!**

# 🔄 DataCharted Domain Redirect - Complete Setup

## 🎯 **Overview**

This setup redirects all traffic from `datacharted.com` to `app.datacharted.com`, consolidating both domains to point to your Flask application. Your WordPress site will be replaced with automatic redirects.

## 📁 **Files Created**

| File | Purpose |
|------|---------|
| `domain_redirect_setup.md` | Complete guide with all redirect options |
| `nginx_redirect_config.conf` | Nginx configuration for redirects |
| `setup_domain_redirect.sh` | Automated server setup script |
| `dns_configuration_guide.md` | DNS record configuration instructions |
| `deployment_instructions.md` | Step-by-step deployment guide |
| `test_redirect.sh` | Comprehensive testing script |

## 🚀 **Quick Start (3 Steps)**

### **Step 1: Server Setup (10 minutes)**
```bash
# SSH into your VPS
ssh root@165.232.38.9

# Copy and run the setup script
scp /Users/pmru/datacharted/setup_domain_redirect.sh root@165.232.38.9:/root/
ssh root@165.232.38.9 "chmod +x /root/setup_domain_redirect.sh && /root/setup_domain_redirect.sh"
```

### **Step 2: DNS Configuration (5 minutes)**
In your domain registrar, add these A records:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 165.232.38.9 | 300 |
| A | www | 165.232.38.9 | 300 |

### **Step 3: Test & Verify (5 minutes)**
```bash
# Run the test script
./test_redirect.sh

# Or test manually
curl -I http://datacharted.com
# Should return: 301 redirect to https://app.datacharted.com
```

## 📋 **What This Setup Does**

### **Before:**
- `datacharted.com` → WordPress site
- `app.datacharted.com` → Flask application

### **After:**
- `datacharted.com` → **Redirects to** `app.datacharted.com`
- `www.datacharted.com` → **Redirects to** `app.datacharted.com`
- `app.datacharted.com` → Flask application (unchanged)

## ✅ **Benefits**

- **SEO-Friendly**: 301 redirects preserve search rankings
- **User-Friendly**: Main domain now works for your app
- **Path Preservation**: `datacharted.com/page` → `app.datacharted.com/page`
- **Professional**: Clean, unified domain structure
- **Automatic**: No manual intervention needed

## 🔧 **Technical Details**

### **Redirect Method**
- **Type**: HTTP 301 (Permanent Redirect)
- **Server**: Nginx on VPS (165.232.38.9)
- **Preserves**: URL paths, query parameters
- **SSL**: Optional (can be added with Let's Encrypt)

### **Infrastructure**
- **VPS**: 165.232.38.9 (DigitalOcean)
- **Web Server**: Nginx (for redirects)
- **App Server**: Flask (unchanged)
- **DNS**: A records pointing to VPS

## 📊 **Monitoring**

### **Log Files**
```bash
# Access logs (successful redirects)
tail -f /var/log/nginx/datacharted-redirect.access.log

# Error logs (any issues)  
tail -f /var/log/nginx/datacharted-redirect.error.log
```

### **Health Checks**
```bash
# Test redirect is working
curl -I http://datacharted.com

# Check nginx status
systemctl status nginx

# Verify DNS resolution
nslookup datacharted.com
```

## 🚨 **Troubleshooting**

### **Common Issues**

**DNS not propagating:**
- Wait 5-60 minutes for global propagation
- Check with: https://www.whatsmydns.net/
- Clear local DNS cache

**Redirect not working:**
- Check nginx config: `nginx -t`
- Restart nginx: `systemctl restart nginx`
- Verify DNS points to correct IP

**SSL certificate errors:**
- Set up Let's Encrypt: `certbot --nginx -d datacharted.com -d www.datacharted.com`

## 🔄 **Rollback Plan**

If you need to revert:

1. **DNS**: Change A records back to WordPress hosting IP
2. **Server**: Disable nginx redirect: `rm /etc/nginx/sites-enabled/datacharted-redirect`
3. **Wait**: 5-60 minutes for DNS propagation

## 📞 **Support Commands**

```bash
# Check if redirect is working
curl -I http://datacharted.com

# Test DNS resolution
nslookup datacharted.com

# Check nginx configuration
nginx -t

# View recent redirect activity
tail -20 /var/log/nginx/datacharted-redirect.access.log

# Check nginx service status
systemctl status nginx
```

## 🎉 **Success Criteria**

Your setup is successful when:

- ✅ `http://datacharted.com` redirects to `https://app.datacharted.com`
- ✅ `http://www.datacharted.com` redirects to `https://app.datacharted.com`
- ✅ URL paths are preserved (e.g., `/page` → `/page`)
- ✅ `https://app.datacharted.com` still works normally
- ✅ DNS resolves correctly worldwide
- ✅ No errors in nginx logs

## 📅 **Timeline**

| Task | Duration |
|------|----------|
| Server setup | 10 minutes |
| DNS changes | 5 minutes |
| DNS propagation | 5-60 minutes |
| Testing | 5 minutes |
| **Total** | **25-80 minutes** |

## 🔗 **Related Files**

- **Detailed Guide**: `domain_redirect_setup.md`
- **DNS Instructions**: `dns_configuration_guide.md`
- **Deployment Steps**: `deployment_instructions.md`
- **Testing Script**: `test_redirect.sh`
- **Nginx Config**: `nginx_redirect_config.conf`
- **Setup Script**: `setup_domain_redirect.sh`

---

**🚀 Ready to deploy? Start with the Quick Start section above!**

**📧 Questions? Check the troubleshooting section or review the detailed guides.**

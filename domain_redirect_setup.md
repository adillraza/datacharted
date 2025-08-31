# 🔄 DataCharted Domain Redirect Setup Guide

## 🎯 **Objective**
Redirect all traffic from `datacharted.com` to `app.datacharted.com` to consolidate both domains to point to the same Flask application.

## 📋 **Current Setup Analysis**
- **app.datacharted.com**: Flask app on VPS `165.232.38.9:8080`
- **datacharted.com**: WordPress site (to be replaced with redirect)
- **Target**: All traffic → `app.datacharted.com`

## 🚀 **Implementation Options**

### **Option 1: DNS-Level Redirect (Recommended)**

#### **Step 1: Update DNS Records**
In your domain registrar's DNS management panel:

1. **Remove existing A records for `datacharted.com`**
2. **Add CNAME record:**
   ```
   Type: CNAME
   Name: @ (or leave blank for root domain)
   Value: app.datacharted.com
   TTL: 300 (5 minutes)
   ```

3. **Add CNAME for www subdomain:**
   ```
   Type: CNAME
   Name: www
   Value: app.datacharted.com
   TTL: 300
   ```

#### **Pros:**
- ✅ Simple and fast
- ✅ No server configuration needed
- ✅ Automatic SSL certificate sharing
- ✅ No additional server resources

#### **Cons:**
- ❌ URL doesn't change in browser (shows datacharted.com)
- ❌ Some DNS providers don't support CNAME for root domain

---

### **Option 2: HTTP Redirect via Nginx (Most Flexible)**

#### **Step 1: Install Nginx on VPS**
```bash
ssh root@165.232.38.9
apt update
apt install nginx -y
systemctl enable nginx
systemctl start nginx
```

#### **Step 2: Create Nginx Configuration**
```bash
nano /etc/nginx/sites-available/datacharted-redirect
```

**Add this configuration:**
```nginx
# Redirect datacharted.com to app.datacharted.com
server {
    listen 80;
    listen [::]:80;
    server_name datacharted.com www.datacharted.com;
    
    # Permanent redirect (301) to app.datacharted.com
    return 301 https://app.datacharted.com$request_uri;
}

# SSL redirect (if you have SSL certificates)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name datacharted.com www.datacharted.com;
    
    # SSL certificate paths (update these)
    ssl_certificate /path/to/datacharted.com.crt;
    ssl_certificate_key /path/to/datacharted.com.key;
    
    # Permanent redirect (301) to app.datacharted.com
    return 301 https://app.datacharted.com$request_uri;
}
```

#### **Step 3: Enable the Configuration**
```bash
ln -s /etc/nginx/sites-available/datacharted-redirect /etc/nginx/sites-enabled/
nginx -t  # Test configuration
systemctl reload nginx
```

#### **Step 4: Update DNS Records**
Point `datacharted.com` A record to your VPS:
```
Type: A
Name: @ (root domain)
Value: 165.232.38.9
TTL: 300
```

```
Type: A
Name: www
Value: 165.232.38.9
TTL: 300
```

#### **Pros:**
- ✅ True HTTP redirect (URL changes in browser)
- ✅ SEO-friendly 301 redirects
- ✅ Preserves URL paths and parameters
- ✅ Can handle SSL certificates separately
- ✅ Full control over redirect behavior

---

### **Option 3: Simple HTML Redirect Page**

#### **Step 1: Create Redirect HTML File**
```bash
ssh root@165.232.38.9
mkdir -p /var/www/datacharted-redirect
```

#### **Step 2: Create index.html**
```bash
nano /var/www/datacharted-redirect/index.html
```

**Add this content:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redirecting to DataCharted App...</title>
    <meta http-equiv="refresh" content="0; url=https://app.datacharted.com">
    <link rel="canonical" href="https://app.datacharted.com">
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
            padding: 2rem;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        .spinner {
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top: 3px solid white;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        a {
            color: white;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 DataCharted</h1>
        <div class="spinner"></div>
        <p>Redirecting you to our app...</p>
        <p><a href="https://app.datacharted.com">Click here if you're not redirected automatically</a></p>
    </div>
    
    <script>
        // JavaScript redirect as backup
        setTimeout(function() {
            window.location.href = 'https://app.datacharted.com';
        }, 1000);
    </script>
</body>
</html>
```

#### **Step 3: Configure Web Server**
If using Apache (typical for WordPress):
```bash
# Update Apache virtual host or .htaccess
nano /var/www/html/.htaccess
```

Add:
```apache
RewriteEngine On
RewriteCond %{HTTP_HOST} ^(www\.)?datacharted\.com$ [NC]
RewriteRule ^(.*)$ https://app.datacharted.com/$1 [R=301,L]
```

---

## 🎯 **Recommended Approach**

**I recommend Option 2 (Nginx HTTP Redirect)** because:

1. **SEO Benefits**: Proper 301 redirects preserve search engine rankings
2. **User Experience**: Clear URL change shows users they're on the app
3. **Flexibility**: Can handle complex redirect rules if needed
4. **Professional**: Industry standard approach
5. **Preserves Paths**: `/some/page` on main site redirects to `/some/page` on app

## 📋 **Implementation Steps**

### **Phase 1: Prepare Server**
1. SSH into your VPS: `ssh root@165.232.38.9`
2. Install Nginx: `apt update && apt install nginx -y`
3. Create redirect configuration
4. Test configuration: `nginx -t`

### **Phase 2: Update DNS**
1. Log into your domain registrar
2. Update A records for `datacharted.com` and `www.datacharted.com`
3. Point both to `165.232.38.9`
4. Wait for DNS propagation (5-60 minutes)

### **Phase 3: Test & Verify**
1. Test redirect: `curl -I http://datacharted.com`
2. Verify in browser: Visit `datacharted.com`
3. Check SSL certificates work
4. Test various URL paths

## 🔒 **SSL Certificate Considerations**

If you need SSL for `datacharted.com`, you can:

1. **Use Let's Encrypt (Free):**
   ```bash
   apt install certbot python3-certbot-nginx -y
   certbot --nginx -d datacharted.com -d www.datacharted.com
   ```

2. **Use existing certificates** if you have them

## 🧪 **Testing Commands**

```bash
# Test HTTP redirect
curl -I http://datacharted.com

# Test HTTPS redirect  
curl -I https://datacharted.com

# Test with path preservation
curl -I http://datacharted.com/some/path

# Check DNS propagation
nslookup datacharted.com
dig datacharted.com
```

## 📞 **Next Steps**

1. **Choose your preferred option** (I recommend Option 2)
2. **Backup your current WordPress site** (if needed)
3. **Follow the implementation steps**
4. **Test thoroughly before going live**
5. **Monitor for any issues after deployment**

Would you like me to help you implement any of these options?

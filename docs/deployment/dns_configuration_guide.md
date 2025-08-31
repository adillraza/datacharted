# 🌐 DNS Configuration Guide for DataCharted Domain Redirect

## 🎯 **Objective**
Configure DNS records to point `datacharted.com` and `www.datacharted.com` to your VPS server where the redirect will be handled.

## 📋 **Required DNS Changes**

### **Current Setup (Before Changes)**
- `app.datacharted.com` → Points to `165.232.38.9` (VPS)
- `datacharted.com` → Points to WordPress hosting

### **New Setup (After Changes)**
- `app.datacharted.com` → Points to `165.232.38.9` (VPS) - **No change**
- `datacharted.com` → Points to `165.232.38.9` (VPS) - **NEW**
- `www.datacharted.com` → Points to `165.232.38.9` (VPS) - **NEW**

## 🔧 **DNS Record Configuration**

### **Step 1: Access Your Domain Registrar**
Log into your domain registrar's control panel where you manage DNS for `datacharted.com`.

Common registrars:
- GoDaddy
- Namecheap  
- Cloudflare
- Google Domains
- Route 53 (AWS)

### **Step 2: Update A Records**

**Add/Update these DNS records:**

| Type | Name/Host | Value/Points To | TTL |
|------|-----------|----------------|-----|
| A    | @         | 165.232.38.9   | 300 |
| A    | www       | 165.232.38.9   | 300 |

**Explanation:**
- `@` represents the root domain (`datacharted.com`)
- `www` represents the www subdomain (`www.datacharted.com`)
- `165.232.38.9` is your VPS IP address
- `300` seconds (5 minutes) TTL for quick propagation

### **Step 3: Remove Old Records**
**Delete these existing records (if they exist):**
- Any A records pointing to old WordPress hosting
- Any CNAME records for the root domain
- Any conflicting records for `www`

### **Step 4: Verify Current app.datacharted.com**
**Ensure this record remains unchanged:**

| Type | Name/Host | Value/Points To | TTL |
|------|-----------|----------------|-----|
| A    | app       | 165.232.38.9   | 300 |

## 📱 **Platform-Specific Instructions**

### **Cloudflare**
1. Go to **DNS** tab in Cloudflare dashboard
2. **Add A record:**
   - Type: `A`
   - Name: `@`
   - IPv4 address: `165.232.38.9`
   - Proxy status: 🟠 (DNS only, not proxied)
   - TTL: `Auto`

3. **Add A record for www:**
   - Type: `A` 
   - Name: `www`
   - IPv4 address: `165.232.38.9`
   - Proxy status: 🟠 (DNS only, not proxied)
   - TTL: `Auto`

### **GoDaddy**
1. Go to **DNS Management** in your GoDaddy account
2. **Add A record:**
   - Type: `A`
   - Host: `@`
   - Points to: `165.232.38.9`
   - TTL: `1 Hour`

3. **Add A record for www:**
   - Type: `A`
   - Host: `www` 
   - Points to: `165.232.38.9`
   - TTL: `1 Hour`

### **Namecheap**
1. Go to **Advanced DNS** tab
2. **Add A Record:**
   - Type: `A Record`
   - Host: `@`
   - Value: `165.232.38.9`
   - TTL: `Automatic`

3. **Add A Record for www:**
   - Type: `A Record`
   - Host: `www`
   - Value: `165.232.38.9` 
   - TTL: `Automatic`

### **Google Domains**
1. Go to **DNS** section
2. **Add custom record:**
   - Type: `A`
   - Name: Leave blank (for root domain)
   - Data: `165.232.38.9`
   - TTL: `300`

3. **Add custom record for www:**
   - Type: `A`
   - Name: `www`
   - Data: `165.232.38.9`
   - TTL: `300`

## ⏱️ **DNS Propagation Timeline**

| Timeframe | What to Expect |
|-----------|----------------|
| 0-5 minutes | Changes saved in DNS provider |
| 5-30 minutes | Most users see changes |
| 30-60 minutes | Global propagation complete |
| Up to 24 hours | Maximum propagation time |

## 🧪 **Testing DNS Changes**

### **Command Line Tests**
```bash
# Test root domain
nslookup datacharted.com
dig datacharted.com

# Test www subdomain  
nslookup www.datacharted.com
dig www.datacharted.com

# Test from different DNS servers
nslookup datacharted.com 8.8.8.8
nslookup datacharted.com 1.1.1.1
```

### **Online DNS Checkers**
- https://www.whatsmydns.net/
- https://dnschecker.org/
- https://www.dnswatch.info/

### **Expected Results**
Both commands should return:
```
datacharted.com.    300    IN    A    165.232.38.9
www.datacharted.com.    300    IN    A    165.232.38.9
```

## 🚨 **Important Notes**

### **Before Making Changes**
1. **Backup current DNS settings** (screenshot or export)
2. **Note current WordPress hosting details** (in case rollback needed)
3. **Inform users** of potential brief downtime
4. **Plan for off-peak hours** if possible

### **After Making Changes**
1. **Monitor DNS propagation** using online tools
2. **Test from multiple locations** and devices
3. **Check both HTTP and HTTPS** access
4. **Verify redirect works correctly**

### **Rollback Plan**
If something goes wrong:
1. **Revert A records** to original WordPress hosting IP
2. **Wait for DNS propagation** (5-60 minutes)
3. **Test WordPress site** is accessible again

## 📞 **Troubleshooting**

### **Common Issues**

**DNS not propagating:**
- Lower TTL to 300 seconds
- Clear local DNS cache: `sudo dscacheutil -flushcache` (macOS)
- Try different DNS servers (8.8.8.8, 1.1.1.1)

**Mixed results:**
- Some locations see old IP, others see new
- This is normal during propagation
- Wait 30-60 minutes for full propagation

**SSL certificate errors:**
- Set up SSL certificates after DNS propagation
- Use Let's Encrypt: `certbot --nginx -d datacharted.com -d www.datacharted.com`

## ✅ **Verification Checklist**

- [ ] A record for `@` points to `165.232.38.9`
- [ ] A record for `www` points to `165.232.38.9`  
- [ ] A record for `app` still points to `165.232.38.9`
- [ ] Old WordPress hosting records removed
- [ ] DNS propagation complete (check online tools)
- [ ] `nslookup datacharted.com` returns correct IP
- [ ] `nslookup www.datacharted.com` returns correct IP
- [ ] Ready to test redirect functionality

## 🎯 **Next Steps**

After DNS propagation is complete:
1. **Deploy nginx redirect configuration** on VPS
2. **Test redirect functionality**
3. **Set up SSL certificates** (optional)
4. **Monitor logs** for any issues

---

**⚠️ Remember:** DNS changes can take up to 24 hours to fully propagate worldwide, but most users will see changes within 30 minutes.

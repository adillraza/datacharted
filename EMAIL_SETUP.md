# 📧 DataCharted Email System Setup Guide

## 🎯 Overview

DataCharted now includes a comprehensive email system that automatically sends:
- **Welcome emails** when users sign up
- **Password reset emails** when users request password resets

All emails are sent from `support@datacharted.com` using professional, branded templates.

## 🚀 Quick Setup

### 1. Email Provider Configuration

#### Option A: Gmail (Recommended for Development)
1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account Settings → Security
   - Click "App passwords" under 2-Step Verification
   - Generate a password for "Mail"
   - Copy the 16-character password

3. **Update your `.env` file**:
```bash
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=support@datacharted.com
MAIL_PASSWORD=your_16_character_app_password
MAIL_DEFAULT_SENDER=support@datacharted.com
MAIL_MAX_EMAILS=10
```

#### Option B: Custom SMTP Server
```bash
# Email Configuration
MAIL_SERVER=your_smtp_server.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=your_username
MAIL_PASSWORD=your_password
MAIL_DEFAULT_SENDER=support@datacharted.com
MAIL_MAX_EMAILS=10
```

### 2. Domain Email Setup (Production)

For production use, we recommend setting up a proper domain email:

1. **Domain Email Provider** (e.g., Google Workspace, Microsoft 365, or custom SMTP)
2. **Create email account**: `support@datacharted.com`
3. **Configure SMTP settings** in your `.env` file
4. **Set up SPF, DKIM, and DMARC** records for better deliverability

## 📧 Email Templates

### Welcome Email Template
- **File**: `app/templates/emails/welcome.html` / `welcome.txt`
- **Triggered**: When a new user registers
- **Content**: Welcome message, platform features, next steps
- **CTA**: "Get Started Now" button linking to login

### Password Reset Email Template
- **File**: `app/templates/emails/password_reset.html` / `password_reset.txt`
- **Triggered**: When user requests password reset
- **Content**: New password, security tips, login link
- **Security**: Includes security recommendations

## 🔧 Technical Implementation

### Email Utility Functions
```python
# app/email_utils.py
from app.email_utils import send_welcome_email, send_password_reset_email

# Send welcome email
send_welcome_email(user)

# Send password reset email
new_password = generate_random_password()
send_password_reset_email(user, new_password)
```

### Configuration
```python
# config.py
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'support@datacharted.com'
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = 'support@datacharted.com'
```

### Integration Points
- **Registration**: `app/auth/routes.py` - `register()` function
- **Password Reset**: `app/auth/routes.py` - `reset_password_request()` function

## 🧪 Testing

### Local Testing
1. **Set up email credentials** in `.env`
2. **Register a new user** - should receive welcome email
3. **Request password reset** - should receive reset email

### Test Command
```bash
python test_email.py
```

## 📊 Email Features

### ✅ What's Included
- **Professional HTML templates** with DataCharted branding
- **Plain text fallbacks** for email clients that don't support HTML
- **Responsive design** that works on all devices
- **Error handling** - emails won't break user registration
- **Logging** for debugging email issues
- **Configurable settings** for different environments

### 🎨 Template Design
- **Brand colors**: DataCharted teal (#00B4D8) and blue (#0077B6)
- **Professional layout** with proper spacing and typography
- **Call-to-action buttons** for better user engagement
- **Mobile-responsive** design
- **Accessibility** considerations

## 🚨 Troubleshooting

### Common Issues

#### 1. "Authentication failed" Error
- **Cause**: Incorrect email password or 2FA not enabled
- **Solution**: Generate new app password and update `.env`

#### 2. "Connection refused" Error
- **Cause**: Wrong SMTP server or port
- **Solution**: Verify SMTP settings with your email provider

#### 3. Emails not sending
- **Cause**: Missing environment variables
- **Solution**: Check all email settings in `.env`

#### 4. Emails going to spam
- **Cause**: Missing SPF/DKIM records
- **Solution**: Set up proper DNS records for your domain

### Debug Commands
```bash
# Check email configuration
python -c "
from app import create_app
from config import Config
app = create_app(Config)
print(f'Mail Server: {app.config.get(\"MAIL_SERVER\")}')
print(f'Mail Username: {app.config.get(\"MAIL_USERNAME\")}')
print(f'Mail Password: {\"Set\" if app.config.get(\"MAIL_PASSWORD\") else \"Not set\"}')
"
```

## 🔒 Security Considerations

### Password Reset Security
- **Random passwords** generated using `secrets` module
- **Immediate password change** recommended after login
- **Security tips** included in reset emails
- **Rate limiting** can be added to prevent abuse

### Email Security
- **TLS encryption** for all email transmission
- **No sensitive data** in email content
- **Professional sender** address for trust
- **Clear unsubscribe** information

## 📈 Future Enhancements

### Planned Features
- **Email verification** for new accounts
- **Newsletter subscriptions** for updates
- **Transactional emails** for platform events
- **Email analytics** and delivery tracking
- **Template customization** for different user types

### Integration Opportunities
- **Marketing automation** platforms
- **Customer support** systems
- **Analytics tools** for email performance
- **A/B testing** for email templates

## 📞 Support

If you encounter any issues with the email system:

1. **Check the logs** for error messages
2. **Verify email configuration** in `.env`
3. **Test with the test script** (`python test_email.py`)
4. **Contact support** at support@datacharted.com

---

**Last Updated**: August 26, 2025  
**Version**: 1.0  
**Maintainer**: DataCharted Development Team

#!/usr/bin/env python3
"""
Setup script for DataCharted email system on live server
Run this on your live server to configure email settings
"""

import os
import sys

def setup_email_config():
    """Set up email configuration on live server"""
    print("📧 Setting up DataCharted Email System on Live Server")
    print("=" * 60)
    
    # Email configuration
    email_config = """# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=support@datacharted.com
MAIL_PASSWORD=zzqh tfur yocr whhk
MAIL_DEFAULT_SENDER=support@datacharted.com
MAIL_MAX_EMAILS=10
"""
    
    # Check if .env exists
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"✅ Found existing .env file: {env_file}")
        
        # Read current content
        with open(env_file, 'r') as f:
            current_content = f.read()
        
        # Check if email config already exists
        if 'MAIL_SERVER=smtp.gmail.com' in current_content:
            print("⚠️  Email configuration already exists in .env")
            print("   Updating with latest settings...")
            
            # Remove old email config lines
            lines = current_content.split('\n')
            new_lines = []
            skip_email_section = False
            
            for line in lines:
                if line.startswith('# Email Configuration'):
                    skip_email_section = True
                    new_lines.append(line)
                    continue
                elif skip_email_section and (line.startswith('#') or line.startswith('MAIL_') or line.startswith('GOOGLE_OAUTH')):
                    continue
                elif skip_email_section and line.strip() == '':
                    skip_email_section = False
                    new_lines.append('')
                    continue
                elif not skip_email_section:
                    new_lines.append(line)
            
            # Add new email config
            new_lines.append('')
            new_lines.append(email_config)
            new_content = '\n'.join(new_lines)
            
        else:
            print("📝 Adding email configuration to .env...")
            new_content = current_content + '\n' + email_config
    else:
        print(f"📝 Creating new .env file: {env_file}")
        new_content = email_config
    
    # Write the updated .env file
    try:
        with open(env_file, 'w') as f:
            f.write(new_content)
        print("✅ Email configuration updated successfully!")
        
        # Show the email section
        print("\n📧 Email Configuration Added:")
        print("-" * 40)
        for line in email_config.strip().split('\n'):
            if line.startswith('MAIL_'):
                key, value = line.split('=', 1)
                if 'PASSWORD' in key:
                    display_value = '✅ Set (masked for security)'
                else:
                    display_value = value
                print(f"   {key}: {display_value}")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("1. Restart your Flask service:")
    print("   sudo systemctl restart datacharted")
    print("2. Test email functionality:")
    print("   - Register a new user")
    print("   - Request password reset")
    print("3. Check email delivery")
    
    return True

def test_email_config():
    """Test if email configuration is working"""
    print("\n🧪 Testing Email Configuration...")
    print("-" * 40)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check required variables
    required_vars = [
        'MAIL_SERVER',
        'MAIL_PORT',
        'MAIL_USERNAME',
        'MAIL_PASSWORD',
        'MAIL_DEFAULT_SENDER'
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var:
                display_value = '✅ Set' if len(value) >= 16 else '❌ Too short'
            else:
                display_value = value
            print(f"   {var}: {display_value}")
        else:
            print(f"   {var}: ❌ Not set")
            all_set = False
    
    if all_set:
        print("\n✅ All email variables are configured!")
        print("📧 Ready to test email functionality")
    else:
        print("\n❌ Some email variables are missing")
        print("📝 Please check your .env file")
    
    return all_set

if __name__ == '__main__':
    print("🚀 DataCharted Live Server Email Setup")
    print("=" * 60)
    
    # Set up email configuration
    if setup_email_config():
        # Test the configuration
        test_email_config()
        
        print("\n🎉 Email setup complete!")
        print("📧 Your DataCharted app is now ready to send emails!")
    else:
        print("\n❌ Email setup failed. Please check the error messages above.")

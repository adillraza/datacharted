#!/usr/bin/env python3
"""
Simple email test script for DataCharted
Tests if email credentials are working
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_config():
    """Test email configuration"""
    print("🧪 Testing Email Configuration")
    print("=" * 40)
    
    # Check required email variables
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
            # Mask password for security
            if 'PASSWORD' in var:
                display_value = '✅ Set' if len(value) >= 16 else '❌ Too short'
            else:
                display_value = value
            print(f"   {var}: {display_value}")
        else:
            print(f"   {var}: ❌ Not set")
            all_set = False
    
    print("\n" + "=" * 40)
    
    if all_set:
        print("✅ All email variables are set!")
        print("📧 Ready to test email sending")
        
        # Test SMTP connection
        print("\n🔗 Testing SMTP connection...")
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            # Create test message
            msg = MIMEText("This is a test email from DataCharted")
            msg['Subject'] = "DataCharted Email Test"
            msg['From'] = os.getenv('MAIL_DEFAULT_SENDER')
            msg['To'] = os.getenv('MAIL_USERNAME')  # Send to yourself for testing
            
            # Connect to SMTP server
            server = smtplib.SMTP(os.getenv('MAIL_SERVER'), int(os.getenv('MAIL_PORT')))
            server.starttls()
            
            # Login
            username = os.getenv('MAIL_USERNAME')
            password = os.getenv('MAIL_PASSWORD')
            server.login(username, password)
            
            # Send test email
            server.send_message(msg)
            server.quit()
            
            print("   ✅ SMTP connection successful!")
            print("   ✅ Test email sent!")
            print(f"   📧 Check your inbox at {username}")
            
        except Exception as e:
            print(f"   ❌ SMTP connection failed: {str(e)}")
            print("\n🔧 Troubleshooting tips:")
            print("   - Check if 2FA is enabled on your Google account")
            print("   - Verify the app password is correct")
            print("   - Make sure 'Less secure app access' is disabled")
            print("   - Check if your domain allows SMTP access")
    else:
        print("❌ Some email variables are missing")
        print("📝 Please update your .env file with the required values")

if __name__ == '__main__':
    test_email_config()

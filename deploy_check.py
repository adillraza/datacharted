#!/usr/bin/env python3
"""
Deployment verification script for DataCharted
Run this on your server to check if everything is properly configured
"""

import os
import sys
import importlib

def check_python_packages():
    """Check if all required Python packages are installed"""
    print("🔍 Checking Python packages...")
    
    required_packages = [
        'flask',
        'flask_mail',
        'flask_sqlalchemy',
        'flask_login',
        'flask_migrate',
        'flask_cors',
        'python_dotenv',
        'psycopg2',
        'bcrypt',
        'email_validator',
        'gunicorn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("   Install with: pip3 install " + " ".join(missing_packages))
        return False
    else:
        print("✅ All required packages are installed")
        return True

def check_environment_variables():
    """Check if all required environment variables are set"""
    print("\n🔍 Checking environment variables...")
    
    # Load .env file if it exists
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'MAIL_SERVER',
        'MAIL_USERNAME',
        'MAIL_PASSWORD',
        'MAIL_DEFAULT_SENDER'
    ]
    
    optional_vars = [
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET',
        'MAIL_PORT',
        'MAIL_USE_TLS',
        'MAIL_USE_SSL'
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var or 'SECRET' in var:
                display_value = '✅ Set (masked)'
            else:
                display_value = f'✅ {value}'
            print(f"   {var}: {display_value}")
        else:
            print(f"   {var}: ❌ MISSING")
            missing_required.append(var)
    
    print("\n   Optional variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"   {var}: ✅ {value}")
        else:
            print(f"   {var}: ⚠️  Not set (using defaults)")
            missing_optional.append(var)
    
    if missing_required:
        print(f"\n❌ Missing required variables: {', '.join(missing_required)}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def check_flask_app():
    """Check if Flask app can be created and configured"""
    print("\n🔍 Checking Flask app configuration...")
    
    try:
        from app import create_app
        from config import Config
        
        app = create_app(Config)
        
        # Check email configuration
        mail_config = {
            'MAIL_SERVER': app.config.get('MAIL_SERVER'),
            'MAIL_PORT': app.config.get('MAIL_PORT'),
            'MAIL_USE_TLS': app.config.get('MAIL_USE_TLS'),
            'MAIL_USERNAME': app.config.get('MAIL_USERNAME'),
            'MAIL_DEFAULT_SENDER': app.config.get('MAIL_DEFAULT_SENDER')
        }
        
        print("   ✅ Flask app created successfully")
        print("   📧 Email configuration:")
        for key, value in mail_config.items():
            if key == 'MAIL_USERNAME' or key == 'MAIL_DEFAULT_SENDER':
                print(f"      {key}: {value}")
            else:
                print(f"      {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Flask app creation failed: {str(e)}")
        return False

def check_database():
    """Check if database connection works"""
    print("\n🔍 Checking database connection...")
    
    try:
        from app import create_app, db
        from config import Config
        
        app = create_app(Config)
        with app.app_context():
            # Try to execute a simple query
            db.engine.execute("SELECT 1")
            print("   ✅ Database connection successful")
            return True
            
    except Exception as e:
        print(f"   ❌ Database connection failed: {str(e)}")
        return False

def check_email_templates():
    """Check if email templates exist"""
    print("\n🔍 Checking email templates...")
    
    template_files = [
        'app/templates/emails/welcome.html',
        'app/templates/emails/welcome.txt',
        'app/templates/emails/password_reset.html',
        'app/templates/emails/password_reset.txt'
    ]
    
    missing_templates = []
    for template in template_files:
        if os.path.exists(template):
            print(f"   ✅ {template}")
        else:
            print(f"   ❌ {template} - MISSING")
            missing_templates.append(template)
    
    if missing_templates:
        print(f"\n❌ Missing email templates: {', '.join(missing_templates)}")
        return False
    else:
        print("✅ All email templates are present")
        return True

def main():
    """Main verification function"""
    print("🚀 DataCharted Deployment Verification")
    print("=" * 60)
    
    checks = [
        check_python_packages,
        check_environment_variables,
        check_flask_app,
        check_database,
        check_email_templates
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Check failed with error: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 Verification Results:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 All checks passed! Your deployment is ready.")
    else:
        print(f"⚠️  {passed}/{total} checks passed. Please fix the issues above.")
        print("\n🔧 Common fixes:")
        print("1. Install missing packages: pip3 install -r requirements.txt")
        print("2. Set up .env file with email configuration")
        print("3. Ensure database is accessible")
        print("4. Restart Flask service after fixes")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Debug script for DataCharted server issues
Run this on your server to diagnose internal server errors
"""

import os
import sys
import traceback

def debug_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    modules_to_test = [
        'flask',
        'flask_mail',
        'flask_sqlalchemy',
        'flask_login',
        'flask_migrate',
        'flask_cors',
        'dotenv',
        'psycopg2',
        'bcrypt',
        'email_validator'
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module}: {str(e)}")

def debug_environment():
    """Check environment variables"""
    print("\n🔍 Checking environment variables...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    env_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'MAIL_SERVER',
        'MAIL_USERNAME',
        'MAIL_PASSWORD',
        'MAIL_DEFAULT_SENDER'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var or 'SECRET' in var:
                print(f"   {var}: ✅ Set (length: {len(value)})")
            else:
                print(f"   {var}: ✅ {value}")
        else:
            print(f"   {var}: ❌ Not set")

def debug_flask_app():
    """Test Flask app creation"""
    print("\n🔍 Testing Flask app creation...")
    
    try:
        from app import create_app
        from config import Config
        
        print("   ✅ Imports successful")
        
        app = create_app(Config)
        print("   ✅ Flask app created")
        
        # Test email configuration
        mail_config = {
            'MAIL_SERVER': app.config.get('MAIL_SERVER'),
            'MAIL_PORT': app.config.get('MAIL_PORT'),
            'MAIL_USE_TLS': app.config.get('MAIL_USE_TLS'),
            'MAIL_USERNAME': app.config.get('MAIL_USERNAME'),
            'MAIL_DEFAULT_SENDER': app.config.get('MAIL_DEFAULT_SENDER')
        }
        
        print("   📧 Email configuration:")
        for key, value in mail_config.items():
            print(f"      {key}: {value}")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Flask app creation failed: {str(e)}")
        print("   🔍 Full traceback:")
        traceback.print_exc()
        return False

def debug_database():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from app import create_app, db
        from config import Config
        
        app = create_app(Config)
        with app.app_context():
            # Test database connection
            result = db.engine.execute("SELECT 1")
            print("   ✅ Database connection successful")
            return True
            
    except Exception as e:
        print(f"   ❌ Database connection failed: {str(e)}")
        print("   🔍 Full traceback:")
        traceback.print_exc()
        return False

def debug_email_function():
    """Test email function specifically"""
    print("\n🔍 Testing email function...")
    
    try:
        from app import create_app
        from config import Config
        from app.email_utils import send_welcome_email
        
        app = create_app(Config)
        with app.app_context():
            # Create a mock user object
            class MockUser:
                def __init__(self):
                    self.email = "test@example.com"
                    self.username = "testuser"
            
            mock_user = MockUser()
            
            # Test email function
            result = send_welcome_email(mock_user)
            print(f"   ✅ Email function test result: {result}")
            return True
            
    except Exception as e:
        print(f"   ❌ Email function test failed: {str(e)}")
        print("   🔍 Full traceback:")
        traceback.print_exc()
        return False

def debug_registration_route():
    """Test registration route specifically"""
    print("\n🔍 Testing registration route...")
    
    try:
        from app import create_app
        from config import Config
        from app.auth.routes import register
        from app.auth.forms import RegistrationForm
        
        app = create_app(Config)
        with app.app_context():
            print("   ✅ Registration route imports successful")
            
            # Test form creation
            form = RegistrationForm()
            print("   ✅ Registration form created")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Registration route test failed: {str(e)}")
        print("   🔍 Full traceback:")
        traceback.print_exc()
        return False

def main():
    """Run all debug tests"""
    print("🚨 DataCharted Server Debug Script")
    print("=" * 60)
    
    tests = [
        debug_imports,
        debug_environment,
        debug_flask_app,
        debug_database,
        debug_email_function,
        debug_registration_route
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test failed with error: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 Debug Results:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 All tests passed! The issue might be elsewhere.")
    else:
        print(f"⚠️  {passed}/{total} tests passed. Issues found above.")
        print("\n🔧 Next steps:")
        print("1. Fix the issues identified above")
        print("2. Check Flask service logs: sudo journalctl -u datacharted -f")
        print("3. Restart the service: sudo systemctl restart datacharted")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

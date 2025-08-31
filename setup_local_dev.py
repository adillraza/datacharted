#!/usr/bin/env python3
"""
Local Development Setup Script for DataCharted
This script sets up your local development environment
"""

import os
import subprocess
import sys

def create_env_file():
    """Create .env file for local development"""
    env_content = """# Local Development Environment Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production

# Database Configuration (Local SQLite)
DATABASE_URL=sqlite:///app_dev_local.db

# Email Configuration (Optional for local dev - leave blank to skip email)
MAIL_SERVER=
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=
MAIL_PASSWORD=

# Google OAuth (Optional - leave blank if not testing OAuth)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Development Settings
DEBUG=true
TESTING=false
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file for local development")
    else:
        print("⚠️  .env file already exists - skipping creation")

def setup_database():
    """Initialize the local database"""
    try:
        # Set environment variables
        os.environ['FLASK_APP'] = 'run.py'
        os.environ['FLASK_ENV'] = 'development'
        
        print("🗄️  Setting up local database...")
        
        # Initialize database
        result = subprocess.run(['flask', 'db', 'upgrade'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database initialized successfully")
        else:
            print("⚠️  Database migration output:", result.stdout)
            if result.stderr:
                print("Error:", result.stderr)
            
            # Try to initialize if no migrations exist
            print("🔄 Attempting to initialize database...")
            init_result = subprocess.run(['flask', 'db', 'init'], 
                                       capture_output=True, text=True)
            if init_result.returncode == 0:
                print("✅ Database migration folder initialized")
                
                # Create initial migration
                migrate_result = subprocess.run(['flask', 'db', 'migrate', '-m', 'Initial migration'], 
                                              capture_output=True, text=True)
                if migrate_result.returncode == 0:
                    print("✅ Initial migration created")
                    
                    # Apply migration
                    upgrade_result = subprocess.run(['flask', 'db', 'upgrade'], 
                                                  capture_output=True, text=True)
                    if upgrade_result.returncode == 0:
                        print("✅ Database setup complete")
                    else:
                        print("❌ Failed to apply migration")
                        return False
                else:
                    print("❌ Failed to create initial migration")
                    return False
            else:
                print("❌ Failed to initialize database")
                return False
                
    except FileNotFoundError:
        print("❌ Flask command not found. Make sure you've activated the virtual environment:")
        print("   source venv/bin/activate")
        return False
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
    
    return True

def create_admin_user():
    """Create an admin user for local development"""
    try:
        print("👤 Creating admin user for local development...")
        
        # Create admin user script
        admin_script = """
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Check if admin user already exists
    admin_user = User.query.filter_by(email='admin@localhost').first()
    if not admin_user:
        admin_user = User(
            email='admin@localhost',
            first_name='Admin',
            last_name='User',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            is_verified=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin user created: admin@localhost / admin123")
    else:
        print("⚠️  Admin user already exists")
"""
        
        result = subprocess.run([sys.executable, '-c', admin_script], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print("❌ Failed to create admin user:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 DataCharted Local Development Setup")
    print("=" * 40)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not detected!")
        print("Please activate your virtual environment first:")
        print("   source venv/bin/activate")
        print("Then run this script again.")
        return
    
    print("✅ Virtual environment detected")
    
    # Step 1: Create .env file
    create_env_file()
    
    # Step 2: Setup database
    if setup_database():
        # Step 3: Create admin user
        create_admin_user()
        
        print("\n🎉 Local development environment setup complete!")
        print("\n📋 Next steps:")
        print("1. Run the development server: python run.py")
        print("2. Open your browser to: http://localhost:5000")
        print("3. Login with: admin@localhost / admin123")
        print("\n💡 Tips:")
        print("- The app will auto-reload when you make changes")
        print("- Check the terminal for any error messages")
        print("- Local database file: app_dev_local.db")
    else:
        print("\n❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main()

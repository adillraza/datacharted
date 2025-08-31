#!/usr/bin/env python3
"""
Script to restore admin user after database was accidentally wiped
"""
import os
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

# Set environment
os.environ['FLASK_APP'] = 'run.py'
os.environ['FLASK_ENV'] = 'production'

def restore_admin_user():
    app = create_app()
    with app.app_context():
        try:
            # Check if admin user already exists
            admin_user = User.query.filter_by(email='admin@datacharted.com').first()
            if admin_user:
                print(f"✅ Admin user already exists: {admin_user.email}")
                return
            
            # Create admin user
            admin_user = User(
                email='admin@datacharted.com',
                first_name='Admin',
                last_name='User',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                is_verified=True
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"✅ Admin user restored successfully!")
            print(f"   Email: admin@datacharted.com")
            print(f"   Password: admin123")
            print(f"   Please change the password after login!")
            
            # Verify creation
            total_users = User.query.count()
            print(f"📊 Total users in database: {total_users}")
            
        except Exception as e:
            print(f"❌ Error restoring admin user: {e}")
            db.session.rollback()

if __name__ == '__main__':
    restore_admin_user()

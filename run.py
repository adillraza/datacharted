#!/usr/bin/env python3
"""
DataCharted Flask Application
Main entry point for running the application
"""

import os
from app import create_app, db
from app.models import User
from config import config

# Get environment and select appropriate config
env = os.getenv('FLASK_ENV') or 'development'
config_class = config.get(env, config['default'])

app = create_app(config_class)

@app.shell_context_processor
def make_shell_context():
    """Make database and models available in Flask shell"""
    return {
        'db': db,
        'User': User
    }

@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized!')

@app.cli.command()
def create_admin():
    """Create an admin user."""
    username = input('Enter admin username: ')
    email = input('Enter admin email: ')
    password = input('Enter admin password: ')
    
    if User.query.filter_by(username=username).first():
        print('User already exists!')
        return
    
    user = User(
        username=username,
        email=email,
        first_name='Admin',
        last_name='User',
        is_verified=True
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    print(f'Admin user {username} created successfully!')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5555)

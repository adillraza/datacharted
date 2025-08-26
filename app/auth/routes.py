from flask import render_template, redirect, url_for, flash, request, jsonify, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app.auth import bp
from app.models import User
from app import db
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, ProfileForm
from datetime import datetime
import re
import requests
import json
from urllib.parse import urlencode

# Google OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    # Debug logging
    if request.method == 'POST':
        print(f"🔍 DEBUG: Form data received")
        print(f"   Username: {request.form.get('username')}")
        print(f"   Password: {request.form.get('password')}")
        print(f"   Form valid: {form.validate()}")
        if not form.validate():
            print(f"   Form errors: {form.errors}")
    
    if form.validate_on_submit():
        print(f"✅ Form validation passed")
        user = User.query.filter_by(email=form.email.data).first()
        print(f"   User lookup result: {user}")
        
        if user is None or not user.check_password(form.password.data):
            print(f"   ❌ Login failed: user={user}, password_valid={user.check_password(form.password.data) if user else False}")
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Account is deactivated. Please contact support.', 'error')
            return redirect(url_for('auth.login'))
        
        print(f"   ✅ Login successful for user: {user.username}")
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/login/google')
def google_login():
    """Initiate Google OAuth login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Store the next page in session for after OAuth
    next_page = request.args.get('next')
    if next_page and url_parse(next_page).netloc == '':
        session['next'] = next_page
    
    # Google OAuth parameters
    params = {
        'client_id': current_app.config['GOOGLE_CLIENT_ID'],
        'redirect_uri': url_for('auth.google_callback', _external=True),
        'scope': 'openid email profile',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)

@bp.route('/login/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Get authorization code from Google
    code = request.args.get('code')
    if not code:
        flash('Google authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # Exchange code for access token
        token_data = {
            'client_id': current_app.config['GOOGLE_CLIENT_ID'],
            'client_secret': current_app.config['GOOGLE_CLIENT_SECRET'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': url_for('auth.google_callback', _external=True)
        }
        
        token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        # Get user info from Google
        headers = {'Authorization': f"Bearer {token_info['access_token']}"}
        user_response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
        user_response.raise_for_status()
        google_user_data = user_response.json()
        
        # Get or create user
        user = User.get_or_create_google_user(google_user_data)
        
        if not user.is_active:
            flash('Account is deactivated. Please contact support.', 'error')
            return redirect(url_for('auth.login'))
        
        # Log in the user
        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Redirect to next page or dashboard
        next_page = session.pop('next', None)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        
        flash(f'Welcome back, {user.first_name or user.username}!', 'success')
        return redirect(next_page)
        
    except Exception as e:
        print(f"Google OAuth error: {e}")
        flash('Google authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@bp.route('/register/google')
def google_register():
    """Initiate Google OAuth registration (same as login for now)"""
    return redirect(url_for('auth.google_login'))

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken. Please choose another one.', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please use another email or login.', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            company_name=form.company_name.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Send password reset email (implement later)
            flash('Check your email for the instructions to reset your password', 'info')
        else:
            flash('Email address not found.', 'error')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    user = User.verify_reset_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.company_name = form.company_name.data
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('auth.profile'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.company_name.data = current_user.company_name
    return render_template('auth/profile.html', title='Edit Profile', form=form)

# API endpoints for future integration
@bp.route('/api/user', methods=['GET'])
@login_required
def get_user():
    return jsonify(current_user.to_dict())

@bp.route('/api/user/update', methods=['PUT'])
@login_required
def update_user():
    data = request.get_json()
    
    if 'first_name' in data:
        current_user.first_name = data['first_name']
    if 'last_name' in data:
        current_user.last_name = data['last_name']
    if 'company_name' in data:
        current_user.company_name = data['company_name']
    
    db.session.commit()
    return jsonify({'message': 'User updated successfully', 'user': current_user.to_dict()})

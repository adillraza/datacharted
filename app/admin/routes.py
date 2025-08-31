from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.admin import bp
from app.models import User
from app import db
from werkzeug.security import generate_password_hash
import re

def admin_required(f):
    """Decorator to check if user is admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         active_users=active_users,
                         recent_users=recent_users)

@bp.route('/users')
@login_required
@admin_required
def users():
    """Users list page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Search functionality
    search = request.args.get('search', '')
    if search:
        users = User.query.filter(
            (User.first_name.ilike(f'%{search}%')) |
            (User.last_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        ).order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        users = User.query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    return render_template('admin/users.html', users=users, search=search)

@bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """User detail/edit page"""
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_detail.html', user=user)

@bp.route('/users/<int:user_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user information"""
    user = User.query.get_or_404(user_id)
    
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    is_active = 'is_active' in request.form
    is_admin = 'is_admin' in request.form
    
    # Validation
    errors = []
    
    if not first_name and not last_name:
        errors.append('At least first name or last name is required')
    
    if not email:
        errors.append('Email is required')
    elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        errors.append('Invalid email format')
    elif User.query.filter(User.email == email, User.id != user.id).first():
        errors.append('Email already exists')
    
    if password and len(password) < 6:
        errors.append('Password must be at least 6 characters')
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('admin.user_detail', user_id=user.id))
    
    # Update user
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.is_active = is_active
    user.is_admin = is_admin
    
    if password:
        user.password_hash = generate_password_hash(password)
    
    try:
        db.session.commit()
        flash('User updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating user. Please try again.', 'error')
    
    return redirect(url_for('admin.user_detail', user_id=user.id))

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user (soft delete)"""
    if current_user.id == user_id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = False
    user.deleted_at = db.func.now()
    
    try:
        db.session.commit()
        flash('User deactivated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deactivating user. Please try again.', 'error')
    
    return redirect(url_for('admin.users'))

@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Create new user"""
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        is_admin = 'is_admin' in request.form
        
        # Validation
        errors = []
        
        if not first_name and not last_name:
            errors.append('At least first name or last name is required')
        
        if not email:
            errors.append('Email is required')
        elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append('Invalid email format')
        elif User.query.filter_by(email=email).first():
            errors.append('Email already exists')
        
        if not password:
            errors.append('Password is required')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('admin/create_user.html')
        
        # Create user
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_admin=is_admin
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('User created successfully!', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating user. Please try again.', 'error')
    
    return render_template('admin/create_user.html')

@bp.route('/api/users')
@login_required
@admin_required
def api_users():
    """API endpoint for users data (for AJAX)"""
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip() or 'No Name',
        'email': user.email,
        'is_active': user.is_active,
        'is_admin': user.is_admin,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'last_login': user.last_login.isoformat() if user.last_login else None
    } for user in users])

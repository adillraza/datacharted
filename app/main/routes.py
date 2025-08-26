from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.main import bp

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html', title='DataCharted - Welcome')

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('main/dashboard.html', title='Dashboard')

@bp.route('/get-started')
def get_started():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.register'))

@bp.route('/pricing')
def pricing():
    return render_template('main/pricing.html', title='Pricing')

@bp.route('/about')
def about():
    return render_template('main/about.html', title='About DataCharted')

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

# Service Pages
@bp.route('/services/data-strategy-consulting')
def data_strategy_consulting():
    return render_template('services/data_strategy_consulting.html', title='Data Strategy & Consulting')

@bp.route('/services/data-integration-automation')
def data_integration_automation():
    return render_template('services/data_integration_automation.html', title='Data Integration & Automation')

@bp.route('/services/data-modeling-transformation')
def data_modeling_transformation():
    return render_template('services/data_modeling_transformation.html', title='Data Modeling & Transformation')

@bp.route('/services/dashboard-design-visualization')
def dashboard_design_visualization():
    return render_template('services/dashboard_design_visualization.html', title='Dashboard Design & Visualization')

@bp.route('/services/advanced-analytics-forecasting')
def advanced_analytics_forecasting():
    return render_template('services/advanced_analytics_forecasting.html', title='Advanced Analytics & Forecasting')

@bp.route('/services/custom-api-connectors')
def custom_api_connectors():
    return render_template('services/custom_api_connectors.html', title='Custom API Connectors')

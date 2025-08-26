from flask import jsonify, request
from flask_login import login_required, current_user
from app.api import bp
from app.models import User
from app import db

@bp.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'DataCharted API',
        'version': '1.0.0'
    })

@bp.route('/user/status')
@login_required
def user_status():
    """Get current user's connection status and project info"""
    return jsonify({
        'user_id': current_user.id,
        'username': current_user.username,
        'connections': {
            'google_ads': current_user.google_ads_connected,
            'meta_ads': current_user.meta_ads_connected,
            'callrail': current_user.callrail_connected,
            'ghl': current_user.ghl_connected
        },
        'projects': {
            'bigquery_project_id': current_user.bigquery_project_id,
            'bigquery_dataset': current_user.bigquery_dataset,
            'vps_ip': current_user.vps_ip
        }
    })

# Future endpoints for data source connections
@bp.route('/connections/google-ads', methods=['POST'])
@login_required
def connect_google_ads():
    """Connect Google Ads account"""
    # TODO: Implement Google Ads OAuth flow
    return jsonify({'message': 'Google Ads connection endpoint - coming soon'})

@bp.route('/connections/meta-ads', methods=['POST'])
@login_required
def connect_meta_ads():
    """Connect Meta Ads account"""
    # TODO: Implement Meta Ads OAuth flow
    return jsonify({'message': 'Meta Ads connection endpoint - coming soon'})

@bp.route('/connections/callrail', methods=['POST'])
@login_required
def connect_callrail():
    """Connect CallRail account"""
    # TODO: Implement CallRail API integration
    return jsonify({'message': 'CallRail connection endpoint - coming soon'})

@bp.route('/connections/ghl', methods=['POST'])
@login_required
def connect_ghl():
    """Connect GoHighLevel account"""
    # TODO: Implement GHL API integration
    return jsonify({'message': 'GoHighLevel connection endpoint - coming soon'})

# Future endpoints for infrastructure management
@bp.route('/infrastructure/bigquery', methods=['POST'])
@login_required
def setup_bigquery():
    """Set up BigQuery project and dataset for user"""
    # TODO: Implement BigQuery project creation
    return jsonify({'message': 'BigQuery setup endpoint - coming soon'})

@bp.route('/infrastructure/vps', methods=['POST'])
@login_required
def setup_vps():
    """Set up DigitalOcean VPS with Airbyte"""
    # TODO: Implement VPS creation and Airbyte deployment
    return jsonify({'message': 'VPS setup endpoint - coming soon'})

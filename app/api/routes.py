from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from app.api import bp
import subprocess
import hmac
import hashlib
import os

@bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'service': 'DataCharted API',
        'status': 'healthy',
        'version': '1.0.0'
    })

@bp.route('/user/status')
@login_required
def user_status():
    """Get current user status"""
    return jsonify({
        'user_id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'is_active': current_user.is_active,
        'is_verified': current_user.is_verified
    })

@bp.route('/webhook/deploy', methods=['POST'])
def deploy_webhook():
    """GitHub webhook for automatic deployment"""
    # Verify GitHub webhook signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        return jsonify({'error': 'No signature provided'}), 401
    
    # Get the webhook secret from environment
    webhook_secret = os.environ.get('GITHUB_WEBHOOK_SECRET', 'your-webhook-secret')
    
    # Calculate expected signature
    expected_signature = 'sha256=' + hmac.new(
        webhook_secret.encode('utf-8'),
        request.data,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Check if this is a push to main branch
    payload = request.get_json()
    if payload.get('ref') != 'refs/heads/main':
        return jsonify({'message': 'Not main branch, skipping deployment'}), 200
    
    try:
        # Run deployment script
        result = subprocess.run(
            ['/opt/deploy/deploy.sh'],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            return jsonify({
                'message': 'Deployment triggered successfully',
                'output': result.stdout
            }), 200
        else:
            return jsonify({
                'error': 'Deployment failed',
                'output': result.stdout,
                'error_output': result.stderr
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Deployment timed out'}), 500
    except Exception as e:
        return jsonify({'error': f'Deployment error: {str(e)}'}), 500

# Future endpoints for data source connections
@bp.route('/connect/google-ads', methods=['POST'])
@login_required
def connect_google_ads():
    """Connect Google Ads account"""
    return jsonify({'message': 'Google Ads connection endpoint - coming soon'})

@bp.route('/connect/meta-ads', methods=['POST'])
@login_required
def connect_meta_ads():
    """Connect Meta Ads account"""
    return jsonify({'message': 'Meta Ads connection endpoint - coming soon'})

@bp.route('/connect/callrail', methods=['POST'])
@login_required
def connect_callrail():
    """Connect CallRail account"""
    return jsonify({'message': 'CallRail connection endpoint - coming soon'})

@bp.route('/connect/ghl', methods=['POST'])
@login_required
def connect_ghl():
    """Connect GoHighLevel account"""
    return jsonify({'message': 'GoHighLevel connection endpoint - coming soon'})

@bp.route('/setup/bigquery', methods=['POST'])
@login_required
def setup_bigquery():
    """Setup BigQuery project and dataset"""
    return jsonify({'message': 'BigQuery setup endpoint - coming soon'})

@bp.route('/setup/vps', methods=['POST'])
@login_required
def setup_vps():
    """Setup DigitalOcean VPS"""
    return jsonify({'message': 'VPS setup endpoint - coming soon'})

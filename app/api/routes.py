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
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
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

# BigQuery Management Endpoints
@bp.route('/bigquery/projects', methods=['GET'])
@login_required
def list_bigquery_projects():
    """List all BigQuery projects for the current user"""
    from app.services.bigquery_service import bigquery_service
    
    try:
        projects = bigquery_service.list_user_projects(current_user)
        return jsonify({
            'projects': [project.to_dict() for project in projects],
            'count': len(projects)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/bigquery/projects', methods=['POST'])
@login_required
def create_bigquery_project():
    """Create a new managed BigQuery project"""
    from app.services.bigquery_service import bigquery_service
    
    data = request.get_json()
    if not data or not data.get('project_name'):
        return jsonify({'error': 'project_name is required'}), 400
    
    project_name = data['project_name'].strip()
    if len(project_name) < 3 or len(project_name) > 100:
        return jsonify({'error': 'project_name must be between 3 and 100 characters'}), 400
    
    # Optional folder name for first project
    folder_name = data.get('folder_name', '').strip() if data.get('folder_name') else None
    if folder_name and (len(folder_name) < 3 or len(folder_name) > 50):
        return jsonify({'error': 'folder_name must be between 3 and 50 characters'}), 400
    
    try:
        project = bigquery_service.create_managed_project(current_user, project_name, folder_name)
        return jsonify({
            'message': 'BigQuery project creation started',
            'project': project.to_dict(),
            'folder_info': {
                'folder_id': current_user.gcp_folder_id,
                'folder_name': current_user.gcp_folder_name
            }
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/bigquery/projects/<project_id>', methods=['GET'])
@login_required
def get_bigquery_project(project_id):
    """Get details of a specific BigQuery project"""
    from app.services.bigquery_service import bigquery_service
    
    try:
        project = bigquery_service.get_project(current_user, project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify({'project': project.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/bigquery/projects/<project_id>/status', methods=['GET'])
@login_required
def get_bigquery_project_status(project_id):
    """Get the current status of a BigQuery project"""
    from app.services.bigquery_service import bigquery_service
    
    try:
        # Verify user owns this project
        project = bigquery_service.get_project(current_user, project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        status = bigquery_service.get_project_status(project_id)
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/bigquery/projects/creation-progress/<project_id>', methods=['GET'])
@login_required
def get_project_creation_progress(project_id):
    """Get real-time progress of project creation"""
    from app.services.bigquery_service import bigquery_service
    
    try:
        # Verify user owns this project
        project = bigquery_service.get_project(current_user, project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        progress = bigquery_service.get_creation_progress(project_id)
        return jsonify(progress)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/bigquery/projects/<project_id>', methods=['DELETE'])
@login_required
def delete_bigquery_project(project_id):
    """Delete a BigQuery project (soft delete)"""
    from app.services.bigquery_service import bigquery_service
    
    try:
        success = bigquery_service.delete_project(current_user, project_id)
        if not success:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify({'message': 'Project deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/setup/vps', methods=['POST'])
@login_required
def setup_vps():
    """Setup DigitalOcean VPS"""
    return jsonify({'message': 'VPS setup endpoint - coming soon'})

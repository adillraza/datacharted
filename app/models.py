from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
import jwt
from time import time
from config import Config

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    company_name = db.Column(db.String(128))
    phone_number = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    
    # Google OAuth fields
    google_id = db.Column(db.String(128), unique=True, nullable=True)
    google_picture = db.Column(db.String(512), nullable=True)
    auth_provider = db.Column(db.String(20), default='local')  # 'local' or 'google'
    
    # GCP Organization structure
    gcp_folder_id = db.Column(db.String(128))  # User's dedicated folder in organization
    gcp_folder_name = db.Column(db.String(256))  # Human-readable folder name
    
    # Relationships to data pipeline components
    bigquery_projects = db.relationship('BigQueryProject', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    vps_instances = db.relationship('VPSInstance', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    data_sources = db.relationship('DataSource', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def is_google_user(self):
        return self.auth_provider == 'google' and self.google_id is not None
    
    def get_folder_prefix(self):
        """Generate folder prefix from user's email domain"""
        if not self.email:
            return 'datacharted'
        
        domain = self.email.split('@')[1] if '@' in self.email else 'datacharted'
        # Clean domain for GCP naming (only lowercase letters, numbers, hyphens)
        clean_domain = ''.join(c for c in domain.lower() if c.isalnum() or c == '-')
        return clean_domain[:20]  # Limit length
    
    def get_reset_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            Config.JWT_SECRET_KEY, algorithm='HS256'
        )
    
    @staticmethod
    def verify_reset_token(token):
        try:
            id = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])['reset_password']
        except:
            return None
        return User.query.get(id)
    
    @staticmethod
    def get_or_create_google_user(google_data):
        """Get existing user by Google ID or create new one"""
        user = User.query.filter_by(google_id=google_data['sub']).first()
        
        if not user:
            # Check if email already exists
            user = User.query.filter_by(email=google_data['email']).first()
            if user:
                # Link existing user to Google
                user.google_id = google_data['sub']
                user.auth_provider = 'google'
                user.google_picture = google_data.get('picture')
                user.is_verified = True
                db.session.commit()
            else:
                # Create new user
                user = User(
                    email=google_data['email'],
                    first_name=google_data.get('given_name', ''),
                    last_name=google_data.get('family_name', ''),
                    google_id=google_data['sub'],
                    google_picture=google_data.get('picture'),
                    auth_provider='google',
                    is_verified=True,
                    is_active=True
                )
                db.session.add(user)
                db.session.commit()
        
        return user
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company_name': self.company_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'auth_provider': self.auth_provider,
            'google_picture': self.google_picture,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            # Related data pipeline components
            'bigquery_projects_count': self.bigquery_projects.count(),
            'vps_instances_count': self.vps_instances.count(),
            'data_sources_count': self.data_sources.count()
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class BigQueryProject(db.Model):
    """Managed BigQuery projects for users"""
    __tablename__ = 'bigquery_projects'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Project identification
    project_id = db.Column(db.String(128), unique=True, nullable=False, index=True)
    project_name = db.Column(db.String(256), nullable=False)
    project_number = db.Column(db.String(64))  # GCP project number
    
    # Project type and billing
    project_type = db.Column(db.String(20), default='managed')  # 'managed' or 'external'
    billing_account_id = db.Column(db.String(128))  # For managed projects
    
    # Configuration
    default_dataset = db.Column(db.String(128), default='datacharted_data')
    location = db.Column(db.String(32), default='US')  # BigQuery location
    
    # Service account for integrations
    service_account_email = db.Column(db.String(256))
    service_account_key_path = db.Column(db.String(512))  # Path to JSON key file
    
    # Status and metadata
    status = db.Column(db.String(20), default='creating')  # creating, active, error, deleted
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)
    
    # Relationships
    data_sources = db.relationship('DataSource', backref='bigquery_project', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_name': self.project_name,
            'project_type': self.project_type,
            'default_dataset': self.default_dataset,
            'location': self.location,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<BigQueryProject {self.project_id}>'


class VPSInstance(db.Model):
    """DigitalOcean VPS instances for Airbyte deployment"""
    __tablename__ = 'vps_instances'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bigquery_project_id = db.Column(db.Integer, db.ForeignKey('bigquery_projects.id'))
    
    # DigitalOcean droplet info
    droplet_id = db.Column(db.String(128), unique=True, index=True)
    droplet_name = db.Column(db.String(256), nullable=False)
    
    # Network configuration
    public_ip = db.Column(db.String(45))  # IPv4/IPv6 compatible
    private_ip = db.Column(db.String(45))
    region = db.Column(db.String(32), default='nyc1')
    size = db.Column(db.String(32), default='s-2vcpu-2gb')
    
    # Airbyte configuration
    airbyte_workspace_id = db.Column(db.String(128))
    airbyte_url = db.Column(db.String(512))  # http://ip:8000
    airbyte_username = db.Column(db.String(128))
    airbyte_password = db.Column(db.String(128))
    
    # Status and metadata
    status = db.Column(db.String(20), default='creating')  # creating, active, error, deleted
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)
    
    # Relationship
    bigquery_project = db.relationship('BigQueryProject', backref='vps_instances')
    
    def to_dict(self):
        return {
            'id': self.id,
            'droplet_id': self.droplet_id,
            'droplet_name': self.droplet_name,
            'public_ip': self.public_ip,
            'region': self.region,
            'size': self.size,
            'airbyte_url': self.airbyte_url,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<VPSInstance {self.droplet_name}>'


class DataSource(db.Model):
    """Data source connections (Google Ads, Meta Ads, etc.)"""
    __tablename__ = 'data_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bigquery_project_id = db.Column(db.Integer, db.ForeignKey('bigquery_projects.id'))
    
    # Source identification
    source_type = db.Column(db.String(50), nullable=False)  # 'google_ads', 'meta_ads', 'callrail', 'ghl'
    source_name = db.Column(db.String(256), nullable=False)  # User-friendly name
    
    # Connection configuration (stored as JSON)
    connection_config = db.Column(db.JSON)  # OAuth tokens, API keys, etc.
    
    # Airbyte integration
    airbyte_source_id = db.Column(db.String(128))  # Airbyte source ID
    airbyte_connection_id = db.Column(db.String(128))  # Airbyte connection ID
    
    # Sync configuration
    sync_frequency = db.Column(db.String(32), default='daily')  # hourly, daily, weekly
    sync_enabled = db.Column(db.Boolean, default=True)
    last_sync_at = db.Column(db.DateTime)
    next_sync_at = db.Column(db.DateTime)
    
    # Status and metadata
    status = db.Column(db.String(20), default='configuring')  # configuring, active, error, paused
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_type': self.source_type,
            'source_name': self.source_name,
            'sync_frequency': self.sync_frequency,
            'sync_enabled': self.sync_enabled,
            'status': self.status,
            'error_message': self.error_message,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'next_sync_at': self.next_sync_at.isoformat() if self.next_sync_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<DataSource {self.source_type}:{self.source_name}>'

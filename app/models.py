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
    
    # Future fields for data sources
    google_ads_connected = db.Column(db.Boolean, default=False)
    meta_ads_connected = db.Column(db.Boolean, default=False)
    callrail_connected = db.Column(db.Boolean, default=False)
    ghl_connected = db.Column(db.Boolean, default=False)
    
    # BigQuery project info
    bigquery_project_id = db.Column(db.String(128))
    bigquery_dataset = db.Column(db.String(128))
    
    # DigitalOcean VPS info
    vps_id = db.Column(db.String(128))
    vps_ip = db.Column(db.String(45))  # IPv6 compatible
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def is_google_user(self):
        return self.auth_provider == 'google' and self.google_id is not None
    
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
            'google_ads_connected': self.google_ads_connected,
            'meta_ads_connected': self.meta_ads_connected,
            'callrail_connected': self.callrail_connected,
            'ghl_connected': self.ghl_connected,
            'bigquery_project_id': self.bigquery_project_id,
            'vps_ip': self.vps_ip
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

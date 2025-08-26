from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
import jwt
from time import time
from config import Config

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    company_name = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    
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
        return check_password_hash(self.password_hash, password)
    
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company_name': self.company_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
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
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

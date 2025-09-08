"""
BigQuery Project Management Service

This service handles the creation and management of BigQuery projects
in your managed GCP environment for users.
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from google.cloud import resourcemanager_v3
from google.cloud import bigquery
from google.cloud import iam
# from google.cloud import serviceusage_v1  # Will implement later
from google.oauth2 import service_account
from google.api_core import exceptions as gcp_exceptions

from app import db
from app.models import User, BigQueryProject
from config import Config

logger = logging.getLogger(__name__)


class BigQueryService:
    """Service for managing BigQuery projects in your GCP environment"""
    
    def __init__(self):
        """Initialize the BigQuery service with your GCP credentials"""
        self.master_project_id = Config.GOOGLE_CLOUD_PROJECT
        self.billing_account_id = os.environ.get('GCP_BILLING_ACCOUNT_ID')
        self.organization_id = os.environ.get('GCP_ORGANIZATION_ID')
        
        if not self.organization_id:
            raise ValueError("GCP_ORGANIZATION_ID is required for folder-based project management")
        
        # Initialize GCP clients
        self._init_gcp_clients()
    
    def _init_gcp_clients(self):
        """Initialize Google Cloud clients"""
        try:
            # Use service account credentials if provided, otherwise use default
            credentials_path = Config.GOOGLE_APPLICATION_CREDENTIALS
            if credentials_path and os.path.exists(credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
            else:
                credentials = None  # Use default credentials
            
            self.projects_client = resourcemanager_v3.ProjectsClient(credentials=credentials)
            self.folders_client = resourcemanager_v3.FoldersClient(credentials=credentials)
            self.bigquery_client = bigquery.Client(credentials=credentials)
            # self.service_usage_client = serviceusage_v1.ServiceUsageClient(credentials=credentials)  # Will implement later
            
        except Exception as e:
            logger.error(f"Failed to initialize GCP clients: {str(e)}")
            raise
    
    def ensure_user_folder(self, user: User, folder_name: str) -> str:
        """
        Ensure user has a dedicated folder in the organization.
        Creates folder if it doesn't exist.
        
        Args:
            user: The user requesting the folder
            folder_name: Human-readable name for the folder
            
        Returns:
            str: The folder ID (e.g., "folders/123456789")
        """
        if user.gcp_folder_id:
            # Verify folder still exists
            try:
                folder_request = resourcemanager_v3.GetFolderRequest(
                    name=user.gcp_folder_id
                )
                self.folders_client.get_folder(request=folder_request)
                logger.info(f"Using existing folder for user {user.id}: {user.gcp_folder_id}")
                return user.gcp_folder_id
            except gcp_exceptions.NotFound:
                logger.warning(f"User's folder {user.gcp_folder_id} not found, creating new one")
                user.gcp_folder_id = None
        
        # Create new folder
        prefix = user.get_folder_prefix()
        folder_display_name = f"{prefix}-{folder_name}"
        
        # Ensure unique folder name
        folder_display_name = self._ensure_unique_folder_name(folder_display_name)
        
        folder_request = resourcemanager_v3.CreateFolderRequest(
            folder=resourcemanager_v3.Folder(
                display_name=folder_display_name,
                parent=f"organizations/{self.organization_id}"
            )
        )
        
        try:
            operation = self.folders_client.create_folder(request=folder_request)
            folder = operation.result(timeout=60)  # Wait up to 1 minute
            
            # Update user record
            user.gcp_folder_id = folder.name  # This will be "folders/123456789"
            user.gcp_folder_name = folder_display_name
            db.session.commit()
            
            logger.info(f"Created folder for user {user.id}: {folder.name}")
            return folder.name
            
        except Exception as e:
            logger.error(f"Failed to create folder for user {user.id}: {str(e)}")
            raise
    
    def _ensure_unique_folder_name(self, base_name: str) -> str:
        """Ensure folder name is unique and within GCP limits (30 chars max)"""
        import time
        timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
        
        # GCP folder names must be <= 30 characters
        max_base_length = 30 - len(timestamp) - 1  # -1 for the dash
        if len(base_name) > max_base_length:
            base_name = base_name[:max_base_length]
        
        return f"{base_name}-{timestamp}"
    
    def create_managed_project(self, user: User, project_name: str, folder_name: str = None) -> BigQueryProject:
        """
        Create a new managed BigQuery project for a user
        
        Args:
            user: The user requesting the project
            project_name: Human-readable name for the project
            folder_name: Name for user's folder (if first project)
            
        Returns:
            BigQueryProject: The created project record
        """
        try:
            # Ensure user has a folder (create if first project)
            if not folder_name:
                folder_name = f"{user.first_name or 'user'}-{user.id}"
            
            folder_id = self.ensure_user_folder(user, folder_name)
            
            # Generate unique project ID
            project_id = self._generate_project_id(user, project_name)
            
            # Create database record first (with 'creating' status)
            bq_project = BigQueryProject(
                user_id=user.id,
                project_id=project_id,
                project_name=project_name,
                project_type='managed',
                billing_account_id=self.billing_account_id,
                status='creating'
            )
            db.session.add(bq_project)
            db.session.commit()
            
            logger.info(f"Starting BigQuery project creation for user {user.id}: {project_id}")
            
            # Create the GCP project in user's folder
            gcp_project = self._create_gcp_project(project_id, project_name, folder_id)
            
            # Update project number
            bq_project.project_number = str(gcp_project.name.split('/')[-1])
            
            # Enable required APIs
            self._enable_required_apis(project_id)
            
            # Set up billing
            self._setup_billing(project_id)
            
            # Create BigQuery dataset
            dataset_id = self._create_bigquery_dataset(project_id, bq_project.default_dataset)
            
            # Create service account for integrations
            service_account_email = self._create_service_account(project_id, user)
            bq_project.service_account_email = service_account_email
            
            # Add user as viewer to the project
            self._add_user_as_viewer(project_id, user.email)
            
            # Update status to active
            bq_project.status = 'active'
            bq_project.updated_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Successfully created BigQuery project: {project_id}")
            return bq_project
            
        except Exception as e:
            logger.error(f"Failed to create BigQuery project: {str(e)}")
            
            # Update status to error
            if 'bq_project' in locals():
                bq_project.status = 'error'
                bq_project.error_message = str(e)
                bq_project.updated_at = datetime.utcnow()
                db.session.commit()
            
            raise
    
    def _generate_project_id(self, user: User, project_name: str) -> str:
        """Generate a unique GCP project ID with domain prefix"""
        # GCP project IDs must be 6-30 characters, lowercase, numbers, hyphens
        prefix = user.get_folder_prefix()
        
        # Clean project name for ID
        clean_name = ''.join(c for c in project_name.lower() if c.isalnum() or c == '-')[:10]
        short_uuid = str(uuid.uuid4())[:6]
        
        # Format: {domain-prefix}-{clean-name}-{uuid}
        project_id = f"{prefix}-{clean_name}-{short_uuid}"
        
        # Ensure it's within length limits (30 chars max)
        if len(project_id) > 30:
            project_id = f"{prefix}-{short_uuid}"
        
        return project_id.lower()
    
    def _create_gcp_project(self, project_id: str, project_name: str, folder_id: str):
        """Create the actual GCP project in the specified folder"""
        project_request = resourcemanager_v3.CreateProjectRequest(
            project=resourcemanager_v3.Project(
                project_id=project_id,
                display_name=f"DataCharted - {project_name}",
                parent=folder_id,  # Create in user's dedicated folder
                labels={
                    "created-by": "datacharted",
                    "environment": "managed",
                    "service": "bigquery"
                }
            )
        )
        
        operation = self.projects_client.create_project(request=project_request)
        
        # Wait for operation to complete (this can take a few minutes)
        result = operation.result(timeout=300)  # 5 minutes timeout
        
        return result
    
    def _enable_required_apis(self, project_id: str):
        """Enable required APIs for the project"""
        required_apis = [
            'bigquery.googleapis.com',
            'bigquerystorage.googleapis.com',
            'iam.googleapis.com',
            'cloudresourcemanager.googleapis.com'
        ]
        
        logger.info(f"Enabling APIs for {project_id}: {required_apis}")
        
        # Enable APIs using gcloud command
        try:
            import subprocess
            apis_string = " ".join(required_apis)
            cmd = f"gcloud services enable {apis_string} --project={project_id}"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"Successfully enabled APIs for project {project_id}")
            else:
                logger.error(f"Failed to enable APIs for project {project_id}: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error enabling APIs for project {project_id}: {str(e)}")
    
    def _setup_billing(self, project_id: str):
        """Associate the project with your billing account"""
        if not self.billing_account_id:
            logger.warning("No billing account configured")
            return
        
        try:
            import subprocess
            
            # Link project to billing account using gcloud beta
            cmd = f"gcloud beta billing projects link {project_id} --billing-account={self.billing_account_id}"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                logger.info(f"Successfully linked project {project_id} to billing account {self.billing_account_id}")
            else:
                logger.error(f"Failed to link billing for project {project_id}: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error setting up billing for project {project_id}: {str(e)}")
    
    def _create_bigquery_dataset(self, project_id: str, dataset_id: str) -> str:
        """Create the default BigQuery dataset"""
        client = bigquery.Client(project=project_id)
        
        dataset_ref = client.dataset(dataset_id)
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"  # or your preferred location
        dataset.description = "DataCharted managed dataset for data pipeline"
        
        # Set access controls
        access_entries = list(dataset.access_entries)
        # Add your service account as owner
        # Add user as viewer
        
        dataset.access_entries = access_entries
        
        created_dataset = client.create_dataset(dataset, exists_ok=True)
        logger.info(f"Created dataset {dataset_id} in project {project_id}")
        
        return created_dataset.dataset_id
    
    def _create_service_account(self, project_id: str, user: User) -> str:
        """Create a service account for Airbyte integration"""
        service_account_id = f"datacharted-airbyte-{user.id}"
        service_account_email = f"{service_account_id}@{project_id}.iam.gserviceaccount.com"
        
        # TODO: Implement service account creation using IAM API
        logger.info(f"Need to create service account: {service_account_email}")
        
        return service_account_email
    
    def _add_user_as_viewer(self, project_id: str, user_email: str):
        """Add the user as a viewer to the BigQuery project"""
        # TODO: Implement IAM policy binding using IAM API
        logger.info(f"Need to add {user_email} as viewer to project {project_id}")
    
    def list_user_projects(self, user: User) -> List[BigQueryProject]:
        """Get all BigQuery projects for a user"""
        return user.bigquery_projects.filter_by(deleted_at=None).all()
    
    def get_project(self, user: User, project_id: str) -> Optional[BigQueryProject]:
        """Get a specific BigQuery project for a user"""
        return user.bigquery_projects.filter_by(
            project_id=project_id,
            deleted_at=None
        ).first()
    
    def delete_project(self, user: User, project_id: str) -> bool:
        """
        Soft delete a BigQuery project
        
        Note: This marks the project as deleted in our database.
        The actual GCP project deletion should be handled separately
        for safety reasons.
        """
        project = self.get_project(user, project_id)
        if not project:
            return False
        
        project.deleted_at = datetime.utcnow()
        project.status = 'deleted'
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Soft deleted BigQuery project: {project_id}")
        return True
    
    def get_project_status(self, project_id: str) -> Dict:
        """Get the current status of a BigQuery project"""
        project = BigQueryProject.query.filter_by(project_id=project_id).first()
        if not project:
            return {'status': 'not_found'}
        
        return {
            'status': project.status,
            'error_message': project.error_message,
            'created_at': project.created_at,
            'updated_at': project.updated_at
        }


# Global service instance
bigquery_service = BigQueryService()

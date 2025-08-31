# 🏗️ DataCharted Platform Architecture Refactor Plan

## 🎯 **Vision: Comprehensive Data Pipeline Platform**

Transform from a simple user management system to a robust data pipeline platform where users can:
- Connect multiple data sources (Google Ads, Meta Ads, CallRail, GHL, etc.)
- Run automated data ingestion pipelines
- Store data in BigQuery or other destinations
- Create Looker Studio reports and dashboards
- Monitor pipeline health and performance

## 📊 **Current State Analysis**

### ✅ **Strengths**
- Solid authentication system with Google OAuth
- User management with admin panel
- Database migration system working perfectly
- Deployment pipeline established
- Basic data source connection fields in User model

### ⚠️ **Areas for Improvement**
- Monolithic structure (everything in User model)
- No separation of concerns for data pipeline logic
- Missing core data pipeline entities
- No background job processing
- Limited API structure for external integrations

## 🏛️ **Proposed Architecture**

### **1. Domain-Driven Design Structure**

```
app/
├── __init__.py
├── core/                          # Core business logic
│   ├── __init__.py
│   ├── auth/                      # Authentication domain
│   ├── users/                     # User management domain
│   └── shared/                    # Shared utilities
├── pipelines/                     # Data pipeline domain
│   ├── __init__.py
│   ├── models/                    # Pipeline data models
│   ├── connectors/                # Data source connectors
│   ├── processors/                # Data processing logic
│   ├── destinations/              # Data destination handlers
│   └── orchestration/             # Pipeline orchestration
├── integrations/                  # External service integrations
│   ├── __init__.py
│   ├── google_ads/
│   ├── meta_ads/
│   ├── callrail/
│   ├── ghl/
│   ├── bigquery/
│   └── looker_studio/
├── api/                          # API layer (enhanced)
│   ├── __init__.py
│   ├── v1/                       # API versioning
│   │   ├── auth/
│   │   ├── users/
│   │   ├── pipelines/
│   │   └── integrations/
│   └── webhooks/                 # Webhook handlers
├── workers/                      # Background job workers
│   ├── __init__.py
│   ├── pipeline_runner.py
│   ├── data_ingestion.py
│   └── report_generator.py
├── admin/                        # Admin interface (enhanced)
├── web/                          # Web interface
│   ├── __init__.py
│   ├── dashboard/
│   ├── pipelines/
│   └── reports/
└── shared/                       # Shared components
    ├── __init__.py
    ├── database/
    ├── cache/
    ├── monitoring/
    └── utils/
```

### **2. Core Data Models**

#### **User Management (Refactored)**
```python
# app/core/users/models.py
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    company_name = db.Column(db.String(128))
    phone_number = db.Column(db.String(20), nullable=True)
    
    # Authentication
    password_hash = db.Column(db.String(128))
    google_id = db.Column(db.String(128), unique=True, nullable=True)
    auth_provider = db.Column(db.String(20), default='local')
    
    # Status and permissions
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    organizations = db.relationship('Organization', backref='owner', lazy='dynamic')
    pipelines = db.relationship('Pipeline', backref='user', lazy='dynamic')
```

#### **Organization Management**
```python
# app/core/users/models.py
class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    slug = db.Column(db.String(128), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Settings
    timezone = db.Column(db.String(50), default='UTC')
    currency = db.Column(db.String(3), default='USD')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = db.relationship('OrganizationMember', backref='organization', lazy='dynamic')
    data_sources = db.relationship('DataSource', backref='organization', lazy='dynamic')
    pipelines = db.relationship('Pipeline', backref='organization', lazy='dynamic')
```

#### **Data Pipeline Models**
```python
# app/pipelines/models.py
class DataSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'google_ads', 'meta_ads', etc.
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    
    # Connection details (encrypted)
    credentials = db.Column(db.Text)  # JSON encrypted credentials
    config = db.Column(db.Text)      # JSON configuration
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_sync = db.Column(db.DateTime)
    sync_status = db.Column(db.String(20), default='pending')  # 'success', 'error', 'running'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Pipeline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    
    # Pipeline configuration
    source_id = db.Column(db.Integer, db.ForeignKey('data_source.id'))
    destination_id = db.Column(db.Integer, db.ForeignKey('data_destination.id'))
    schedule = db.Column(db.String(100))  # Cron expression
    
    # Processing configuration
    transformations = db.Column(db.Text)  # JSON transformation rules
    filters = db.Column(db.Text)          # JSON filter rules
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='draft')  # 'draft', 'active', 'paused', 'error'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    runs = db.relationship('PipelineRun', backref='pipeline', lazy='dynamic')

class DataDestination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'bigquery', 'postgres', 'snowflake'
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    
    # Connection details (encrypted)
    credentials = db.Column(db.Text)
    config = db.Column(db.Text)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PipelineRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pipeline_id = db.Column(db.Integer, db.ForeignKey('pipeline.id'))
    
    # Execution details
    status = db.Column(db.String(20), default='running')  # 'running', 'success', 'error', 'cancelled'
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Results
    records_processed = db.Column(db.Integer, default=0)
    records_success = db.Column(db.Integer, default=0)
    records_error = db.Column(db.Integer, default=0)
    
    # Logs and errors
    logs = db.Column(db.Text)
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### **3. Service Layer Architecture**

#### **Data Source Connectors**
```python
# app/integrations/base.py
from abc import ABC, abstractmethod

class BaseConnector(ABC):
    def __init__(self, credentials: dict, config: dict):
        self.credentials = credentials
        self.config = config
    
    @abstractmethod
    def authenticate(self) -> bool:
        pass
    
    @abstractmethod
    def fetch_data(self, date_range: tuple) -> list:
        pass
    
    @abstractmethod
    def get_schema(self) -> dict:
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        pass

# app/integrations/google_ads/connector.py
class GoogleAdsConnector(BaseConnector):
    def authenticate(self) -> bool:
        # Google Ads API authentication
        pass
    
    def fetch_data(self, date_range: tuple) -> list:
        # Fetch campaign, ad group, keyword data
        pass
```

#### **Pipeline Orchestration**
```python
# app/pipelines/orchestration/scheduler.py
import celery
from app.pipelines.models import Pipeline, PipelineRun

@celery.task
def run_pipeline(pipeline_id: int):
    pipeline = Pipeline.query.get(pipeline_id)
    run = PipelineRun(pipeline_id=pipeline_id)
    
    try:
        # Execute pipeline
        connector = get_connector(pipeline.source)
        data = connector.fetch_data()
        
        # Process data
        processed_data = process_data(data, pipeline.transformations)
        
        # Send to destination
        destination = get_destination(pipeline.destination)
        destination.load_data(processed_data)
        
        run.status = 'success'
        run.records_processed = len(data)
        
    except Exception as e:
        run.status = 'error'
        run.error_message = str(e)
    
    finally:
        run.completed_at = datetime.utcnow()
        db.session.add(run)
        db.session.commit()
```

### **4. API Architecture**

#### **RESTful API with Versioning**
```python
# app/api/v1/pipelines/routes.py
from flask import Blueprint, request, jsonify
from app.pipelines.services import PipelineService

bp = Blueprint('pipelines_api', __name__)

@bp.route('/pipelines', methods=['GET'])
@jwt_required()
def list_pipelines():
    pipelines = PipelineService.get_user_pipelines(current_user.id)
    return jsonify([p.to_dict() for p in pipelines])

@bp.route('/pipelines', methods=['POST'])
@jwt_required()
def create_pipeline():
    data = request.get_json()
    pipeline = PipelineService.create_pipeline(current_user.id, data)
    return jsonify(pipeline.to_dict()), 201

@bp.route('/pipelines/<int:pipeline_id>/run', methods=['POST'])
@jwt_required()
def trigger_pipeline_run(pipeline_id):
    run = PipelineService.trigger_run(pipeline_id, current_user.id)
    return jsonify(run.to_dict()), 202
```

### **5. Background Job Processing**

#### **Celery Integration**
```python
# app/workers/__init__.py
from celery import Celery

def create_celery_app(app=None):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# app/workers/pipeline_runner.py
from app.workers import celery
from app.pipelines.services import PipelineService

@celery.task
def run_scheduled_pipelines():
    """Run all pipelines that are scheduled to run"""
    pipelines = PipelineService.get_scheduled_pipelines()
    for pipeline in pipelines:
        run_pipeline.delay(pipeline.id)

@celery.task
def run_pipeline(pipeline_id):
    """Execute a single pipeline"""
    return PipelineService.execute_pipeline(pipeline_id)
```

## 🚀 **Implementation Phases**

### **Phase 1: Foundation Refactor (Week 1-2)**
1. **Restructure codebase** into domain-driven architecture
2. **Separate User model** from data pipeline concerns
3. **Create Organization model** for multi-tenancy
4. **Set up service layer** patterns
5. **Implement basic API versioning**

### **Phase 2: Core Pipeline Infrastructure (Week 3-4)**
1. **Create pipeline data models**
2. **Implement base connector interface**
3. **Set up Celery for background jobs**
4. **Create pipeline orchestration service**
5. **Build basic pipeline CRUD operations**

### **Phase 3: Data Source Integrations (Week 5-8)**
1. **Google Ads connector**
2. **Meta Ads connector**
3. **CallRail connector**
4. **GHL connector**
5. **BigQuery destination**

### **Phase 4: Advanced Features (Week 9-12)**
1. **Data transformation engine**
2. **Pipeline monitoring and alerting**
3. **Looker Studio integration**
4. **Advanced scheduling**
5. **Performance optimization**

## 🛠️ **Technology Stack Additions**

### **Background Processing**
- **Celery** + **Redis**: For background job processing
- **Celery Beat**: For scheduled pipeline runs
- **Flower**: For monitoring background jobs

### **Data Processing**
- **Pandas**: For data transformation
- **Apache Airflow** (future): For complex workflow orchestration
- **dbt** (future): For data transformation

### **Monitoring & Observability**
- **Prometheus** + **Grafana**: For metrics and monitoring
- **Sentry**: For error tracking
- **Structured logging**: For better debugging

### **Caching & Performance**
- **Redis**: For caching and session storage
- **Connection pooling**: For database performance
- **Query optimization**: For large datasets

## 📋 **Migration Strategy**

### **1. Gradual Migration**
- Keep existing functionality working
- Migrate one domain at a time
- Use feature flags for new functionality

### **2. Database Migration**
- Create new tables alongside existing ones
- Migrate data gradually
- Remove old columns after migration complete

### **3. API Backwards Compatibility**
- Maintain existing endpoints during transition
- Version new APIs properly
- Deprecate old endpoints gradually

## 🎯 **Success Metrics**

### **Technical Metrics**
- **Code maintainability**: Reduced cyclomatic complexity
- **Test coverage**: >80% for core business logic
- **Performance**: <2s API response times
- **Reliability**: >99.9% uptime for pipeline execution

### **Business Metrics**
- **User adoption**: Pipeline creation and usage
- **Data volume**: Records processed per day
- **Integration coverage**: Number of supported data sources
- **Customer satisfaction**: Support ticket reduction

## 🔄 **Next Steps**

1. **Review and approve** this architecture plan
2. **Create detailed implementation tickets** for Phase 1
3. **Set up development environment** with new dependencies
4. **Begin foundation refactor** with User/Organization separation
5. **Implement CI/CD updates** for new architecture

This architecture will transform your application from a simple user management system into a robust, scalable data pipeline platform ready for enterprise use.

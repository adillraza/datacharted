# 📊 DataCharted - Data Pipeline Platform

A comprehensive data pipeline platform that enables users to connect multiple data sources, run automated data ingestion, and create powerful analytics dashboards.

## 🚀 **Vision**

DataCharted transforms how businesses handle their data by providing:
- **Multi-source data connections** (Google Ads, Meta Ads, CallRail, GHL, etc.)
- **Automated data pipelines** with scheduling and monitoring
- **Flexible data destinations** (BigQuery, PostgreSQL, Snowflake)
- **Integrated reporting** with Looker Studio and custom dashboards
- **Enterprise-grade reliability** with monitoring and alerting

## 🏗️ **Current Status**

- ✅ **User Management**: Complete authentication system with Google OAuth
- ✅ **Admin Panel**: User management and system administration
- ✅ **Database Migrations**: Robust schema change management
- ✅ **Deployment Pipeline**: Automated CI/CD with health checks
- 🚧 **Data Pipeline Core**: In development (see [Architecture Plan](docs/architecture/ARCHITECTURE_REFACTOR_PLAN.md))

## 🛠️ **Technology Stack**

### **Backend**
- **Flask**: Web framework with blueprints
- **SQLAlchemy**: ORM with Flask-Migrate for schema management
- **PostgreSQL/SQLite**: Database (production/development)
- **Celery + Redis**: Background job processing (planned)

### **Frontend**
- **Bootstrap 5**: Responsive UI framework
- **Jinja2**: Server-side templating
- **JavaScript**: Interactive components

### **Infrastructure**
- **Nginx**: Reverse proxy with SSL termination
- **Gunicorn**: WSGI server
- **GitHub Actions**: CI/CD pipeline
- **DigitalOcean**: VPS hosting

## 🚀 **Quick Start**

### **Development Setup**
```bash
# Clone repository
git clone https://github.com/adillraza/datacharted.git
cd datacharted

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
flask db upgrade

# Run development server
python run.py
```

### **Production Deployment**
See [Deployment Guide](docs/deployment/BULLETPROOF_DEPLOYMENT_GUIDE.md) for complete production setup instructions.

## 📚 **Documentation**

### **Architecture & Development**
- [Architecture Refactor Plan](docs/architecture/ARCHITECTURE_REFACTOR_PLAN.md) - Future platform architecture
- [Codebase Cleanup Plan](docs/architecture/CODEBASE_CLEANUP_PLAN.md) - Code organization improvements
- [Development Setup](docs/development/DEVELOPMENT.md) - Local development guide
- [Google OAuth Setup](docs/development/GOOGLE_OAUTH_SETUP.md) - OAuth integration guide

### **Deployment & Operations**
- [Deployment Guide](docs/deployment/BULLETPROOF_DEPLOYMENT_GUIDE.md) - Production deployment
- [Database Migrations](docs/deployment/DATABASE_SCHEMA_CHANGES_GUIDE.md) - Schema change management
- [Database Safety](docs/deployment/DATABASE_SAFETY_DEPLOYMENT_GUIDE.md) - Data protection during deployments
- [SEO Optimization](docs/deployment/SEO_OPTIMIZATION_PLAN.md) - Search engine optimization

## 🔧 **Key Features**

### **Current Features**
- **User Authentication**: Email/password and Google OAuth
- **User Management**: Profile management with admin controls
- **Admin Panel**: User administration and system monitoring
- **Responsive Design**: Mobile-friendly interface
- **Email Integration**: Welcome emails and password reset
- **Database Migrations**: Safe schema changes with rollback capability

### **Planned Features** (See [Architecture Plan](docs/architecture/ARCHITECTURE_REFACTOR_PLAN.md))
- **Data Source Connectors**: Google Ads, Meta Ads, CallRail, GHL
- **Pipeline Orchestration**: Scheduled data ingestion and processing
- **Data Destinations**: BigQuery, PostgreSQL, Snowflake integration
- **Transformation Engine**: Data cleaning and transformation
- **Monitoring & Alerting**: Pipeline health and performance monitoring
- **Report Builder**: Custom dashboard and report creation

## 🏛️ **Architecture Overview**

### **Current Structure**
```
app/
├── auth/           # Authentication (login, registration, OAuth)
├── admin/          # Admin panel (user management)
├── main/           # Main application routes
├── api/            # API endpoints
├── models.py       # Database models
└── templates/      # Jinja2 templates
```

### **Planned Structure** (Domain-Driven Design)
```
app/
├── core/           # Core business domains (auth, users)
├── pipelines/      # Data pipeline domain
├── integrations/   # External service integrations
├── api/            # Versioned API layer
├── workers/        # Background job processing
└── shared/         # Shared utilities and components
```

## 🧪 **Testing**

```bash
# Run tests (when implemented)
python -m pytest

# Run with coverage
python -m pytest --cov=app
```

## 📊 **Database Schema**

### **Current Models**
- **User**: User accounts with authentication and profile data
- **Organization**: Multi-tenant organization support (planned)
- **Pipeline**: Data pipeline definitions (planned)
- **DataSource**: External data source connections (planned)

See [Database Schema Documentation](docs/architecture/database-schema.md) for detailed schema information.

## 🚀 **Deployment**

### **Production Environment**
- **URL**: https://datacharted.com
- **Admin Panel**: https://datacharted.com/admin
- **API**: https://datacharted.com/api/v1

### **Deployment Process**
1. Push to `main` branch
2. GitHub Actions triggers deployment
3. Automated database migrations
4. Health checks and verification
5. Service restart and monitoring

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 **License**

This project is proprietary software. All rights reserved.

## 📞 **Support**

For support and questions:
- **Email**: support@datacharted.com
- **Documentation**: [docs/](docs/)
- **Issues**: GitHub Issues (for development team)

---

**🎯 Building the future of data pipeline automation!**
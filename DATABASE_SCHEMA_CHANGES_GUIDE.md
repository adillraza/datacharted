# 🗄️ Database Schema Changes & Migration Guide

## ✅ **Your Migration System is Already Set Up!**

Your Flask application uses **Flask-Migrate** (which uses **Alembic**) to handle all database schema changes safely. Here's how it works:

## 🔧 **How Database Schema Changes Work**

### **✅ Current Migration Setup**
- ✅ **Flask-Migrate**: Installed and configured
- ✅ **Migration Directory**: `migrations/` folder exists
- ✅ **Existing Migrations**: 3 migrations already applied
- ✅ **Deployment Integration**: Automatic migration during deployment

### **📋 Existing Migrations**
```
migrations/versions/
├── efaa4db08375_add_google_oauth_fields_to_user_model.py
├── d23e4c7acdcc_add_admin_fields_to_user_model.py
└── c73eb26d576f_remove_username_field_from_user_model.py
```

## 🚀 **Step-by-Step: Making Schema Changes**

### **1. Modify Your Model**
Edit `app/models.py` to add/remove/modify fields:

```python
# Example: Adding a new field to User model
class User(UserMixin, db.Model):
    # ... existing fields ...
    
    # NEW FIELD EXAMPLE
    phone_number = db.Column(db.String(20), nullable=True)
    subscription_tier = db.Column(db.String(20), default='free')
    
    # MODIFY EXISTING FIELD EXAMPLE
    company_name = db.Column(db.String(256))  # Changed from 128 to 256
```

### **2. Generate Migration**
Run this command locally to create the migration:

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # or python -m venv venv && source venv/bin/activate

# Set Flask app
export FLASK_APP=run.py

# Generate migration automatically
flask db migrate -m "Add phone number and subscription tier to User"
```

### **3. Review the Generated Migration**
Flask-Migrate will create a new file in `migrations/versions/` like:
```python
# migrations/versions/abc123_add_phone_number_and_subscription_tier_to_user.py

def upgrade():
    # Add new columns
    op.add_column('user', sa.Column('phone_number', sa.String(length=20), nullable=True))
    op.add_column('user', sa.Column('subscription_tier', sa.String(length=20), nullable=True))
    
    # Modify existing column
    op.alter_column('user', 'company_name', type_=sa.String(length=256))

def downgrade():
    # Reverse the changes
    op.alter_column('user', 'company_name', type_=sa.String(length=128))
    op.drop_column('user', 'subscription_tier')
    op.drop_column('user', 'phone_number')
```

### **4. Test Migration Locally (Optional)**
```bash
# Apply migration locally to test
flask db upgrade

# If you need to rollback for testing
flask db downgrade  # Goes back one migration
```

### **5. Commit and Deploy**
```bash
# Add the migration file to git
git add migrations/versions/your_new_migration_file.py
git add app/models.py  # Your model changes

# Commit the changes
git commit -m "Add phone number and subscription tier fields to User model"

# Push to deploy (triggers automatic migration on server)
git push origin main
```

## 🛡️ **What Happens During Deployment**

### **✅ Automatic Migration Process**
When you push code, the deployment script automatically:

1. **📦 Backs up database** (keeps 3 backups)
2. **🔍 Checks current migration**: `flask db current`
3. **⬆️ Applies new migrations**: `flask db upgrade`
4. **✅ Verifies success**: Confirms migration completed
5. **🔄 Restarts service**: Applies changes to live app

### **✅ Safety Features**
- **Database Backup**: Automatic backup before migration
- **Rollback Capability**: Can restore from backup if needed
- **Migration Retry**: If migration fails, attempts recovery
- **Data Preservation**: Existing data is never lost
- **Error Handling**: Deployment stops if migration fails

## 📊 **Common Schema Change Examples**

### **Adding a New Table**
```python
# In app/models.py
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### **Adding a Field to Existing Table**
```python
# In User model
class User(UserMixin, db.Model):
    # ... existing fields ...
    
    # New field
    profile_picture = db.Column(db.String(512), nullable=True)
```

### **Modifying an Existing Field**
```python
# Change field size or type
email = db.Column(db.String(255), unique=True, nullable=False)  # Was 120
```

### **Adding an Index**
```python
# Add index for performance
email = db.Column(db.String(120), unique=True, nullable=False, index=True)
```

### **Removing a Field**
```python
# Simply remove the field from the model
# Flask-Migrate will detect and create appropriate migration
```

## 🔄 **Migration Commands Reference**

### **Local Development**
```bash
# Generate new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback one migration
flask db downgrade

# Show current migration
flask db current

# Show migration history
flask db history

# Show specific migration
flask db show <revision_id>
```

### **Production (Automatic via Deployment)**
```bash
# These happen automatically during deployment:
flask db current    # Check current state
flask db upgrade    # Apply new migrations
```

## ⚠️ **Best Practices & Safety Tips**

### **✅ Do's**
- ✅ **Always test locally first**: Run migration on local copy
- ✅ **Use descriptive messages**: Clear migration descriptions
- ✅ **Review generated migrations**: Check before committing
- ✅ **Backup before major changes**: Especially for data transformations
- ✅ **Add default values**: For new non-nullable fields

### **❌ Don'ts**
- ❌ **Don't edit existing migrations**: Create new ones instead
- ❌ **Don't skip migration generation**: Always use `flask db migrate`
- ❌ **Don't modify production DB directly**: Use migrations only
- ❌ **Don't remove migrations**: They're part of version history

### **🚨 Special Cases**

#### **Adding Non-Nullable Field to Existing Table**
```python
# BAD: Will fail if table has existing data
new_field = db.Column(db.String(50), nullable=False)

# GOOD: Add with default value
new_field = db.Column(db.String(50), nullable=False, default='default_value')

# OR: Add as nullable first, populate, then make non-nullable
new_field = db.Column(db.String(50), nullable=True)
```

#### **Data Transformations**
If you need to transform existing data, create a migration with custom code:
```python
def upgrade():
    # Add new column
    op.add_column('user', sa.Column('full_name', sa.String(128)))
    
    # Transform existing data
    connection = op.get_bind()
    connection.execute(
        "UPDATE user SET full_name = first_name || ' ' || last_name"
    )
```

## 🎯 **Example: Complete Workflow**

### **Scenario**: Add a "subscription_tier" field to User model

#### **Step 1**: Modify Model
```python
# app/models.py
class User(UserMixin, db.Model):
    # ... existing fields ...
    subscription_tier = db.Column(db.String(20), default='free', nullable=False)
```

#### **Step 2**: Generate Migration
```bash
flask db migrate -m "Add subscription tier to User model"
```

#### **Step 3**: Review Generated Migration
```python
# migrations/versions/abc123_add_subscription_tier_to_user_model.py
def upgrade():
    op.add_column('user', sa.Column('subscription_tier', sa.String(20), 
                                   nullable=False, server_default='free'))

def downgrade():
    op.drop_column('user', 'subscription_tier')
```

#### **Step 4**: Test Locally
```bash
flask db upgrade  # Apply migration
# Test your application
```

#### **Step 5**: Deploy
```bash
git add migrations/versions/abc123_add_subscription_tier_to_user_model.py
git add app/models.py
git commit -m "Add subscription tier field to User model"
git push origin main  # Triggers automatic deployment with migration
```

#### **Step 6**: Verify Deployment
- Check GitHub Actions for successful deployment
- Verify field exists in production
- Test application functionality

## 📊 **Migration Status Monitoring**

### **Check Migration Status**
```bash
# On server (via SSH)
cd /opt/datacharted-app
source venv/bin/activate
export FLASK_APP=run.py
flask db current  # Shows current migration
flask db history  # Shows all migrations
```

### **Deployment Logs**
Check GitHub Actions logs for migration details:
- Migration backup creation
- Current migration status
- Migration application results
- New migration status

## 🎉 **Summary**

### **✅ Your System is Ready for Schema Changes!**

**🛡️ Safe Process:**
1. **Modify models** → **Generate migration** → **Test locally** → **Deploy**
2. **Automatic backups** before each migration
3. **Data preservation** guaranteed
4. **Rollback capability** if needed

**🚀 Deployment Integration:**
- **Automatic migration** during deployment
- **Error handling** and recovery
- **Health verification** after changes
- **Service restart** to apply changes

**📈 Scalable:**
- **Version control** for all schema changes
- **Team collaboration** through migration files
- **Production safety** with backup system
- **Rollback capability** for emergency recovery

**🎯 You can now confidently make any database schema changes - the system will handle them safely and automatically!**

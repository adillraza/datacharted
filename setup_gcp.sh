#!/bin/bash

# DataCharted GCP Setup Script
# This script sets up the service account and permissions for BigQuery project management

set -e  # Exit on any error

# Configuration
PROJECT_ID="datacharted"
ORG_ID="777274882597"
BILLING_ACCOUNT_ID="01CC60-C71628-CF586D"
SA_NAME="datacharted-resource-manager"
SA_DISPLAY_NAME="DataCharted Resource Manager"
SA_DESCRIPTION="Service account for managing user BigQuery projects and folders"

echo "🚀 Setting up DataCharted GCP Resources..."
echo "Project: $PROJECT_ID"
echo "Organization: $ORG_ID"
echo "Billing Account: $BILLING_ACCOUNT_ID"
echo ""

# Step 1: Set the project
echo "📋 Step 1: Setting active project..."
gcloud config set project $PROJECT_ID
echo "✅ Active project set to $PROJECT_ID"
echo ""

# Step 2: Enable required APIs
echo "🔌 Step 2: Enabling required APIs..."
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable iam.googleapis.com
gcloud services enable serviceusage.googleapis.com
gcloud services enable cloudbilling.googleapis.com
echo "✅ APIs enabled successfully"
echo ""

# Step 3: Create service account
echo "👤 Step 3: Creating service account..."
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

# Check if service account already exists
if gcloud iam service-accounts describe $SA_EMAIL --quiet 2>/dev/null; then
    echo "⚠️  Service account $SA_EMAIL already exists, skipping creation"
else
    gcloud iam service-accounts create $SA_NAME \
        --display-name="$SA_DISPLAY_NAME" \
        --description="$SA_DESCRIPTION"
    echo "✅ Service account created: $SA_EMAIL"
fi
echo ""

# Step 4: Grant organization-level permissions
echo "🔐 Step 4: Granting organization-level permissions..."

# Array of roles to grant
roles=(
    "roles/resourcemanager.folderCreator"
    "roles/resourcemanager.projectCreator"
    "roles/billing.user"
    "roles/serviceusage.serviceUsageAdmin"
    "roles/iam.serviceAccountAdmin"
    "roles/bigquery.admin"
)

for role in "${roles[@]}"; do
    echo "  Granting $role..."
    gcloud organizations add-iam-policy-binding $ORG_ID \
        --member="serviceAccount:$SA_EMAIL" \
        --role="$role" \
        --quiet
done

echo "✅ Organization-level permissions granted"
echo ""

# Step 5: Grant billing account permissions
echo "💳 Step 5: Granting billing account permissions..."
gcloud beta billing accounts add-iam-policy-binding $BILLING_ACCOUNT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/billing.user" \
    --quiet
echo "✅ Billing account permissions granted"
echo ""

# Step 6: Create and download service account key
echo "🔑 Step 6: Creating service account key..."
KEY_FILE="datacharted-sa-key.json"

if [ -f "$KEY_FILE" ]; then
    echo "⚠️  Key file $KEY_FILE already exists"
    read -p "Do you want to create a new key? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Backup existing key
        mv "$KEY_FILE" "$KEY_FILE.backup.$(date +%s)"
        echo "📋 Backed up existing key file"
    else
        echo "📋 Using existing key file"
        KEY_FILE_EXISTS=true
    fi
fi

if [ "$KEY_FILE_EXISTS" != true ]; then
    gcloud iam service-accounts keys create $KEY_FILE \
        --iam-account=$SA_EMAIL
    echo "✅ Service account key created: $KEY_FILE"
fi
echo ""

# Step 7: Display setup summary
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Summary:"
echo "  Service Account: $SA_EMAIL"
echo "  Key File: $(pwd)/$KEY_FILE"
echo "  Organization ID: $ORG_ID"
echo "  Billing Account: $BILLING_ACCOUNT_ID"
echo ""

# Step 8: Generate .env configuration
echo "⚙️  Step 8: Generating environment configuration..."
cat > .env.gcp << EOF
# Google Cloud Platform Configuration for DataCharted
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/$KEY_FILE
GCP_BILLING_ACCOUNT_ID=$BILLING_ACCOUNT_ID
GCP_ORGANIZATION_ID=$ORG_ID
EOF

echo "✅ Environment configuration saved to .env.gcp"
echo ""

echo "📝 Next steps:"
echo "1. Add the contents of .env.gcp to your .env file:"
echo "   cat .env.gcp >> .env"
echo ""
echo "2. Test the setup:"
echo "   python test_gcp_setup.py"
echo ""
echo "3. Run database migration:"
echo "   flask db migrate -m 'Add folder fields to User model'"
echo "   flask db upgrade"
echo ""
echo "4. Start your application and test BigQuery project creation!"
echo ""

# Step 9: Verify permissions (optional)
echo "🔍 Step 9: Verifying permissions..."
echo "Testing organization access..."

# Test if we can list folders (this verifies permissions)
if gcloud resource-manager folders list --organization=$ORG_ID --limit=1 --quiet > /dev/null 2>&1; then
    echo "✅ Organization access verified"
else
    echo "⚠️  Could not verify organization access - this might be normal if no folders exist yet"
fi

echo ""
echo "🚀 Setup script completed! Your DataCharted GCP environment is ready."


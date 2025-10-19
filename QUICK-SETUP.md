# Quick Google Cloud Setup

## 1. Get Your Project ID

```bash
# Check current project
gcloud config get-value project

# If no project is set, list available projects
gcloud projects list

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

## 2. Create a .env file

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
nano .env
```

Set these values in your `.env` file:
```bash
GOOGLE_CLOUD_PROJECT=your-actual-project-id
GOOGLE_API_KEY=your-actual-api-key
DATABASE_URL=your-actual-database-url
GCS_BUCKET=your-actual-bucket-name
```

## 3. Authenticate Locally

```bash
# Set up application default credentials
gcloud auth application-default login
```

## 4. Create GCS Bucket

```bash
# Create bucket (replace with your desired name)
gsutil mb gs://your-bucket-name

# Make bucket publicly readable (optional)
gsutil iam ch allUsers:objectViewer gs://your-bucket-name
```

## 5. Test the Setup

```bash
# Test GCS connection
python test-gcs.py

# Test the API
curl http://localhost:8001/health
```

## Quick Commands

```bash
# Get project ID
PROJECT_ID=$(gcloud config get-value project)
echo "Project ID: $PROJECT_ID"

# Create bucket with project-specific name
BUCKET_NAME="${PROJECT_ID}-classifier-images"
gsutil mb gs://$BUCKET_NAME
echo "Created bucket: $BUCKET_NAME"

# Update .env file
echo "GCS_BUCKET=$BUCKET_NAME" >> .env
echo "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" >> .env
```
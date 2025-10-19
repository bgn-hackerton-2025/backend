# Google Cloud Storage Setup Guide

## Overview
The application now uses Google Cloud Storage (GCS) instead of Amazon S3 for storing uploaded inventory images.

## Prerequisites

1. **Google Cloud Project** with the following APIs enabled:
   - Cloud Storage API
   - Cloud Run API (if not already enabled)

2. **Google Cloud Storage Bucket** created in your project

3. **Service Account** with appropriate permissions (automatically handled on Cloud Run)

## Setup Steps

### 1. Create a Google Cloud Storage Bucket

```bash
# Create a bucket (replace with your desired bucket name and project ID)
gsutil mb gs://your-bucket-name

# Set appropriate permissions (example for public read access)
gsutil iam ch allUsers:objectViewer gs://your-bucket-name
```

### 2. Environment Variables

Set the following environment variable:

```bash
# Required: Your GCS bucket name
GCS_BUCKET=your-bucket-name

# Optional: Google Cloud Project ID (auto-detected on Cloud Run)
GOOGLE_CLOUD_PROJECT=your-project-id
```

### 3. Authentication

#### On Cloud Run (Production)
- Authentication is handled automatically by the Cloud Run service account
- No additional configuration needed

#### Local Development
Set up Application Default Credentials:

```bash
# Install Google Cloud CLI if not already installed
# Then authenticate:
gcloud auth application-default login
```

Or use a service account key file:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

## How It Works

### File Upload Process
1. **Image Processing**: Image is received and processed by Gemini AI
2. **Storage Path**: Files are stored with the pattern: `inventory/{provider_id}/{inventory_id}.jpg`
3. **Upload**: Image is uploaded to GCS with metadata
4. **Database**: Image URL and storage path are saved to the database

### Storage Structure
```
your-bucket-name/
├── inventory/
│   ├── {provider-id-1}/
│   │   ├── {inventory-id-1}.jpg
│   │   ├── {inventory-id-2}.jpg
│   │   └── ...
│   ├── {provider-id-2}/
│   │   ├── {inventory-id-3}.jpg
│   │   └── ...
│   └── ...
```

### Generated URLs
Images are accessible via public URLs:
```
https://storage.googleapis.com/your-bucket-name/inventory/{provider_id}/{inventory_id}.jpg
```

## Security Considerations

### Public vs Private Access
- **Public Access**: Images are publicly accessible via URL (current setup)
- **Private Access**: Requires signed URLs for access

To make bucket private:
```bash
# Remove public access
gsutil iam ch -d allUsers:objectViewer gs://your-bucket-name
```

### Signed URLs (for private buckets)
If you need private access, modify the code to generate signed URLs:

```python
from datetime import timedelta

# Generate a signed URL valid for 1 hour
signed_url = blob.generate_signed_url(
    version="v4",
    expiration=timedelta(hours=1),
    method="GET"
)
```

## Migration from S3

If migrating from existing S3 setup:

1. **Data Migration** (if needed):
   ```bash
   # Copy from S3 to GCS
   gsutil -m cp -r s3://your-s3-bucket/* gs://your-gcs-bucket/
   ```

2. **Environment Variables**: Replace AWS variables with GCS variables
3. **Deploy**: The code changes handle the rest automatically

## Cost Optimization

### Storage Classes
Consider using different storage classes for cost optimization:
- **Standard**: Frequently accessed data
- **Nearline**: Data accessed less than once per month
- **Coldline**: Data accessed less than once per quarter

### Lifecycle Policies
Set up lifecycle policies to automatically transition or delete old files:

```bash
# Example: Delete files older than 365 days
gsutil lifecycle set lifecycle.json gs://your-bucket-name
```

## Monitoring and Logging

### Cloud Logging
Upload operations are logged automatically. Check Cloud Logging for:
- Upload success/failure messages
- Error details

### Cloud Monitoring
Monitor bucket usage, request counts, and costs in Cloud Monitoring.

## Troubleshooting

### Common Issues

1. **"GCS bucket not configured"**
   - Ensure `GCS_BUCKET` environment variable is set

2. **"Permission denied"**
   - Check service account permissions
   - Ensure Cloud Storage API is enabled

3. **"Bucket not found"**
   - Verify bucket name is correct
   - Ensure bucket exists in the same project

### Debug Commands

```bash
# Check if bucket exists
gsutil ls gs://your-bucket-name

# List bucket permissions
gsutil iam get gs://your-bucket-name

# Test upload
echo "test" | gsutil cp - gs://your-bucket-name/test.txt
```
# Google Cloud Run Deployment Instructions

## Prerequisites
1. Make sure you have the Google Cloud CLI installed and authenticated
2. Have your Google Generative AI API key ready

## Deployment Steps

### Option 1: Deploy with gcloud command (Recommended)
```bash
# Build and deploy to Cloud Run with environment variable
gcloud run deploy classifier \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_actual_api_key_here \
  --port 8080
```

### Option 2: Use Cloud Build with environment variables
1. First, store your API key in Google Secret Manager:
```bash
# Create a secret
echo -n "your_actual_api_key_here" | gcloud secrets create google-api-key --data-file=-
```

2. Then deploy with the secret:
```bash
gcloud run deploy classifier \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets GOOGLE_API_KEY=google-api-key:latest \
  --port 8080
```

### Option 3: Set environment variable in Cloud Console
1. Deploy first: `gcloud run deploy classifier --source . --platform managed --region us-central1 --allow-unauthenticated`
2. Go to Google Cloud Console → Cloud Run → Select your service → Edit & Deploy New Revision
3. Go to "Variables & Secrets" tab
4. Add environment variable: `GOOGLE_API_KEY` with your API key value
5. Deploy the revision

## Important Notes
- Replace `your_actual_api_key_here` with your real Google Generative AI API key
- Make sure your API key has the necessary permissions for the Generative AI API
- The Dockerfile now uses dynamic PORT environment variable for Cloud Run compatibility
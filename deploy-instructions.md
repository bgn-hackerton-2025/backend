# Google Cloud Run Deployment with Build-Time Migrations

## Prerequisites
1. Google Cloud CLI installed and authenticated
2. Google Generative AI API key
3. Cloud SQL PostgreSQL instance set up
4. Database connection string ready

## Build-Time Migration Approach

**Migrations now run during Docker build**, ensuring:
- ✅ Database schema is updated before deployment
- ✅ Faster container startup (no migration delays)
- ✅ Build fails if migrations fail (prevents bad deployments)
- ✅ Consistent database state across deployments

## Deployment Methods

### Method 1: Manual Build and Deploy

```bash
# Build with migrations
docker build \
  --build-arg DATABASE_URL="your_postgres_connection_string" \
  -t gcr.io/PROJECT_ID/classifier .

# Push to registry
docker push gcr.io/PROJECT_ID/classifier

# Deploy to Cloud Run
gcloud run deploy classifier \
  --image gcr.io/PROJECT_ID/classifier \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_api_key,DATABASE_URL=your_postgres_connection_string
```

### Method 2: Cloud Build (Recommended)

```bash
# Deploy using Cloud Build with substitution variables
gcloud builds submit \
  --config cloudbuild.yaml \
  --substitutions _DATABASE_URL="your_postgres_connection_string",_GOOGLE_API_KEY="your_api_key"
```

### Method 3: Direct gcloud deploy with build args

```bash
# This approach builds in Cloud Build with the DATABASE_URL
gcloud run deploy classifier \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_api_key,DATABASE_URL=your_postgres_connection_string \
  --set-build-env-vars DATABASE_URL=your_postgres_connection_string
```

## Environment Variables

### Build-Time Variables
- `DATABASE_URL`: Required during build for running migrations

### Runtime Variables  
- `GOOGLE_API_KEY`: Your Google Generative AI API key
- `DATABASE_URL`: PostgreSQL connection string (same as build-time)

## Database Connection String Format

For Cloud SQL PostgreSQL:
```
postgresql://username:password@/database?host=/cloudsql/PROJECT_ID:REGION:INSTANCE_ID
```

Or with public IP:
```
postgresql://username:password@PUBLIC_IP:5432/database
```

## Secrets Management (More Secure)

```bash
# Store secrets in Secret Manager
echo -n "your_api_key" | gcloud secrets create google-api-key --data-file=-
echo -n "your_db_url" | gcloud secrets create database-url --data-file=-

# Build with secret access
gcloud builds submit \
  --config cloudbuild.yaml \
  --substitutions _DATABASE_URL="$(gcloud secrets versions access latest --secret=database-url)",_GOOGLE_API_KEY="$(gcloud secrets versions access latest --secret=google-api-key)"
```

## Migration Process

1. **During Build**: Alembic runs `upgrade head` with provided DATABASE_URL
2. **On Deploy**: Application starts immediately (no migration delay)
3. **Verification**: Use `/health` endpoint to verify database connectivity

## Troubleshooting

### Build Failures
- Check build logs for migration errors
- Verify DATABASE_URL format and connectivity
- Ensure database exists and user has proper permissions

### Runtime Issues
- Use `/health` endpoint to check database connectivity
- Verify runtime environment variables are set correctly

## CI/CD Integration

The `cloudbuild.yaml` supports:
- Automatic builds on code changes
- Environment variable substitution
- Multi-step deployment process
- Build-time migration execution

Example trigger:
```bash
gcloud builds triggers create github \
  --repo-name=classifier \
  --repo-owner=bgn-hackerton-2025 \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --substitutions _DATABASE_URL="your_connection_string",_GOOGLE_API_KEY="your_api_key"
```
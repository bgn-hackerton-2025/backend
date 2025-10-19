# Google Cloud Run Deployment with Manual Migrations

## Prerequisites
1. Google Cloud CLI installed and authenticated
2. Google Generative AI API key
3. Cloud SQL PostgreSQL instance set up
4. Database connection string ready

## Manual Migration Approach

**Migrations are now triggered manually via API endpoint**, providing:
- ✅ Full control over when migrations run
- ✅ Ability to run migrations on live production system
- ✅ Fast deployments (no migration delays)
- ✅ Migration status monitoring via API

## Deployment Methods

### Method 1: Automatic Deployment (GitHub Push) - RECOMMENDED
Your existing Cloud Build trigger automatically deploys when you push to the `main` branch.
**This is your current setup and it works perfectly!**

### Method 2: Direct gcloud deploy (Manual).
```bash
gcloud run deploy classifier \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_api_key,DATABASE_URL=your_postgres_connection_string
```

## Running Migrations

After deployment, run migrations manually via the API:

### Trigger Migration
```bash
# Run migrations on your deployed service
curl -X POST https://your-service-url/admin/migrate

# Or using your local service for testing
curl -X POST http://localhost:8000/admin/migrate
```

### Check Migration Status
```bash
# Check current migration status
curl https://your-service-url/admin/migration-status

# Or locally
curl http://localhost:8000/admin/migration-status
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
#!/bin/bash
set -e

echo "🚀 Starting application deployment..."

# Run database migrations
echo "📊 Running database migrations..."
python migrate.py

# Start the application
echo "🌐 Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
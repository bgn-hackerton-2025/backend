#!/bin/bash
# Local test script for build-time migrations

set -e

echo "🧪 Testing build-time migration approach..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set. Please set it in .env file or environment."
    echo "Example: DATABASE_URL=postgresql://user:pass@localhost:5432/dbname"
    exit 1
fi

echo "📊 DATABASE_URL: ${DATABASE_URL}"

# Build Docker image with migration
echo "🔨 Building Docker image with migrations..."
docker build \
    --build-arg DATABASE_URL="$DATABASE_URL" \
    -t classifier-test \
    .

if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully!"
    echo "🚀 You can now run the container:"
    echo "   docker run -p 8080:8080 -e GOOGLE_API_KEY=\"\$GOOGLE_API_KEY\" -e DATABASE_URL=\"\$DATABASE_URL\" classifier-test"
else
    echo "❌ Build failed!"
    exit 1
fi
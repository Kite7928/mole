#!/bin/bash

# Railway Deployment Script for Celery Workers
# This script deploys Celery workers to Railway

set -e

echo "🚀 Starting deployment to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Initialize Railway project (if not already initialized)
if [ ! -f ".railway/config.json" ]; then
    echo "📦 Initializing Railway project..."
    railway init
fi

# Add PostgreSQL service
echo "🗄️  Adding PostgreSQL service..."
railway add postgresql

# Add Redis service
echo "🔴 Adding Redis service..."
railway add redis

# Deploy Celery Worker
echo "⚙️  Deploying Celery Worker..."
railway up --service celery-worker

# Deploy Celery Beat
echo "⏰ Deploying Celery Beat..."
railway up --service celery-beat

# Deploy Flower (monitoring)
echo "🌸 Deploying Flower..."
railway up --service flower

# Get service URLs
echo ""
echo "✅ Railway deployment complete!"
echo ""
echo "📋 Service URLs:"
railway status

echo ""
echo "🎉 Celery workers are now running on Railway!"
echo ""
echo "📝 Next steps:"
echo "1. Copy DATABASE_URL and REDIS_URL from Railway"
echo "2. Add them to your Vercel environment variables"
echo "3. Restart your Vercel deployment"
echo "4. Monitor tasks at the Flower URL"
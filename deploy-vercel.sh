#!/bin/bash

# Vercel + Cloudflare Deployment Script
# This script deploys the application to Vercel and configures Cloudflare

set -e

echo "🚀 Starting deployment to Vercel + Cloudflare..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if Wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler CLI not found. Installing..."
    npm install -g wrangler
fi

# Deploy to Vercel
echo "📦 Deploying to Vercel..."
vercel --prod

# Get the deployed URL
VERCEL_URL=$(vercel ls --prod | grep wechat-ai-writer-pro | awk '{print $2}')
echo "✅ Vercel deployment complete: https://$VERCEL_URL"

# Deploy Cloudflare Worker (optional)
if [ -d "cloudflare" ]; then
    echo "🌐 Deploying Cloudflare Worker..."
    cd cloudflare
    npm install
    wrangler deploy
    cd ..
    echo "✅ Cloudflare Worker deployed"
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Configure your Cloudflare DNS to point to Vercel"
echo "2. Set up SSL certificates in Cloudflare"
echo "3. Configure environment variables in Vercel dashboard"
echo "4. Deploy Celery workers to Railway (see deploy-railway.sh)"
echo ""
echo "🔗 Vercel URL: https://$VERCEL_URL"
echo "📚 Documentation: See DEPLOYMENT.md for more details"
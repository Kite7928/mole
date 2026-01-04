# Railway Deployment Script for Celery Workers (PowerShell)
# This script deploys Celery workers to Railway

Write-Host "🚀 Starting deployment to Railway..." -ForegroundColor Green

# Check if Railway CLI is installed
if (-not (Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Railway CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g @railway/cli
}

# Login to Railway
Write-Host "🔐 Logging into Railway..." -ForegroundColor Cyan
railway login

# Initialize Railway project (if not already initialized)
if (-not (Test-Path ".railway\config.json")) {
    Write-Host "📦 Initializing Railway project..." -ForegroundColor Cyan
    railway init
}

# Add PostgreSQL service
Write-Host "🗄️  Adding PostgreSQL service..." -ForegroundColor Cyan
railway add postgresql

# Add Redis service
Write-Host "🔴 Adding Redis service..." -ForegroundColor Cyan
railway add redis

# Deploy Celery Worker
Write-Host "⚙️  Deploying Celery Worker..." -ForegroundColor Cyan
railway up --service celery-worker

# Deploy Celery Beat
Write-Host "⏰ Deploying Celery Beat..." -ForegroundColor Cyan
railway up --service celery-beat

# Deploy Flower (monitoring)
Write-Host "🌸 Deploying Flower..." -ForegroundColor Cyan
railway up --service flower

# Get service URLs
Write-Host ""
Write-Host "✅ Railway deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Service URLs:" -ForegroundColor Cyan
railway status

Write-Host ""
Write-Host "🎉 Celery workers are now running on Railway!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. Copy DATABASE_URL and REDIS_URL from Railway"
Write-Host "2. Add them to your Vercel environment variables"
Write-Host "3. Restart your Vercel deployment"
Write-Host "4. Monitor tasks at the Flower URL"
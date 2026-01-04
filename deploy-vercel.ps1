# Vercel + Cloudflare Deployment Script (PowerShell)
# This script deploys the application to Vercel and configures Cloudflare

Write-Host "🚀 Starting deployment to Vercel + Cloudflare..." -ForegroundColor Green

# Check if Vercel CLI is installed
if (-not (Get-Command vercel -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Vercel CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g vercel
}

# Check if Wrangler is installed
if (-not (Get-Command wrangler -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Wrangler CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g wrangler
}

# Deploy to Vercel
Write-Host "📦 Deploying to Vercel..." -ForegroundColor Cyan
vercel --prod

# Get the deployed URL
$vercelOutput = vercel ls --prod
$VERCEL_URL = ($vercelOutput | Select-String "wechat-ai-writer-pro" | ForEach-Object { $_.ToString().Split(" ")[1] })
Write-Host "✅ Vercel deployment complete: https://$VERCEL_URL" -ForegroundColor Green

# Deploy Cloudflare Worker (optional)
if (Test-Path "cloudflare") {
    Write-Host "🌐 Deploying Cloudflare Worker..." -ForegroundColor Cyan
    Push-Location cloudflare
    npm install
    wrangler deploy
    Pop-Location
    Write-Host "✅ Cloudflare Worker deployed" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Configure your Cloudflare DNS to point to Vercel"
Write-Host "2. Set up SSL certificates in Cloudflare"
Write-Host "3. Configure environment variables in Vercel dashboard"
Write-Host "4. Deploy Celery workers to Railway (see deploy-railway.ps1)"
Write-Host ""
Write-Host "🔗 Vercel URL: https://$VERCEL_URL" -ForegroundColor Yellow
Write-Host "📚 Documentation: See DEPLOYMENT.md for more details" -ForegroundColor Gray
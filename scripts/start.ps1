# AI公众号自动写作助手 Pro - 启动脚本 (Windows PowerShell)

Write-Host "🚀 Starting AI公众号自动写作助手 Pro..." -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "⚠️  .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ .env file created. Please edit it with your configuration." -ForegroundColor Green
    Write-Host "⏸️  Please configure your .env file and run this script again." -ForegroundColor Yellow
    exit 1
}

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path uploads, temp, logs | Out-Null

# Start Docker Compose
Write-Host "🐳 Starting Docker containers..." -ForegroundColor Cyan
docker-compose -f docker/docker-compose.yml up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
Write-Host "🔍 Checking service status..." -ForegroundColor Cyan
docker-compose -f docker/docker-compose.yml ps

Write-Host ""
Write-Host "✅ Services started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Service URLs:" -ForegroundColor Cyan
Write-Host "   - Frontend: http://localhost:3000"
Write-Host "   - Backend API: http://localhost:8000"
Write-Host "   - API Docs: http://localhost:8000/docs"
Write-Host "   - Flower (Celery Monitor): http://localhost:5555"
Write-Host "   - Nginx: http://localhost"
Write-Host ""
Write-Host "📝 To view logs:" -ForegroundColor Cyan
Write-Host "   docker-compose -f docker/docker-compose.yml logs -f"
Write-Host ""
Write-Host "🛑 To stop services:" -ForegroundColor Cyan
Write-Host "   docker-compose -f docker/docker-compose.yml down"
Write-Host ""
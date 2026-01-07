# AI公众号自动写作助手 Pro - 构建和推送镜像脚本 (Windows PowerShell)

param(
    [string]$DockerHubUsername = "your-dockerhub-username",
    [string]$ImageName = "wechat-ai-writer-pro",
    [string]$Version = "latest"
)

$FullImageName = "${DockerHubUsername}/${ImageName}:${Version}"

Write-Host "🚀 Building Docker image: $FullImageName" -ForegroundColor Green

# Build the image
Write-Host "📦 Building image..." -ForegroundColor Cyan
docker build -t $FullImageName .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build successful!" -ForegroundColor Green

# Push to Docker Hub
Write-Host "📤 Pushing image to Docker Hub..." -ForegroundColor Cyan
docker push $FullImageName

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Push failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Push successful!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Image details:" -ForegroundColor Cyan
Write-Host "   Image: $FullImageName"
Write-Host ""
Write-Host "🚀 To pull and run on CentOS 7:" -ForegroundColor Cyan
Write-Host "   docker pull $FullImageName"
Write-Host "   docker run -d -p 3000:3000 -p 8000:8000 $FullImageName"
Write-Host ""
# Docker部署脚本 (Windows PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  AI公众号自动写作助手 Pro - Docker部署" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 构建Docker镜像
Write-Host "步骤 1/3: 构建Docker镜像..." -ForegroundColor Yellow
docker build -t wechat-ai-writer-pro:latest .

# 2. 启动服务
Write-Host "步骤 2/3: 启动服务..." -ForegroundColor Yellow
docker-compose -f docker-compose.standalone.yml up -d

# 3. 等待服务就绪
Write-Host "步骤 3/3: 等待服务就绪..." -ForegroundColor Yellow
Write-Host "等待数据库初始化..." -ForegroundColor Gray
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  部署完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "后端服务: http://localhost:8000" -ForegroundColor Cyan
Write-Host "前端服务: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Celery监控: http://localhost:5555" -ForegroundColor Cyan
Write-Host ""
Write-Host "查看日志: docker-compose -f docker-compose.standalone.yml logs -f" -ForegroundColor Gray
Write-Host "停止服务: docker-compose -f docker-compose.standalone.yml down" -ForegroundColor Gray
Write-Host ""
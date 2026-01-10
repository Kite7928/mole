# 开发环境启动脚本 (Windows PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  AI公众号自动写作助手 Pro - 开发环境" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 启动数据库服务
Write-Host "步骤 1/5: 启动数据库服务..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml up -d postgres redis

# 等待数据库就绪
Write-Host "等待数据库就绪..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# 2. 初始化数据库
Write-Host "步骤 2/5: 初始化数据库..." -ForegroundColor Yellow
cd backend
py -m init_db
cd ..

# 3. 安装后端依赖
Write-Host "步骤 3/5: 检查后端依赖..." -ForegroundColor Yellow
cd backend
py -m pip install -r requirements.txt -q
cd ..

# 4. 启动后端服务
Write-Host "步骤 4/5: 启动后端服务..." -ForegroundColor Yellow
cd backend
Start-Process -NoNewWindow -FilePath "py" -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
cd ..

# 5. 安装前端依赖
Write-Host "步骤 5/5: 检查前端依赖..." -ForegroundColor Yellow
cd frontend
if (-not (Test-Path "node_modules")) {
  npm install
}

# 启动前端服务
Write-Host "启动前端服务..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "run dev"
cd ..

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  服务启动完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "后端服务: http://localhost:8000" -ForegroundColor Cyan
Write-Host "前端服务: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止所有服务" -ForegroundColor Gray
Write-Host ""

# 等待用户中断
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null

# 停止所有服务
Write-Host "停止所有服务..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml down

# 停止Python进程
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force

# 停止Node进程
Get-Process | Where-Object {$_.ProcessName -eq "node"} | Stop-Process -Force

Write-Host "所有服务已停止" -ForegroundColor Green
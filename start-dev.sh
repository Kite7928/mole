#!/bin/bash

# 开发环境启动脚本

echo "=========================================="
echo "  AI公众号自动写作助手 Pro - 开发环境"
echo "=========================================="

# 1. 启动数据库服务
echo ""
echo "步骤 1/5: 启动数据库服务..."
docker-compose -f docker-compose.dev.yml up -d postgres redis

# 等待数据库就绪
echo "等待数据库就绪..."
sleep 5

# 2. 初始化数据库
echo ""
echo "步骤 2/5: 初始化数据库..."
cd backend
py -m init_db
cd ..

# 3. 安装后端依赖
echo ""
echo "步骤 3/5: 检查后端依赖..."
cd backend
py -m pip install -r requirements.txt -q
cd ..

# 4. 启动后端服务
echo ""
echo "步骤 4/5: 启动后端服务..."
cd backend
py -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# 5. 安装前端依赖
echo ""
echo "步骤 5/5: 检查前端依赖..."
cd frontend
if [ ! -d "node_modules" ]; then
  npm install
fi

# 启动前端服务
echo "启动前端服务..."
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================="
echo "  服务启动完成！"
echo "=========================================="
echo ""
echo "后端服务: http://localhost:8000"
echo "前端服务: http://localhost:3000"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID; docker-compose -f docker-compose.dev.yml down; exit" INT TERM

wait
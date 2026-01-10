#!/bin/bash

# Docker部署脚本

echo "=========================================="
echo "  AI公众号自动写作助手 Pro - Docker部署"
echo "=========================================="

# 1. 构建Docker镜像
echo ""
echo "步骤 1/3: 构建Docker镜像..."
docker build -t wechat-ai-writer-pro:latest .

# 2. 启动服务
echo ""
echo "步骤 2/3: 启动服务..."
docker-compose -f docker-compose.standalone.yml up -d

# 3. 等待服务就绪
echo ""
echo "步骤 3/3: 等待服务就绪..."
echo "等待数据库初始化..."
sleep 10

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "后端服务: http://localhost:8000"
echo "前端服务: http://localhost:3000"
echo "API文档: http://localhost:8000/docs"
echo "Celery监控: http://localhost:5555"
echo ""
echo "查看日志: docker-compose -f docker-compose.standalone.yml logs -f"
echo "停止服务: docker-compose -f docker-compose.standalone.yml down"
echo ""
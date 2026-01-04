#!/bin/bash

# AI公众号自动写作助手 Pro - 启动脚本

set -e

echo "🚀 Starting AI公众号自动写作助手 Pro..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
    echo "⏸️  Please configure your .env file and run this script again."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads temp logs

# Start Docker Compose
echo "🐳 Starting Docker containers..."
docker-compose -f docker/docker-compose.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
docker-compose -f docker/docker-compose.yml ps

echo ""
echo "✅ Services started successfully!"
echo ""
echo "📊 Service URLs:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Flower (Celery Monitor): http://localhost:5555"
echo "   - Nginx: http://localhost"
echo ""
echo "📝 To view logs:"
echo "   docker-compose -f docker/docker-compose.yml logs -f"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose -f docker/docker-compose.yml down"
echo ""
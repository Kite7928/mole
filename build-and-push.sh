#!/bin/bash

# AI公众号自动写作助手 Pro - 构建和推送镜像脚本

set -e

DOCKER_HUB_USERNAME=${DOCKER_HUB_USERNAME:-"your-dockerhub-username"}
IMAGE_NAME=${IMAGE_NAME:-"wechat-ai-writer-pro"}
VERSION=${VERSION:-"latest"}

FULL_IMAGE_NAME="${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${VERSION}"

echo "🚀 Building Docker image: $FULL_IMAGE_NAME"

# Build the image
echo "📦 Building image..."
docker build -t "$FULL_IMAGE_NAME" .

echo "✅ Build successful!"

# Push to Docker Hub
echo "📤 Pushing image to Docker Hub..."
docker push "$FULL_IMAGE_NAME"

echo "✅ Push successful!"
echo ""
echo "📊 Image details:"
echo "   Image: $FULL_IMAGE_NAME"
echo ""
echo "🚀 To pull and run on CentOS 7:"
echo "   docker pull $FULL_IMAGE_NAME"
echo "   docker run -d -p 3000:3000 -p 8000:8000 $FULL_IMAGE_NAME"
echo ""
#!/bin/bash

# AI公众号自动写作助手 Pro - 自动部署脚本
# 用途：帮助快速配置 GitHub Secrets 和环境变量

set -e

echo "🚀 AI公众号自动写作助手 Pro - 自动部署配置向导"
echo "=================================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否安装了 gh CLI
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 GitHub CLI (gh)${NC}"
    echo "请先安装 GitHub CLI: https://cli.github.com/"
    echo ""
    echo "安装命令："
    echo "  macOS: brew install gh"
    echo "  Linux: sudo apt install gh"
    echo "  Windows: winget install GitHub.cli"
    exit 1
fi

# 检查是否登录
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  未登录 GitHub，正在进行登录...${NC}"
    gh auth login
fi

echo -e "${GREEN}✅ GitHub CLI 已就绪${NC}"
echo ""

# 选择部署方案
echo "📋 请选择部署方案："
echo "  1) Vercel（推荐，最简单，免费额度大）"
echo "  2) Railway（支持后台任务）"
echo "  3) 自托管服务器（完全控制）"
echo "  4) 混合部署（Vercel前端 + Railway后台）"
echo ""
read -p "请输入选项 (1-4): " deploy_choice

case $deploy_choice in
    1)
        echo -e "${GREEN}✨ 你选择了 Vercel 部署${NC}"
        echo ""
        echo "📝 需要配置以下环境变量："
        echo ""

        # 读取环境变量
        read -p "OPENAI_API_KEY (OpenAI API密钥): " openai_key
        read -p "WECHAT_APP_ID (微信公众号AppID): " wechat_id
        read -p "WECHAT_APP_SECRET (微信公众号密钥): " wechat_secret

        # 生成 SECRET_KEY
        secret_key=$(openssl rand -hex 32)
        echo -e "${GREEN}✅ 已自动生成 SECRET_KEY: $secret_key${NC}"

        echo ""
        echo "🎯 下一步操作："
        echo "1. 访问：https://vercel.com/new/clone?repository-url=https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)"
        echo "2. 在 Vercel 中配置以下环境变量："
        echo "   OPENAI_API_KEY=$openai_key"
        echo "   WECHAT_APP_ID=$wechat_id"
        echo "   WECHAT_APP_SECRET=$wechat_secret"
        echo "   SECRET_KEY=$secret_key"
        echo "3. 在 Vercel Storage 中添加 Postgres 和 Redis"
        echo ""
        echo -e "${YELLOW}💡 提示：以后只需 git push，Vercel 会自动部署！${NC}"
        ;;

    2)
        echo -e "${GREEN}✨ 你选择了 Railway 部署${NC}"
        echo ""
        echo "📝 需要配置以下环境变量："
        echo ""

        read -p "OPENAI_API_KEY: " openai_key
        read -p "WECHAT_APP_ID: " wechat_id
        read -p "WECHAT_APP_SECRET: " wechat_secret

        secret_key=$(openssl rand -hex 32)
        echo -e "${GREEN}✅ 已自动生成 SECRET_KEY: $secret_key${NC}"

        echo ""
        echo "🎯 下一步操作："
        echo "1. 访问：https://railway.app/new/template?template=https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)"
        echo "2. Railway 会自动创建 Postgres 和 Redis"
        echo "3. 配置以下环境变量："
        echo "   OPENAI_API_KEY=$openai_key"
        echo "   WECHAT_APP_ID=$wechat_id"
        echo "   WECHAT_APP_SECRET=$wechat_secret"
        echo "   SECRET_KEY=$secret_key"
        echo ""
        echo -e "${YELLOW}💡 提示：以后只需 git push，Railway 会自动部署！${NC}"
        ;;

    3)
        echo -e "${GREEN}✨ 你选择了自托管服务器部署${NC}"
        echo ""
        echo "📝 需要配置 GitHub Secrets 用于自动部署"
        echo ""

        read -p "服务器 IP 地址: " server_host
        read -p "SSH 用户名 (如 root): " server_user
        echo "SSH 私钥 (输入完整路径，如 ~/.ssh/id_rsa): "
        read -p "> " ssh_key_path

        # 读取 SSH 私钥
        if [ ! -f "$ssh_key_path" ]; then
            echo -e "${RED}❌ SSH 私钥文件不存在: $ssh_key_path${NC}"
            exit 1
        fi
        ssh_key=$(cat "$ssh_key_path")

        # 可选：Docker Hub 配置
        read -p "是否需要推送到 Docker Hub? (y/n): " use_docker
        if [ "$use_docker" = "y" ]; then
            read -p "Docker Hub 用户名: " docker_user
            read -sp "Docker Hub 密码/Token: " docker_pass
            echo ""
        fi

        # 设置 GitHub Secrets
        echo ""
        echo "🔐 正在设置 GitHub Secrets..."

        gh secret set SERVER_HOST -b"$server_host"
        gh secret set SERVER_USER -b"$server_user"
        gh secret set SERVER_SSH_KEY -b"$ssh_key"

        if [ "$use_docker" = "y" ]; then
            gh secret set DOCKER_USERNAME -b"$docker_user"
            gh secret set DOCKER_PASSWORD -b"$docker_pass"
        fi

        echo -e "${GREEN}✅ GitHub Secrets 配置完成！${NC}"
        echo ""
        echo "🎯 下一步操作："
        echo "1. SSH 登录到服务器: ssh $server_user@$server_host"
        echo "2. 安装 Docker: curl -fsSL https://get.docker.com | sh"
        echo "3. 创建 .env 文件并配置环境变量"
        echo "4. 推送代码到 main 分支触发自动部署"
        echo ""
        echo -e "${YELLOW}💡 提示：以后只需 git push origin main，GitHub Actions 会自动部署到服务器！${NC}"
        ;;

    4)
        echo -e "${GREEN}✨ 你选择了混合部署（最佳实践！）${NC}"
        echo ""
        echo "📝 配置说明："
        echo ""
        echo "前端 + API → Vercel："
        echo "  访问：https://vercel.com/new/clone?repository-url=https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)"
        echo ""
        echo "后台任务 → Railway："
        echo "  访问：https://railway.app/new/template?template=https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)"
        echo ""
        echo "💡 这种方案结合了两者的优势："
        echo "  - Vercel：全球 CDN，快速响应"
        echo "  - Railway：长期运行任务，无冷启动"
        ;;

    *)
        echo -e "${RED}❌ 无效的选项${NC}"
        exit 1
        ;;
esac

echo ""
echo "=================================================="
echo -e "${GREEN}🎉 配置完成！${NC}"
echo ""
echo "📚 更多信息请查看："
echo "  - 部署指南：./DEPLOY.md"
echo "  - 项目文档：./README.md"
echo ""
echo "💬 遇到问题？提交 Issue："
echo "  https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/issues"
echo ""

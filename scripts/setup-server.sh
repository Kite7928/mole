#!/bin/bash

# 服务器环境一键配置脚本
# 用于在服务器上快速安装和配置所需的环境

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════╗"
echo "║   AI公众号自动写作助手 Pro - 服务器环境配置   ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

# 检查是否为 root 用户
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  检测到以 root 用户运行${NC}"
    echo -e "${YELLOW}建议创建普通用户运行此脚本${NC}"
    read -p "是否继续? (y/n): " continue_as_root
    if [ "$continue_as_root" != "y" ]; then
        exit 1
    fi
fi

# 检测操作系统
echo -e "${BLUE}🔍 检测操作系统...${NC}"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
    echo -e "${GREEN}✅ 操作系统: $PRETTY_NAME${NC}"
else
    echo -e "${RED}❌ 无法检测操作系统${NC}"
    exit 1
fi

# 更新系统包
echo -e "${BLUE}📦 更新系统包...${NC}"
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt update && sudo apt upgrade -y
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    sudo yum update -y
else
    echo -e "${YELLOW}⚠️  未知的操作系统，跳过更新${NC}"
fi

# 安装必要工具
echo -e "${BLUE}🛠️  安装必要工具...${NC}"
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt install -y \
        curl \
        wget \
        git \
        vim \
        htop \
        ufw \
        ca-certificates \
        gnupg \
        lsb-release
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    sudo yum install -y \
        curl \
        wget \
        git \
        vim \
        htop \
        firewalld
fi
echo -e "${GREEN}✅ 必要工具安装完成${NC}"

# 安装 Docker
echo -e "${BLUE}🐳 安装 Docker...${NC}"
if command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker 已安装${NC}"
    docker --version
else
    echo -e "${GREEN}正在安装 Docker...${NC}"
    curl -fsSL https://get.docker.com | sh

    # 将当前用户添加到 docker 组
    sudo usermod -aG docker $USER

    # 启动 Docker 服务
    sudo systemctl enable docker
    sudo systemctl start docker

    echo -e "${GREEN}✅ Docker 安装完成${NC}"
    docker --version
fi

# 安装 Docker Compose
echo -e "${BLUE}🐳 安装 Docker Compose...${NC}"
if command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose 已安装${NC}"
    docker-compose --version
else
    echo -e "${GREEN}正在安装 Docker Compose...${NC}"

    # 获取最新版本号
    LATEST_COMPOSE=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)

    # 下载并安装
    sudo curl -L "https://github.com/docker/compose/releases/download/${LATEST_COMPOSE}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose

    sudo chmod +x /usr/local/bin/docker-compose

    # 创建软链接
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

    echo -e "${GREEN}✅ Docker Compose 安装完成${NC}"
    docker-compose --version
fi

# 配置防火墙
echo -e "${BLUE}🔥 配置防火墙...${NC}"
read -p "是否配置防火墙? (y/n): " config_firewall

if [ "$config_firewall" = "y" ]; then
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        # UFW 配置
        echo -e "${GREEN}配置 UFW 防火墙...${NC}"
        sudo ufw --force enable
        sudo ufw default deny incoming
        sudo ufw default allow outgoing

        # 允许 SSH
        sudo ufw allow 22/tcp

        # 允许 HTTP/HTTPS
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp

        echo -e "${GREEN}✅ UFW 防火墙配置完成${NC}"
        sudo ufw status

    elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
        # Firewalld 配置
        echo -e "${GREEN}配置 Firewalld 防火墙...${NC}"
        sudo systemctl enable firewalld
        sudo systemctl start firewalld

        sudo firewall-cmd --permanent --add-service=ssh
        sudo firewall-cmd --permanent --add-service=http
        sudo firewall-cmd --permanent --add-service=https
        sudo firewall-cmd --reload

        echo -e "${GREEN}✅ Firewalld 防火墙配置完成${NC}"
        sudo firewall-cmd --list-all
    fi
fi

# 创建项目目录
echo -e "${BLUE}📁 创建项目目录...${NC}"
PROJECT_DIR="/opt/wechat-ai-writer"

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠️  项目目录已存在: $PROJECT_DIR${NC}"
    read -p "是否删除并重新创建? (y/n): " recreate
    if [ "$recreate" = "y" ]; then
        sudo rm -rf "$PROJECT_DIR"
        sudo mkdir -p "$PROJECT_DIR"
        sudo chown $USER:$USER "$PROJECT_DIR"
    fi
else
    sudo mkdir -p "$PROJECT_DIR"
    sudo chown $USER:$USER "$PROJECT_DIR"
    echo -e "${GREEN}✅ 项目目录创建完成: $PROJECT_DIR${NC}"
fi

# 克隆项目
echo -e "${BLUE}📥 克隆项目代码...${NC}"
read -p "是否克隆项目代码? (y/n): " clone_repo

if [ "$clone_repo" = "y" ]; then
    cd "$PROJECT_DIR"

    if [ -d ".git" ]; then
        echo -e "${YELLOW}⚠️  Git 仓库已存在，执行 git pull${NC}"
        git pull origin main
    else
        echo -e "${GREEN}克隆项目...${NC}"
        git clone https://github.com/Kite7928/mole.git .
    fi

    echo -e "${GREEN}✅ 项目代码准备完成${NC}"
fi

# 配置环境变量
echo -e "${BLUE}⚙️  配置环境变量...${NC}"
cd "$PROJECT_DIR"

if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 文件已存在${NC}"
    read -p "是否重新配置? (y/n): " reconfig_env
    if [ "$reconfig_env" != "y" ]; then
        skip_env=true
    fi
fi

if [ "$skip_env" != true ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        # 创建基本的 .env 文件
        cat > .env << 'EOF'
# Application
APP_NAME=AI公众号自动写作助手 Pro
SECRET_KEY=CHANGE_ME
DEBUG=False

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=wechat_ai_writer
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/wechat_ai_writer

# Redis
REDIS_URL=redis://redis:6379/0

# AI Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# WeChat Configuration
WECHAT_APP_ID=your-app-id-here
WECHAT_APP_SECRET=your-app-secret-here

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/1
CELERY_WORKER_CONCURRENCY=2

# Docker
DOCKER_USERNAME=local

# Server
HTTP_PORT=80
HTTPS_PORT=443
EOF
    fi

    # 生成 SECRET_KEY
    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        echo -e "${GREEN}✅ 已生成 SECRET_KEY${NC}"
    fi

    echo -e "${YELLOW}⚠️  请编辑 $PROJECT_DIR/.env 文件配置必要的环境变量${NC}"
    echo -e "${YELLOW}必须配置的变量:${NC}"
    echo -e "  - OPENAI_API_KEY"
    echo -e "  - WECHAT_APP_ID"
    echo -e "  - WECHAT_APP_SECRET"
    echo ""
    read -p "按回车键打开编辑器 (或按 Ctrl+C 跳过): " edit_env

    if command -v nano &> /dev/null; then
        nano .env
    elif command -v vim &> /dev/null; then
        vim .env
    else
        echo -e "${YELLOW}请手动编辑: $PROJECT_DIR/.env${NC}"
    fi
fi

# 配置 SSH 密钥（用于 GitHub Actions）
echo -e "${BLUE}🔑 配置 SSH 密钥（用于 GitHub Actions）${NC}"
read -p "是否配置 SSH 密钥? (y/n): " config_ssh

if [ "$config_ssh" = "y" ]; then
    echo -e "${GREEN}请提供你的 SSH 公钥内容${NC}"
    echo -e "${YELLOW}（在本地运行: cat ~/.ssh/deploy_key.pub）${NC}"
    echo ""
    read -p "粘贴公钥内容并按回车: " ssh_pubkey

    if [ -n "$ssh_pubkey" ]; then
        mkdir -p ~/.ssh
        chmod 700 ~/.ssh

        # 添加公钥
        echo "$ssh_pubkey" >> ~/.ssh/authorized_keys
        chmod 600 ~/.ssh/authorized_keys

        echo -e "${GREEN}✅ SSH 公钥已添加${NC}"
        echo -e "${GREEN}测试连接: ssh -i ~/.ssh/deploy_key $USER@$(curl -s ifconfig.me)${NC}"
    else
        echo -e "${YELLOW}⚠️  未提供公钥，跳过配置${NC}"
    fi
fi

# 优化 Docker 配置
echo -e "${BLUE}🔧 优化 Docker 配置...${NC}"
read -p "是否优化 Docker 配置? (y/n): " optimize_docker

if [ "$optimize_docker" = "y" ]; then
    sudo mkdir -p /etc/docker

    cat | sudo tee /etc/docker/daemon.json > /dev/null << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
EOF

    sudo systemctl restart docker
    echo -e "${GREEN}✅ Docker 配置已优化${NC}"
fi

# 显示服务器信息
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════╗"
echo "║              安装完成！                        ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}✅ 环境配置完成！${NC}"
echo ""
echo -e "${BLUE}📋 服务器信息:${NC}"
echo -e "  IP 地址: $(curl -s ifconfig.me)"
echo -e "  用户名: $USER"
echo -e "  项目目录: $PROJECT_DIR"
echo ""
echo -e "${BLUE}📚 下一步操作:${NC}"
echo -e "  1. 编辑环境变量: nano $PROJECT_DIR/.env"
echo -e "  2. 启动服务:"
echo -e "     cd $PROJECT_DIR"
echo -e "     docker-compose -f docker-compose.production.yml up -d"
echo -e "  3. 查看日志:"
echo -e "     docker-compose -f docker-compose.production.yml logs -f"
echo ""
echo -e "${BLUE}🔐 GitHub Secrets 配置:${NC}"
echo -e "  在 GitHub 仓库设置以下 Secrets:"
echo -e "  - SERVER_HOST: $(curl -s ifconfig.me)"
echo -e "  - SERVER_USER: $USER"
echo -e "  - SERVER_SSH_KEY: (你的私钥内容)"
echo -e "  - SERVER_PORT: 22"
echo ""
echo -e "${YELLOW}⚠️  重要提示:${NC}"
echo -e "  - 如果修改了 docker 组，请重新登录以使更改生效"
echo -e "  - 记得配置 .env 文件中的敏感信息"
echo -e "  - 定期备份数据库和 Redis 数据"
echo ""
echo -e "${GREEN}🎉 祝你部署成功！${NC}"

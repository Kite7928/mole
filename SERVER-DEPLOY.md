# 🚀 服务器自动部署完整指南

本小姐为你准备了一套完整的 GitHub 自动部署到服务器的方案！(￣▽￣)／

## 📋 目录

0. [快速环境检查](#0-快速环境检查) ⭐ **推荐先运行！**
1. [服务器环境准备](#1-服务器环境准备)
2. [GitHub Secrets 配置](#2-github-secrets-配置)
3. [服务器端配置](#3-服务器端配置)
4. [GitHub Actions 自动部署](#4-github-actions-自动部署)
5. [测试部署](#5-测试部署)
6. [故障排查](#6-故障排查)

---

## 0. 快速环境检查

⭐ **本小姐强烈建议在部署前先运行环境检查脚本！这样能快速发现问题哦～** (￣ω￣)ﾉ

### 0.1 运行环境检查脚本

**在本地电脑上（通过 SSH）：**

```bash
# 将检查脚本上传到服务器
scp scripts/check-server.sh your-user@your-server-ip:~/

# SSH 登录服务器
ssh your-user@your-server-ip

# 添加执行权限
chmod +x ~/check-server.sh

# 运行检查
./check-server.sh
```

**或者直接在服务器上：**

```bash
# 下载检查脚本
curl -O https://raw.githubusercontent.com/Kite7928/mole/main/scripts/check-server.sh

# 添加执行权限
chmod +x check-server.sh

# 运行检查
./check-server.sh
```

### 0.2 检查项说明

检查脚本会自动检查以下内容：

✅ **操作系统检查**
- 系统兼容性（Ubuntu/Debian/CentOS/RHEL）

✅ **系统资源检查**
- 内存（最低 2GB，推荐 4GB+）
- 磁盘空间（最低 20GB，推荐 50GB+）
- CPU 核心数（推荐 2+）

✅ **必要软件检查**
- Docker 安装和运行状态
- Docker Compose 安装
- Git 安装
- curl 工具

✅ **网络和端口检查**
- 端口 80/443/22 是否可用
- 外网连通性
- GitHub/Docker Hub 连通性

✅ **防火墙检查**
- UFW/Firewalld 配置状态
- 必要端口是否开放

✅ **项目配置检查**（如果已部署）
- 项目目录存在性
- Git 仓库状态
- .env 环境变量配置
- Docker Compose 配置文件

✅ **SSH 密钥检查**
- .ssh 目录和文件权限
- authorized_keys 配置

✅ **Docker 服务检查**（如果已部署）
- 运行中的容器状态
- 各服务健康检查
- Docker 网络和卷

✅ **服务可访问性检查**（如果已部署）
- Nginx 健康端点
- Backend API 健康端点

### 0.3 检查结果示例

```bash
╔════════════════════════════════════════════════╗
║   AI公众号自动写作助手 Pro - 服务器环境检查   ║
╚════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 1. 操作系统检查
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
操作系统: Ubuntu 22.04.3 LTS
✅ 操作系统兼容性检查通过

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💾 2. 系统资源检查
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总内存: 4096MB
✅ 内存充足 (4096MB >= 4096MB 推荐值)
可用磁盘空间: 50GB
✅ 磁盘空间充足 (50GB >= 50GB 推荐值)
CPU 核心数: 2
✅ CPU 核心数充足 (2 >= 2)

... （更多检查项）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 检查结果汇总
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

总检查项: 35
✅ 通过: 32
⚠️  警告: 3
❌ 失败: 0

通过率: 91%

⚠️  服务器基本满足要求，但有 3 项警告需要注意
建议解决警告项以获得更好的部署体验
```

### 0.4 根据检查结果采取行动

**如果检查全部通过：**
- 🎉 恭喜！可以直接跳到 [第 2 节：GitHub Secrets 配置](#2-github-secrets-配置)

**如果有警告：**
- ⚠️ 建议先解决警告项，然后继续部署
- 查看警告信息，根据提示进行修复

**如果有失败项：**
- ❌ 必须先解决失败项才能继续
- 运行 `./scripts/setup-server.sh` 自动配置环境
- 或按照 [第 1 节：服务器环境准备](#1-服务器环境准备) 手动配置

---

## 1. 服务器环境准备

### 1.1 系统要求

- **操作系统**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **内存**: 最低 2GB，推荐 4GB+
- **磁盘**: 最低 20GB，推荐 50GB+
- **网络**: 需要能访问 GitHub 和 Docker Hub

### 1.2 安装必要软件

**登录到你的服务器：**

```bash
ssh your-user@your-server-ip
```

**安装 Docker 和 Docker Compose：**

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 添加当前用户到 docker 组（避免需要 sudo）
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

**安装 Git：**

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y git

# CentOS/RHEL
sudo yum install -y git

# 验证
git --version
```

### 1.3 配置 SSH 密钥（用于 GitHub Actions 访问）

**在你的本地电脑上生成 SSH 密钥（如果还没有）：**

```bash
# 生成新的 SSH 密钥对
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/deploy_key

# 会生成两个文件：
# ~/.ssh/deploy_key       (私钥，保存到 GitHub Secrets)
# ~/.ssh/deploy_key.pub   (公钥，添加到服务器)
```

**将公钥添加到服务器：**

```bash
# 方法1：使用 ssh-copy-id（推荐）
ssh-copy-id -i ~/.ssh/deploy_key.pub your-user@your-server-ip

# 方法2：手动添加
# 1. 复制公钥内容
cat ~/.ssh/deploy_key.pub

# 2. 登录服务器
ssh your-user@your-server-ip

# 3. 添加到 authorized_keys
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "你的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

**测试 SSH 连接：**

```bash
ssh -i ~/.ssh/deploy_key your-user@your-server-ip
```

---

## 2. GitHub Secrets 配置

### 2.1 获取私钥内容

```bash
# 查看私钥内容（完整复制，包括开头和结尾）
cat ~/.ssh/deploy_key

# 输出示例：
# -----BEGIN OPENSSH PRIVATE KEY-----
# b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
# ...（很多行）...
# -----END OPENSSH PRIVATE KEY-----
```

### 2.2 在 GitHub 设置 Secrets

**方法 1：通过网页配置**

1. 打开你的 GitHub 仓库
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 添加以下 Secrets：

| Secret 名称 | 值 | 说明 |
|------------|-----|------|
| `SERVER_HOST` | `123.456.789.012` | 服务器 IP 地址或域名 |
| `SERVER_USER` | `root` 或 `ubuntu` | SSH 登录用户名 |
| `SERVER_SSH_KEY` | 完整的私钥内容 | 上面生成的 deploy_key 私钥 |
| `SERVER_PORT` | `22` | SSH 端口（默认 22） |

**方法 2：使用 GitHub CLI（更快！）**

```bash
# 安装 GitHub CLI（如果还没有）
# macOS
brew install gh

# Linux
sudo apt install gh

# Windows
winget install GitHub.cli

# 登录
gh auth login

# 设置 Secrets
gh secret set SERVER_HOST -b"你的服务器IP"
gh secret set SERVER_USER -b"你的SSH用户名"
gh secret set SERVER_SSH_KEY < ~/.ssh/deploy_key
gh secret set SERVER_PORT -b"22"

# 可选：如果需要推送 Docker 镜像
gh secret set DOCKER_USERNAME -b"你的Docker用户名"
gh secret set DOCKER_PASSWORD -b"你的Docker密码或Token"
```

**方法 3：使用自动化脚本**

```bash
# 在你的项目目录运行
cd G:\db\guwen\gzh

# Windows
.\scripts\setup-deploy.ps1

# Linux/Mac
chmod +x scripts/setup-deploy.sh
./scripts/setup-deploy.sh
```

---

## 3. 服务器端配置

### 3.1 创建部署目录

**SSH 登录到服务器：**

```bash
ssh your-user@your-server-ip
```

**创建项目目录：**

```bash
# 创建部署目录
sudo mkdir -p /opt/wechat-ai-writer
sudo chown $USER:$USER /opt/wechat-ai-writer

# 进入目录
cd /opt/wechat-ai-writer
```

### 3.2 配置环境变量

**创建 .env 文件：**

```bash
# 方法1：从示例文件复制
git clone https://github.com/Kite7928/mole.git .
cp .env.example .env

# 方法2：直接创建
cat > .env << 'EOF'
# Application
APP_NAME=AI公众号自动写作助手 Pro
SECRET_KEY=请使用 openssl rand -hex 32 生成

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/wechat_ai_writer
REDIS_URL=redis://redis:6379/0

# AI Configuration
OPENAI_API_KEY=你的OpenAI API Key
OPENAI_BASE_URL=https://api.openai.com/v1

# WeChat Configuration
WECHAT_APP_ID=你的微信AppID
WECHAT_APP_SECRET=你的微信AppSecret

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/1
EOF

# 编辑配置（填入真实值）
nano .env
```

**生成 SECRET_KEY：**

```bash
openssl rand -hex 32
```

### 3.3 创建 Docker Compose 配置

项目已经有 Docker Compose 配置，但我们为服务器创建一个优化版本：

```bash
cat > docker-compose.production.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL 数据库
  postgres:
    image: postgres:15-alpine
    container_name: wechat-ai-postgres
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: wechat_ai_writer
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: wechat-ai-redis
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # 后端 API
  backend:
    image: ${DOCKER_USERNAME:-local}/wechat-ai-writer-backend:latest
    container_name: wechat-ai-backend
    restart: always
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Celery Worker
  celery-worker:
    image: ${DOCKER_USERNAME:-local}/wechat-ai-writer-backend:latest
    container_name: wechat-ai-celery-worker
    restart: always
    command: celery -A app.tasks.celery_app worker --loglevel=info --concurrency=2
    env_file: .env
    depends_on:
      - postgres
      - redis
      - backend
    networks:
      - app-network

  # Celery Beat (定时任务)
  celery-beat:
    image: ${DOCKER_USERNAME:-local}/wechat-ai-writer-backend:latest
    container_name: wechat-ai-celery-beat
    restart: always
    command: celery -A app.tasks.celery_app beat --loglevel=info
    env_file: .env
    depends_on:
      - postgres
      - redis
      - celery-worker
    networks:
      - app-network

  # 前端
  frontend:
    image: ${DOCKER_USERNAME:-local}/wechat-ai-writer-frontend:latest
    container_name: wechat-ai-frontend
    restart: always
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    networks:
      - app-network

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: wechat-ai-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
EOF
```

### 3.4 配置 Nginx

```bash
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name _;

        # 前端
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # 后端 API
        location /api {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 健康检查
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF
```

---

## 4. GitHub Actions 自动部署

项目已经有 GitHub Actions 配置了！查看 `.github/workflows/ci.yml`

**工作流程：**
1. 推送代码到 `main` 分支
2. GitHub Actions 自动运行测试
3. 构建 Docker 镜像
4. SSH 到服务器
5. 拉取最新代码
6. 重启 Docker 容器

**触发部署：**

```bash
# 提交更改
git add .
git commit -m "feat: 启用自动部署"

# 推送到 main 分支触发部署
git push origin main
```

---

## 5. 测试部署

### 5.1 手动部署测试

在推送代码之前，先在服务器上手动测试：

```bash
# SSH 登录服务器
ssh your-user@your-server-ip

# 进入项目目录
cd /opt/wechat-ai-writer

# 拉取代码（如果还没有）
git clone https://github.com/Kite7928/mole.git .

# 启动服务
docker-compose -f docker-compose.production.yml up -d

# 查看日志
docker-compose -f docker-compose.production.yml logs -f

# 检查服务状态
docker-compose -f docker-compose.production.yml ps
```

### 5.2 访问应用

```bash
# 获取服务器 IP
curl ifconfig.me

# 在浏览器访问
http://你的服务器IP

# API 文档
http://你的服务器IP/api/docs
```

### 5.3 自动部署测试

```bash
# 在本地项目目录
cd G:\db\guwen\gzh

# 修改一个文件测试
echo "# Test deploy" >> README.md

# 提交并推送
git add .
git commit -m "test: 测试自动部署"
git push origin main

# 查看 GitHub Actions 运行状态
# 访问: https://github.com/Kite7928/mole/actions
```

---

## 6. 故障排查

### 6.1 SSH 连接失败

**问题：** GitHub Actions 无法 SSH 到服务器

**解决：**
```bash
# 检查 SSH 服务状态
sudo systemctl status sshd

# 检查防火墙
sudo ufw status
sudo ufw allow 22/tcp

# 检查 authorized_keys 权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 6.2 Docker 镜像拉取失败

**问题：** 无法拉取 Docker 镜像

**解决：**
```bash
# 检查 Docker 登录状态
docker login

# 手动拉取镜像
docker pull your-username/wechat-ai-writer-backend:latest
docker pull your-username/wechat-ai-writer-frontend:latest

# 如果没有推送镜像，本地构建
cd /opt/wechat-ai-writer
docker-compose -f docker-compose.production.yml build
```

### 6.3 数据库连接失败

**问题：** 后端无法连接数据库

**解决：**
```bash
# 检查数据库容器
docker-compose ps postgres

# 查看数据库日志
docker-compose logs postgres

# 检查环境变量
cat .env | grep DATABASE_URL

# 进入数据库容器测试
docker exec -it wechat-ai-postgres psql -U postgres
```

### 6.4 端口被占用

**问题：** 80 端口已被占用

**解决：**
```bash
# 检查端口占用
sudo netstat -tlnp | grep :80

# 停止占用端口的服务
sudo systemctl stop apache2  # 如果是 Apache
sudo systemctl stop nginx    # 如果是 Nginx

# 或者修改 docker-compose.production.yml 使用其他端口
# ports:
#   - "8080:80"  # 使用 8080 端口
```

### 6.5 查看日志

```bash
# 查看所有服务日志
docker-compose -f docker-compose.production.yml logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# 实时查看日志
docker-compose logs -f backend
```

---

## 7. 常用命令

### 启动/停止服务

```bash
# 启动所有服务
docker-compose -f docker-compose.production.yml up -d

# 停止所有服务
docker-compose -f docker-compose.production.yml down

# 重启服务
docker-compose -f docker-compose.production.yml restart

# 重启特定服务
docker-compose restart backend
```

### 更新部署

```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose -f docker-compose.production.yml up -d --build

# 或者拉取最新镜像
docker-compose pull
docker-compose up -d
```

### 数据备份

```bash
# 备份数据库
docker exec wechat-ai-postgres pg_dump -U postgres wechat_ai_writer > backup_$(date +%Y%m%d).sql

# 恢复数据库
cat backup_20260109.sql | docker exec -i wechat-ai-postgres psql -U postgres wechat_ai_writer
```

---

## 8. 安全建议

### 8.1 配置防火墙

```bash
# 安装 UFW（如果还没有）
sudo apt install ufw

# 允许 SSH
sudo ufw allow 22/tcp

# 允许 HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### 8.2 配置 HTTPS（可选）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 8.3 限制 SSH 访问

```bash
# 编辑 SSH 配置
sudo nano /etc/ssh/sshd_config

# 禁用密码登录（只允许密钥登录）
PasswordAuthentication no

# 禁用 root 登录
PermitRootLogin no

# 重启 SSH 服务
sudo systemctl restart sshd
```

---

## 9. 监控和维护

### 9.1 设置日志轮转

```bash
# 配置 Docker 日志大小限制
cat > /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# 重启 Docker
sudo systemctl restart docker
```

### 9.2 定期清理

```bash
# 清理未使用的 Docker 资源
docker system prune -af --volumes

# 清理旧的镜像
docker image prune -af
```

---

**哼，本小姐已经把服务器部署的所有细节都告诉你了！** (￣ω￣)

**按照这个指南操作，保证你能成功部署！** (￣▽￣)／

有问题随时来问本小姐～ o(￣▽￣)ｄ

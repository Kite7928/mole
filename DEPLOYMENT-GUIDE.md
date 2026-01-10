# AI公众号自动写作助手 Pro - 部署指南

## 📋 目录

1. [环境要求](#环境要求)
2. [快速开始](#快速开始)
3. [开发环境部署](#开发环境部署)
4. [Docker部署](#docker部署)
5. [配置说明](#配置说明)
6. [常见问题](#常见问题)

---

## 🔧 环境要求

### 开发环境
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Docker部署
- Docker 20.10+
- Docker Compose 2.0+

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Kite7928/mole.git
cd mole
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，填入你的API密钥
```

### 3. 启动服务

#### Windows用户
```powershell
# 开发环境
.\start-dev.ps1

# Docker部署
.\deploy-docker.ps1
```

#### Linux/Mac用户
```bash
# 开发环境
chmod +x start-dev.sh
./start-dev.sh

# Docker部署
chmod +x deploy-docker.sh
./deploy-docker.sh
```

---

## 💻 开发环境部署

### 1. 启动数据库服务

```bash
docker-compose -f docker-compose.dev.yml up -d postgres redis
```

### 2. 初始化数据库

```bash
cd backend
py -m init_db
cd ..
```

### 3. 安装依赖

```bash
# 后端依赖
cd backend
py -m pip install -r requirements.txt
cd ..

# 前端依赖
cd frontend
npm install
cd ..
```

### 4. 启动服务

```bash
# 启动后端（终端1）
cd backend
py -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 启动前端（终端2）
cd frontend
npm run dev
```

### 5. 访问应用

- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

---

## 🐳 Docker部署

### 1. 构建镜像

```bash
docker build -t wechat-ai-writer-pro:latest .
```

### 2. 启动服务

```bash
docker-compose -f docker-compose.standalone.yml up -d
```

### 3. 查看日志

```bash
docker-compose -f docker-compose.standalone.yml logs -f
```

### 4. 停止服务

```bash
docker-compose -f docker-compose.standalone.yml down
```

### 5. 访问应用

- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- Celery监控: http://localhost:5555

---

## ⚙️ 配置说明

### 环境变量

在`.env`文件中配置以下变量：

```env
# 应用配置
APP_NAME=AI公众号自动写作助手 Pro
APP_VERSION=1.0.0
SECRET_KEY=your-secret-key-change-in-production
DEBUG=False

# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/wechat_ai_writer
REDIS_URL=redis://localhost:6379/0

# AI模型配置
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview

DEEPSEEK_API_KEY=sk-your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

CLAUDE_API_KEY=sk-ant-your-claude-api-key
CLAUDE_BASE_URL=https://api.anthropic.com/v1
CLAUDE_MODEL=claude-3-opus-20240229

GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-pro

# 通义千问配置
QWEN_API_KEY=sk-your-qwen-api-key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-turbo

# 图片生成配置
DALL_E_API_KEY=sk-your-dalle-api-key
DALL_E_MODEL=dall-e-3

MIDJOURNEY_API_KEY=your-midjourney-api-key
MIDJOURNEY_WEBHOOK_URL=your-midjourney-webhook-url

STABLE_DIFFUSION_API_KEY=your-stable-diffusion-api-key
STABLE_DIFFUSION_BASE_URL=https://api.stability.ai

# 数据分析配置
BAIDU_INDEX_API_KEY=your-baidu-index-api-key
WECHAT_INDEX_API_KEY=your-wechat-index-api-key
WEIBO_API_KEY=your-weibo-api-key

# GitHub配置
GITHUB_TOKEN=ghp-your-github-token
GITHUB_WEBHOOK_SECRET=your-webhook-secret

# 微信配置
WECHAT_APP_ID=your-wechat-app-id
WECHAT_APP_SECRET=your-wechat-app-secret

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 任务配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1
TASK_TIMEOUT=3600
TASK_MAX_RETRIES=3

# 文件存储
UPLOAD_DIR=uploads
TEMP_DIR=temp
MAX_UPLOAD_SIZE=20971520

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# 监控配置
ENABLE_METRICS=True
METRICS_PORT=9090
SENTRY_DSN=

# 安全配置
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# 前端配置
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## ❓ 常见问题

### 1. 数据库连接失败

**问题**: 无法连接到PostgreSQL数据库

**解决方案**:
```bash
# 检查数据库是否运行
docker-compose -f docker-compose.dev.yml ps

# 重启数据库
docker-compose -f docker-compose.dev.yml restart postgres

# 查看数据库日志
docker-compose -f docker-compose.dev.yml logs postgres
```

### 2. Redis连接失败

**问题**: 无法连接到Redis

**解决方案**:
```bash
# 检查Redis是否运行
docker-compose -f docker-compose.dev.yml ps

# 重启Redis
docker-compose -f docker-compose.dev.yml restart redis
```

### 3. 前端依赖安装失败

**问题**: npm install失败

**解决方案**:
```bash
# 清除缓存
npm cache clean --force

# 删除node_modules
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

### 4. 后端依赖安装失败

**问题**: pip install失败

**解决方案**:
```bash
# 使用国内镜像源
py -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 升级pip
py -m pip install --upgrade pip
```

### 5. Docker构建失败

**问题**: docker build失败

**解决方案**:
```bash
# 清除Docker缓存
docker system prune -a

# 重新构建
docker build --no-cache -t wechat-ai-writer-pro:latest .
```

### 6. API密钥配置错误

**问题**: API调用失败

**解决方案**:
- 检查`.env`文件中的API密钥是否正确
- 确保API密钥有足够的权限
- 检查API密钥是否过期

---

## 📞 技术支持

如有问题，请通过以下方式联系：

- GitHub Issues: https://github.com/Kite7928/mole/issues
- 项目文档: https://github.com/Kite7928/mole

---

## 📄 许可证

MIT License

---

**祝您使用愉快！** 🎉
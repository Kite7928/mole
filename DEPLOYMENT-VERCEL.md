# Vercel + Cloudflare 部署指南

本文档提供将 AI 公众号自动写作助手 Pro 部署到 Vercel + Cloudflare + Railway 的完整指南。

## 📋 架构概览

```
┌─────────────────────────────────────────────────┐
│                  Cloudflare                     │
│  (CDN + WAF + DDoS 防护 + 边缘缓存)              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│                   Vercel                         │
│  ┌──────────────┐    ┌──────────────┐          │
│  │   Frontend   │    │   Backend    │          │
│  │   (Next.js)  │    │   (FastAPI)  │          │
│  └──────────────┘    └──────────────┘          │
│         │                    │                  │
└─────────┼────────────────────┼──────────────────┘
          │                    │
          ▼                    ▼
    ┌──────────┐        ┌─────────────┐
    │ Vercel KV│        │  Supabase   │
    │  (Redis) │        │ (PostgreSQL)│
    └──────────┘        └─────────────┘
                               │
                               ▼
                     ┌─────────────────┐
                     │  Railway/Render │
                     │  (Celery Worker)│
                     └─────────────────┘
```

## 🚀 快速开始

### 前置要求

- Node.js 18+
- Python 3.11+ (仅用于本地开发)
- Vercel 账号
- Cloudflare 账号
- Railway 账号

### 1. 安装 CLI 工具

```bash
# Vercel CLI
npm install -g vercel

# Railway CLI
npm install -g @railway/cli

# Cloudflare Wrangler (可选)
npm install -g wrangler
```

### 2. 部署到 Vercel

```bash
# Linux/Mac
./deploy-vercel.sh

# Windows PowerShell
.\deploy-vercel.ps1
```

### 3. 部署 Celery Workers 到 Railway

```bash
# Linux/Mac
./deploy-railway.sh

# Windows PowerShell
.\deploy-railway.ps1
```

### 4. 配置 Cloudflare (可选)

```bash
cd cloudflare
npm install
wrangler deploy
```

## 🔧 详细配置步骤

### 步骤 1: 配置 Vercel 环境变量

在 Vercel 项目设置中添加以下环境变量:

```env
# API 配置
NEXT_PUBLIC_API_URL=https://your-app.vercel.app/api

# 数据库 (从 Railway 或 Supabase 获取)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis (从 Vercel KV 或 Railway 获取)
REDIS_URL=redis://host:port/0

# AI 配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1

# 微信配置
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret

# 安全配置
SECRET_KEY=your_secret_key_generate_with_openssl_rand_base64_32
```

### 步骤 2: 配置 Railway

#### 2.1 创建 Railway 项目

```bash
railway login
railway init
```

#### 2.2 添加服务

```bash
# 添加 PostgreSQL
railway add postgresql

# 添加 Redis
railway add redis
```

#### 2.3 部署 Celery Workers

```bash
# 部署 Worker
railway up --service celery-worker

# 部署 Beat (调度器)
railway up --service celery-beat

# 部署 Flower (监控)
railway up --service flower
```

#### 2.4 获取连接字符串

```bash
# 查看服务状态
railway status

# 获取数据库 URL
railway variables

# 复制 DATABASE_URL 和 REDIS_URL 到 Vercel
```

### 步骤 3: 配置 Cloudflare (可选)

#### 3.1 添加域名到 Cloudflare

1. 登录 Cloudflare Dashboard
2. 添加你的域名
3. 更新域名服务器为 Cloudflare 提供的 NS 记录

#### 3.2 配置 DNS

```
Type: CNAME
Name: @
Target: your-app.vercel.app
Proxy: ✅ (橙色云朵)
```

#### 3.3 配置 SSL/TLS

1. 进入 SSL/TLS 设置
2. 选择 "Full" 或 "Full (strict)" 模式
3. 启用 "Always Use HTTPS"

#### 3.4 部署 Cloudflare Worker (可选)

```bash
cd cloudflare
npm install

# 编辑 wrangler.toml 配置
# 设置正确的 KV namespace ID 和路由

wrangler deploy
```

### 步骤 4: 配置 Vercel 域名

1. 进入 Vercel 项目设置
2. 添加自定义域名
3. 选择你的 Cloudflare 域名
4. 等待 DNS 传播完成

## 📊 监控和维护

### Vercel 监控

- 访问 Vercel Dashboard
- 查看 Functions 日志
- 监控性能指标

### Railway 监控

- 访问 Railway Dashboard
- 查看 Celery Worker 日志
- 访问 Flower 监控面板

### Cloudflare 监控

- 访问 Cloudflare Analytics
- 查看流量统计
- 监控安全事件

## 🔍 故障排查

### Vercel 部署失败

**问题**: 构建失败

**解决方案**:
```bash
# 检查本地构建
cd frontend
npm run build

cd backend
pip install -r requirements-vercel.txt
```

**问题**: 环境变量未设置

**解决方案**:
```bash
# 查看环境变量
vercel env ls

# 添加环境变量
vercel env add DATABASE_URL production
```

### Railway 连接失败

**问题**: 无法连接到数据库

**解决方案**:
```bash
# 检查服务状态
railway status

# 查看日志
railway logs

# 重启服务
railway up
```

### Cloudflare Worker 错误

**问题**: Worker 返回 502 错误

**解决方案**:
1. 检查 `wrangler.toml` 中的 API_URL 配置
2. 确保 Vercel 部署成功
3. 查看 Worker 日志:
```bash
wrangler tail
```

### Celery 任务不执行

**问题**: 任务队列中有任务但不执行

**解决方案**:
1. 检查 Railway Worker 日志
2. 访问 Flower 监控面板
3. 确认 Redis 连接正常:
```bash
railway connect redis
redis-cli ping
```

## 💰 成本估算

| 服务 | 免费额度 | 预计成本 |
|------|----------|----------|
| Vercel | 100GB 带宽/月 | $0 - $20/月 |
| Vercel KV | 256MB 存储 | $0 - $5/月 |
| Cloudflare | 无限 CDN | $0 |
| Railway | $5 免费额度 | $5 - $20/月 |
| Supabase | 500MB 数据库 | $0 - $25/月 |
| **总计** | **免费** | **$5 - $70/月** |

## 🎯 性能优化建议

### 1. 启用 Vercel Edge Network

```javascript
// 在 vercel.json 中配置
{
  "functions": {
    "backend/app/api/**/*.py": {
      "maxDuration": 60
    }
  }
}
```

### 2. 配置 Cloudflare 缓存

```javascript
// 在 cloudflare/src/index.ts 中
const CACHE_TTL = {
  '/api/news': 300,      // 5 分钟
  '/api/statistics': 600, // 10 分钟
  '/api/health': 60,     // 1 分钟
};
```

### 3. 优化数据库查询

```python
# 使用连接池
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    poolclass=QueuePool
)
```

### 4. 启用 Redis 缓存

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
```

## 🔒 安全建议

1. **使用强密钥**
   ```bash
   openssl rand -base64 32
   ```

2. **启用 HTTPS**
   - Cloudflare: 强制 HTTPS
   - Vercel: 自动 HTTPS

3. **限制 API 访问**
   - 使用 API 密钥认证
   - 实现速率限制

4. **定期更新依赖**
   ```bash
   cd frontend && npm update
   cd backend && pip install --upgrade -r requirements-vercel.txt
   ```

5. **监控日志**
   - 设置告警通知
   - 定期检查异常日志

## 📚 相关文档

- [Vercel 文档](https://vercel.com/docs)
- [Railway 文档](https://docs.railway.app)
- [Cloudflare Workers 文档](https://developers.cloudflare.com/workers/)
- [FastAPI 文档](https://fastapi.tiangolo.com)
- [Celery 文档](https://docs.celeryq.dev)

## 🆘 获取帮助

如遇到问题:
1. 查看本文档的故障排查部分
2. 检查各服务的日志
3. 提交 GitHub Issue
4. 联系技术支持

---

**注意**: 本部署方案适用于生产环境，但建议先在测试环境验证所有配置。
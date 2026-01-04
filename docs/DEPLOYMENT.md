# 部署指南

本文档提供AI公众号自动写作助手Pro的详细部署指南。

## 目录

- [环境要求](#环境要求)
- [本地开发部署](#本地开发部署)
- [Docker部署](#docker部署)
- [生产环境部署](#生产环境部署)
- [监控和维护](#监控和维护)
- [故障排查](#故障排查)

## 环境要求

### 基础要求
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Docker 20.10+ (可选)
- Docker Compose 2.0+ (可选)

### 系统要求
- CPU: 2核以上
- 内存: 4GB以上
- 磁盘: 20GB以上可用空间
- 网络: 稳定的互联网连接

## 本地开发部署

### 1. 克隆仓库

```bash
git clone <repository-url>
cd wechat-ai-writer-pro
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的配置
```

### 3. 安装后端依赖

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. 安装前端依赖

```bash
cd frontend
npm install
```

### 5. 启动数据库

#### PostgreSQL
```bash
# 使用Docker快速启动
docker run -d \
  --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=wechat_ai_writer \
  -p 5432:5432 \
  postgres:15-alpine
```

#### Redis
```bash
# 使用Docker快速启动
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine
```

### 6. 初始化数据库

```bash
cd backend
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

### 7. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. 启动前端服务

```bash
cd frontend
npm run dev
```

### 9. 访问应用

- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## Docker部署

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件
```

### 2. 启动所有服务

```bash
# Linux/Mac
./scripts/start.sh

# Windows
.\scripts\start.ps1
```

### 3. 查看服务状态

```bash
docker-compose -f docker/docker-compose.yml ps
```

### 4. 查看日志

```bash
# 查看所有服务日志
docker-compose -f docker/docker-compose.yml logs -f

# 查看特定服务日志
docker-compose -f docker/docker-compose.yml logs -f backend
docker-compose -f docker/docker-compose.yml logs -f frontend
```

### 5. 停止服务

```bash
docker-compose -f docker/docker-compose.yml down
```

### 6. 重启服务

```bash
docker-compose -f docker/docker-compose.yml restart
```

## 生产环境部署

### 1. 服务器准备

#### 更新系统
```bash
sudo apt update && sudo apt upgrade -y
```

#### 安装Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### 安装Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 配置Nginx

#### 安装Nginx
```bash
sudo apt install nginx -y
```

#### 配置SSL证书（使用Let's Encrypt）
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

#### 更新Nginx配置
```bash
sudo nano /etc/nginx/sites-available/wechat-ai-writer
```

添加以下配置：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    client_max_body_size 20M;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /flower/ {
        proxy_pass http://localhost:5555/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/wechat-ai-writer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. 配置防火墙

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 4. 设置自动启动

#### 使用Systemd
创建服务文件 `/etc/systemd/system/wechat-ai-writer.service`:

```ini
[Unit]
Description=WeChat AI Writer Pro
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/wechat-ai-writer-pro
ExecStart=/usr/local/bin/docker-compose -f docker/docker-compose.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker/docker-compose.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl enable wechat-ai-writer
sudo systemctl start wechat-ai-writer
```

### 5. 配置备份

#### 数据库备份脚本
创建 `backup.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker exec wechat_ai_writer_postgres pg_dump -U postgres wechat_ai_writer > $BACKUP_DIR/postgres_$DATE.sql

# Backup Redis
docker exec wechat_ai_writer_redis redis-cli BGSAVE

# Keep only last 7 days
find $BACKUP_DIR -name "postgres_*.sql" -mtime +7 -delete
```

设置定时任务：
```bash
crontab -e
# 添加每天凌晨2点备份
0 2 * * * /path/to/backup.sh
```

## 监控和维护

### 1. 查看服务状态

```bash
docker-compose -f docker/docker-compose.yml ps
```

### 2. 查看资源使用

```bash
docker stats
```

### 3. 查看日志

```bash
# 所有服务
docker-compose -f docker/docker-compose.yml logs -f

# 特定服务
docker-compose -f docker/docker-compose.yml logs -f backend
docker-compose -f docker/docker-compose.yml logs -f celery_worker
```

### 4. 更新应用

```bash
git pull
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up -d --build
```

### 5. 清理未使用的资源

```bash
docker system prune -a
```

## 故障排查

### 1. 服务无法启动

检查日志：
```bash
docker-compose -f docker/docker-compose.yml logs backend
```

常见问题：
- 端口被占用：修改 `docker-compose.yml` 中的端口映射
- 数据库连接失败：检查数据库服务是否正常启动
- 环境变量错误：检查 `.env` 文件配置

### 2. 数据库连接失败

检查数据库服务：
```bash
docker-compose -f docker/docker-compose.yml ps postgres
docker-compose -f docker/docker-compose.yml logs postgres
```

测试连接：
```bash
docker exec -it wechat_ai_writer_postgres psql -U postgres -d wechat_ai_writer
```

### 3. Redis连接失败

检查Redis服务：
```bash
docker-compose -f docker/docker-compose.yml ps redis
docker-compose -f docker/docker-compose.yml logs redis
```

测试连接：
```bash
docker exec -it wechat_ai_writer_redis redis-cli ping
```

### 4. Celery任务不执行

检查Celery服务：
```bash
docker-compose -f docker/docker-compose.yml ps celery_worker
docker-compose -f docker/docker-compose.yml logs celery_worker
```

查看任务队列：
```bash
docker-compose -f docker/docker-compose.yml logs flower
```

访问Flower监控：http://localhost:5555

### 5. 前端无法访问后端

检查CORS配置：
```bash
# 查看后端日志
docker-compose -f docker/docker-compose.yml logs backend
```

检查环境变量：
```bash
# 确认 NEXT_PUBLIC_API_URL 配置正确
cat .env | grep NEXT_PUBLIC_API_URL
```

## 性能优化

### 1. 数据库优化

#### 连接池配置
在 `.env` 中调整：
```env
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
```

#### 查询优化
- 添加适当的索引
- 使用分页查询
- 避免N+1查询

### 2. Redis优化

#### 内存配置
在 `docker/docker-compose.yml` 中添加：
```yaml
redis:
  command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

### 3. 应用优化

#### 启用缓存
```python
# 在API中使用缓存
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
```

#### 异步处理
使用Celery处理耗时任务：
```python
from app.tasks.celery_app import celery_app

@celery_app.task
def async_generate_article(topic):
    # 耗时操作
    pass
```

## 安全建议

1. **定期更新依赖**
   ```bash
   cd backend && pip list --outdated
   cd frontend && npm outdated
   ```

2. **使用强密码**
   ```bash
   # 生成随机密码
   openssl rand -base64 32
   ```

3. **启用HTTPS**
   - 使用Let's Encrypt免费SSL证书
   - 强制HTTPS重定向

4. **限制API访问**
   - 使用API密钥认证
   - 实现速率限制

5. **定期备份**
   - 数据库每日备份
   - 配置文件备份
   - 保留7-30天的备份

6. **监控日志**
   - 设置日志告警
   - 定期检查异常日志

## 联系支持

如遇到问题，请：
1. 查看本文档的故障排查部分
2. 检查GitHub Issues
3. 联系技术支持团队
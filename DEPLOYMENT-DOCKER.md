# Docker 镜像部署指南

本指南说明如何将项目打包成 Docker 镜像并部署到任何支持 Docker 的环境。

## 📦 打包和发布镜像

### 1. 在 Windows 10 上构建镜像

**前提条件：**
- Docker Desktop 已安装并运行
- Docker Hub 账号

**步骤：**

```powershell
# 进入项目目录
cd G:\db\guwen\gzh

# 方式一：使用构建脚本（推荐）
.\build-and-push.ps1 -DockerHubUsername "your-dockerhub-username" -Version "v1.0.0"

# 方式二：手动构建
docker build -t your-dockerhub-username/wechat-ai-writer-pro:v1.0.0 .
docker push your-dockerhub-username/wechat-ai-writer-pro:v1.0.0
```

### 2. 在 Linux 上构建镜像

```bash
# 进入项目目录
cd /path/to/gzh

# 给脚本添加执行权限
chmod +x build-and-push.sh

# 构建并推送
./build-and-push.sh
```

## 🚀 在 CentOS 7 上部署

### 1. 创建部署目录

```bash
mkdir -p /opt/wechat-ai-writer
cd /opt/wechat-ai-writer
```

### 2. 下载 docker-compose 配置文件

```bash
# 从 Windows 复制 docker-compose.standalone.yml 到 CentOS
# 或者使用 curl/wget 下载（如果已上传到服务器）

# 创建 .env 文件
cat > .env << EOF
DOCKER_IMAGE=your-dockerhub-username/wechat-ai-writer-pro:latest
SECRET_KEY=your-secret-key-change-in-production
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
WECHAT_APP_ID=your-wechat-app-id
WECHAT_APP_SECRET=your-wechat-app-secret
EOF
```

### 3. 启动服务

```bash
# 拉取镜像
docker-compose -f docker-compose.standalone.yml pull

# 启动所有服务
docker-compose -f docker-compose.standalone.yml up -d

# 查看服务状态
docker-compose -f docker-compose.standalone.yml ps

# 查看日志
docker-compose -f docker-compose.standalone.yml logs -f
```

### 4. 配置防火墙

```bash
# 开放必要端口
firewall-cmd --permanent --add-port=3000/tcp
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --permanent --add-port=5555/tcp
firewall-cmd --reload
```

### 5. 访问服务

在浏览器中访问：
- 前端：`http://<CentOS_IP>:3000`
- 后端 API：`http://<CentOS_IP>:8000`
- API 文档：`http://<CentOS_IP>:8000/docs`
- Celery 监控：`http://<CentOS_IP>:5555`

## 📝 常用命令

```bash
# 停止服务
docker-compose -f docker-compose.standalone.yml down

# 重启服务
docker-compose -f docker-compose.standalone.yml restart

# 查看某个服务的日志
docker-compose -f docker-compose.standalone.yml logs -f app

# 进入容器
docker exec -it wechat_ai_writer_app bash

# 更新镜像
docker-compose -f docker-compose.standalone.yml pull
docker-compose -f docker-compose.standalone.yml up -d

# 清理数据（谨慎使用）
docker-compose -f docker-compose.standalone.yml down -v
```

## 🔧 环境变量说明

在 `.env` 文件中配置以下变量：

| 变量名 | 说明 | 必填 |
|--------|------|------|
| DOCKER_IMAGE | Docker 镜像地址 | 是 |
| SECRET_KEY | 应用密钥 | 是 |
| OPENAI_API_KEY | OpenAI API Key | 是 |
| OPENAI_BASE_URL | OpenAI API 地址 | 否 |
| WECHAT_APP_ID | 微信公众号 AppID | 是 |
| WECHAT_APP_SECRET | 微信公众号 AppSecret | 是 |

## 📊 镜像大小优化

如果镜像过大，可以：

1. 使用 `.dockerignore` 文件排除不必要的文件
2. 使用多阶段构建（已在 Dockerfile 中实现）
3. 清理不必要的依赖

## 🐛 故障排查

### 镜像拉取失败
```bash
# 检查网络连接
ping docker.io

# 配置 Docker 镜像加速器（国内）
# 编辑 /etc/docker/daemon.json
{
  "registry-mirrors": ["https://docker.mirrors.ustc.edu.cn"]
}

# 重启 Docker
systemctl restart docker
```

### 容器启动失败
```bash
# 查看详细日志
docker-compose -f docker-compose.standalone.yml logs

# 检查环境变量
docker exec -it wechat_ai_writer_app env

# 检查数据库连接
docker exec -it wechat_ai_writer_postgres psql -U postgres -d wechat_ai_writer
```

### 端口冲突
```bash
# 检查端口占用
netstat -tulnp | grep -E '3000|8000|5555'

# 修改 docker-compose.standalone.yml 中的端口映射
```

## 🔄 版本更新

当有新版本时：

```bash
# 修改 .env 文件中的镜像版本
DOCKER_IMAGE=your-dockerhub-username/wechat-ai-writer-pro:v2.0.0

# 拉取新版本并重启
docker-compose -f docker-compose.standalone.yml pull
docker-compose -f docker-compose.standalone.yml up -d
```

## 💾 数据备份

```bash
# 备份数据库
docker exec wechat_ai_writer_postgres pg_dump -U postgres wechat_ai_writer > backup.sql

# 恢复数据库
docker exec -i wechat_ai_writer_postgres psql -U postgres wechat_ai_writer < backup.sql

# 备份上传文件
docker cp wechat_ai_writer_app:/app/uploads ./backups/uploads
```

## 🎉 完成后验证

```bash
# 检查所有容器是否正常运行
docker-compose -f docker-compose.standalone.yml ps

# 测试 API
curl http://localhost:8000/api/health

# 测试前端
curl http://localhost:3000
```

---

**注意：** 请确保在生产环境中：
1. 使用强密码和安全的 SECRET_KEY
2. 配置 HTTPS
3. 定期备份数据
4. 监控日志和性能
# 🚀 一键自动化部署指南

## 方案一：Vercel 一键部署（最推荐！）

### 第一步：点击按钮部署

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FKite7928%2Fmole&env=OPENAI_API_KEY,WECHAT_APP_ID,WECHAT_APP_SECRET,DATABASE_URL,REDIS_URL,SECRET_KEY&envDescription=所需的环境变量配置&envLink=https%3A%2F%2Fgithub.com%2FKite7928%2Fmole%2Fblob%2Fmain%2F.env.example&project-name=wechat-ai-writer&repository-name=wechat-ai-writer)

**点击上面的按钮后：**
1. Vercel 会自动 fork 你的仓库
2. 自动配置环境变量（根据 .env.example）
3. 自动构建和部署
4. **以后每次 git push 都会自动重新部署！**

### 第二步：配置数据库（Vercel Postgres）

在 Vercel 控制台：
1. 进入项目 → Storage → Connect Database
2. 选择 Postgres → Create New
3. 会自动设置 `DATABASE_URL` 环境变量

### 第三步：配置 Redis（Upstash）

在 Vercel 控制台：
1. 进入项目 → Storage → Connect Database
2. 选择 Redis → Create New
3. 会自动设置 `REDIS_URL` 环境变量

### 第四步：设置其他环境变量

在 Vercel 控制台 → Settings → Environment Variables 中添加：
- `OPENAI_API_KEY`: 你的 OpenAI API Key
- `WECHAT_APP_ID`: 微信公众号 App ID
- `WECHAT_APP_SECRET`: 微信公众号 App Secret
- `SECRET_KEY`: 随机生成的密钥（可用：`openssl rand -hex 32`）

**完成！以后只需要 `git push`，Vercel 就会自动部署！**

---

## 方案二：Railway 一键部署

### 第一步：点击按钮部署

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2FKite7928%2Fmole)

### 第二步：配置环境变量

Railway 会自动提供 Postgres 和 Redis，只需添加：
- `OPENAI_API_KEY`
- `WECHAT_APP_ID`
- `WECHAT_APP_SECRET`
- `SECRET_KEY`

**完成！以后 git push 自动部署！**

---

## 方案三：自托管服务器（完全控制）

### 使用 GitHub Actions 自动部署到你的服务器

**前提条件：**
- 有一台 Linux 服务器（VPS）
- 服务器已安装 Docker 和 Docker Compose

### 配置步骤：

#### 1. 在 GitHub 设置 Secrets

进入 GitHub 仓库 → Settings → Secrets and variables → Actions，添加：

- `SERVER_HOST`: 服务器 IP 地址
- `SERVER_USER`: SSH 用户名（通常是 `root` 或 `ubuntu`）
- `SERVER_SSH_KEY`: SSH 私钥（用 `cat ~/.ssh/id_rsa` 查看）
- `DOCKER_USERNAME`: Docker Hub 用户名（如果需要）
- `DOCKER_PASSWORD`: Docker Hub 密码（如果需要）

#### 2. 在服务器上准备环境

SSH 登录服务器后：

```bash
# 安装 Docker（如果还没有）
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 创建部署目录
sudo mkdir -p /opt/wechat-ai-writer
sudo chown $USER:$USER /opt/wechat-ai-writer

# 配置环境变量
cd /opt/wechat-ai-writer
git clone https://github.com/Kite7928/mole.git .
cp .env.example .env
nano .env  # 编辑配置文件
```

#### 3. 推送代码触发部署

```bash
git add .
git commit -m "feat: 启用自动部署"
git push origin main
```

**GitHub Actions 会自动：**
1. 运行测试
2. 构建 Docker 镜像
3. 推送到 Docker Hub
4. SSH 到服务器
5. 拉取最新代码
6. 重启容器

**完成！以后每次 push 到 main 分支都会自动部署！**

---

## 📋 环境变量快速生成

### 生成 SECRET_KEY

```bash
# Linux/Mac
openssl rand -hex 32

# Windows PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

### 获取微信公众号配置

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 开发 → 基本配置
3. 复制 AppID 和 AppSecret

---

## 🎉 推荐方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **Vercel** | 最简单，免费额度大，全球 CDN | Serverless 限制，冷启动 | ⭐⭐⭐⭐⭐ |
| **Railway** | 支持长期运行任务，配置简单 | 免费额度较小 | ⭐⭐⭐⭐ |
| **自托管** | 完全控制，无限制 | 需要维护服务器 | ⭐⭐⭐ |

---

## 💡 小贴士

### Vercel 部署注意事项

- Vercel 适合**前端 + API**，如果需要**长期运行的后台任务**（Celery Worker），建议结合 Railway
- Vercel Serverless Function 有 10 秒超时限制（Pro 版 60 秒）

### Railway 部署注意事项

- Railway 免费版有 $5/月额度，超出需付费
- 适合运行 Celery Worker、Beat 等后台服务

### 混合部署方案（最佳实践！）

1. **前端 + API** → Vercel（快速、免费、全球 CDN）
2. **后台任务** → Railway（长期运行、无冷启动）
3. **数据库** → Vercel Postgres + Upstash Redis（免费版够用）

这样可以发挥各平台的优势！

---

## 🆘 常见问题

### Q: 部署后访问 404？
A: 检查 vercel.json 配置，确保路由正确

### Q: 环境变量不生效？
A: 在 Vercel/Railway 控制台重新部署（Redeploy）

### Q: 数据库连接失败？
A: 检查 DATABASE_URL 格式，Vercel 使用 `postgresql://` 而非 `postgresql+asyncpg://`

### Q: Celery 任务不执行？
A: Railway 确保启动了 celery-worker 和 celery-beat 服务

---

**祝你部署愉快！有问题随时问我～** 🎉

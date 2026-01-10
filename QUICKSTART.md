# ⚡ 快速开始 - 5分钟完成部署

## 🎯 最简单的方式：一键部署到 Vercel

### 第 1 步：点击部署按钮

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FKite7928%2Fmole&env=OPENAI_API_KEY,WECHAT_APP_ID,WECHAT_APP_SECRET,DATABASE_URL,REDIS_URL,SECRET_KEY&envDescription=所需的环境变量配置&envLink=https%3A%2F%2Fgithub.com%2FKite7928%2Fmole%2Fblob%2Fmain%2F.env.example&project-name=wechat-ai-writer&repository-name=wechat-ai-writer)

### 第 2 步：准备环境变量

在部署过程中，Vercel 会要求你填写以下环境变量：

#### 必填项：

1. **OPENAI_API_KEY**
   - 获取方式：访问 [OpenAI Platform](https://platform.openai.com/api-keys)
   - 示例：`sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxx`

2. **WECHAT_APP_ID**
   - 获取方式：登录 [微信公众平台](https://mp.weixin.qq.com/) → 开发 → 基本配置
   - 示例：`wx1234567890abcdef`

3. **WECHAT_APP_SECRET**
   - 获取方式：同上，点击"重置"按钮获取
   - 示例：`abcdef1234567890abcdef1234567890`

4. **SECRET_KEY**
   - 生成方式：
     ```bash
     # Linux/Mac
     openssl rand -hex 32

     # Windows PowerShell
     -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | % {[char]$_})
     ```
   - 示例：`a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6`

#### 可选项（稍后配置）：

- `DATABASE_URL` - 稍后在 Vercel Storage 中添加 Postgres 时自动设置
- `REDIS_URL` - 稍后在 Vercel Storage 中添加 Redis 时自动设置

### 第 3 步：添加数据库

部署完成后，在 Vercel 控制台：

1. **添加 PostgreSQL**
   - 进入项目 → Storage → Create Database
   - 选择 **Postgres** → Create
   - 会自动设置 `POSTGRES_*` 环境变量

2. **添加 Redis**
   - 同样在 Storage → Create Database
   - 选择 **Redis** (Upstash) → Create
   - 会自动设置 `KV_*` 环境变量

3. **重新部署**
   - Deployments → 最新部署 → 右侧菜单 → Redeploy

### 第 4 步：访问应用

🎉 完成！你的应用已经部署成功！

- 前端：`https://your-project.vercel.app`
- API 文档：`https://your-project.vercel.app/api/docs`

---

## 🚀 其他部署方式

### Railway（适合需要后台任务的场景）

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2FKite7928%2Fmole)

**优势：**
- 支持长期运行的 Celery Worker
- 自动提供 Postgres 和 Redis
- 无冷启动问题

**步骤：**
1. 点击按钮
2. 填写相同的环境变量
3. Railway 会自动创建数据库并部署

---

## 🛠️ 自动化配置脚本

如果你想更快速地配置，可以使用我们提供的脚本：

### Windows（PowerShell）

```powershell
# 进入项目目录
cd G:\db\guwen\gzh

# 运行配置脚本
.\scripts\setup-deploy.ps1
```

### Linux/Mac（Bash）

```bash
# 进入项目目录
cd ~/projects/gzh

# 添加执行权限
chmod +x scripts/setup-deploy.sh

# 运行配置脚本
./scripts/setup-deploy.sh
```

脚本会引导你：
1. 选择部署平台
2. 输入必要的配置
3. 自动设置 GitHub Secrets（如果选择自托管）
4. 生成环境变量配置

---

## 📋 环境变量完整清单

### 核心配置

| 变量名 | 说明 | 必填 | 示例 |
|--------|------|------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | ✅ | `sk-proj-xxx` |
| `WECHAT_APP_ID` | 微信公众号 AppID | ✅ | `wx1234567890` |
| `WECHAT_APP_SECRET` | 微信公众号密钥 | ✅ | `abcdef123456` |
| `SECRET_KEY` | 应用密钥 | ✅ | 随机生成 |
| `DATABASE_URL` | PostgreSQL 连接 | ✅ | 自动设置 |
| `REDIS_URL` | Redis 连接 | ✅ | 自动设置 |

### 可选配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_BASE_URL` | OpenAI API 地址 | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | 使用的模型 | `gpt-4-turbo-preview` |
| `DEBUG` | 调试模式 | `False` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

---

## ⚠️ 常见问题

### 1. 部署后访问 404？

**原因：** Next.js 构建路径配置问题

**解决：**
```bash
# 检查 vercel.json 中的 outputDirectory
# 确保指向 frontend/.next
```

### 2. API 请求失败？

**原因：** CORS 或环境变量未设置

**解决：**
1. 检查 `NEXT_PUBLIC_API_URL` 是否正确
2. 在 Vercel 控制台 Redeploy

### 3. 数据库连接失败？

**原因：** 连接字符串格式错误

**解决：**
```bash
# Vercel Postgres 使用的格式：
postgresql://user:pass@host:5432/db

# 而不是：
postgresql+asyncpg://user:pass@host:5432/db
```

### 4. Celery 任务不执行？

**原因：** Vercel 不支持长期运行任务

**解决：**
- 使用 Railway 部署后台任务
- 或者使用混合部署方案

---

## 🎯 推荐部署方案

根据你的需求选择：

### 方案 A：纯 Vercel（适合轻量使用）

✅ 优点：
- 完全免费
- 全球 CDN
- 自动 HTTPS

❌ 限制：
- Serverless Function 有超时限制
- 不适合长期运行任务

**适用场景：**
- 个人使用
- 偶尔发布文章
- 不需要定时任务

### 方案 B：纯 Railway（适合频繁使用）

✅ 优点：
- 支持后台任务
- 无冷启动
- 完整功能

❌ 限制：
- 免费额度有限（$5/月）
- CDN 不如 Vercel

**适用场景：**
- 团队使用
- 需要定时任务
- 频繁发布文章

### 方案 C：混合部署（最佳实践！）⭐

**架构：**
- 前端 + API → Vercel（快速、免费）
- 后台任务 → Railway（可靠、稳定）
- 数据库 → Vercel Postgres + Upstash Redis

**配置：**
1. 在 Vercel 部署前端和 API
2. 在 Railway 部署 Celery Worker
3. 两者共享相同的数据库连接

**成本：**
- Vercel: 免费
- Railway: $5/月（如果超出免费额度）
- 数据库: 免费

---

## 🆘 需要帮助？

- 📖 查看完整文档：[DEPLOY.md](./DEPLOY.md)
- 💬 提交 Issue：[GitHub Issues](https://github.com/Kite7928/mole/issues)
- 📧 联系作者：[提交问题](https://github.com/Kite7928/mole/issues/new)

---

**祝你部署成功！** 🎉

如果这个项目对你有帮助，别忘了给个 ⭐ Star！

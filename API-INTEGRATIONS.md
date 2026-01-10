# API 集成说明文档

本文档详细说明了项目中集成的所有第三方API及其配置方法。

## 目录

1. [数据分析API](#数据分析api)
2. [国内AI模型](#国内ai模型)
3. [图片生成API](#图片生成api)
4. [GitHub API](#github-api)

---

## 数据分析API

### 功能概述

数据分析API集成了多个数据平台，用于获取关键词趋势、热门话题和竞品分析数据。

### 支持的平台

1. **百度指数**
   - 获取关键词搜索趋势
   - 分析用户关注度
   - 预测趋势走向

2. **微信指数**
   - 获取微信生态内关键词热度
   - 分析社交传播力
   - 评估内容影响力

3. **微博热搜**
   - 实时获取热门话题
   - 监控热点趋势
   - 发现内容创作灵感

### 配置方法

在 `.env` 文件中添加以下配置：

```bash
# 百度指数
BAIDU_INDEX_API_KEY=your-baidu-index-api-key
BAIDU_INDEX_SECRET=your-baidu-index-secret

# 微信指数
WECHAT_INDEX_API_KEY=your-wechat-index-api-key
WECHAT_INDEX_SECRET=your-wechat-index-secret

# 微博API
WEIBO_API_KEY=your-weibo-api-key
WEIBO_API_SECRET=your-weibo-api-secret
WEIBO_REDIRECT_URI=https://your-domain.com/callback
```

### API端点

- `POST /api/integrations/data-analysis/baidu-index` - 获取百度指数
- `POST /api/integrations/data-analysis/wechat-index` - 获取微信指数
- `GET /api/integrations/data-analysis/weibo-hot` - 获取微博热搜
- `POST /api/integrations/data-analysis/keyword-trend` - 分析关键词趋势
- `GET /api/integrations/data-analysis/hot-keywords` - 获取热门关键词
- `POST /api/integrations/data-analysis/competitor-analysis` - 竞品分析

### 使用示例

```python
# 获取百度指数
response = await data_analysis_service.fetch_baidu_index(
    keywords=["人工智能", "ChatGPT"],
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# 获取微博热搜
response = await data_analysis_service.fetch_weibo_hot_topics(limit=20)

# 分析关键词趋势
response = await data_analysis_service.analyze_keyword_trend(
    keyword="人工智能",
    platform="all"
)
```

---

## 国内AI模型

### 功能概述

集成了国内主流AI大模型，提供文本生成、内容创作等功能。

### 支持的模型

1. **文心一言 (ERNIE)**
   - 百度推出的知识增强大语言模型
   - 支持长文本理解和生成
   - 适合专业内容创作

2. **通义千问 (Qwen)**
   - 阿里云通义千问大语言模型
   - 强大的多轮对话能力
   - 支持多种写作风格

3. **讯飞星火 (Spark)**
   - 科大讯飞星火认知大模型
   - 优秀的中文理解能力
   - 适合创意写作

### 配置方法

在 `.env` 文件中添加以下配置：

```bash
# 文心一言
ERNIE_API_KEY=your-ernie-api-key
ERNIE_SECRET_KEY=your-ernie-secret-key
ERNIE_MODEL=ernie-bot-4

# 通义千问
QWEN_API_KEY=your-qwen-api-key
QWEN_MODEL=qwen-max

# 讯飞星火
SPARK_API_KEY=your-spark-api-key
SPARK_API_SECRET=your-spark-api-secret
SPARK_APP_ID=your-spark-app-id
SPARK_MODEL=spark-4.0
```

### API端点

- `POST /api/integrations/domestic-ai/titles/generate` - 生成标题
- `POST /api/integrations/domestic-ai/content/generate` - 生成文章内容

### 使用示例

```python
# 使用文心一言生成标题
response = await domestic_ai_service.generate_titles_with_domestic(
    topic="人工智能",
    count=5,
    model="ernie"
)

# 使用通义千问生成文章内容
response = await domestic_ai_service.generate_content_with_domestic(
    topic="人工智能",
    title="AI技术发展趋势",
    style="professional",
    length="medium",
    model="qwen"
)
```

---

## 图片生成API

### 功能概述

集成了多个图片生成平台，支持文本到图像的生成、编辑和优化。

### 支持的平台

1. **DALL-E**
   - OpenAI的文本到图像生成模型
   - 高质量图像生成
   - 支持多种尺寸和风格

2. **Midjourney**
   - 强大的AI图像生成工具
   - 艺术风格丰富
   - 适合创意设计

3. **Stable Diffusion**
   - 开源的图像生成模型
   - 高度可定制
   - 支持本地部署

### 配置方法

在 `.env` 文件中添加以下配置：

```bash
# DALL-E
DALL_E_API_KEY=your-dalle-api-key
DALL_E_MODEL=dall-e-3
DALL_E_SIZE=1024x1024
DALL_E_QUALITY=standard

# Midjourney
MIDJOURNEY_API_KEY=your-midjourney-api-key
MIDJOURNEY_BASE_URL=https://api.midjourney.com/v1

# Stable Diffusion
STABLE_DIFFUSION_API_KEY=your-stable-diffusion-api-key
STABLE_DIFFUSION_BASE_URL=https://api.stability.ai/v1
STABLE_DIFFUSION_MODEL=stable-diffusion-xl-1024-v1-0
```

### API端点

- `POST /api/integrations/image-generation/generate` - 生成图片
- `POST /api/integrations/image-generation/article-cover` - 生成文章封面
- `POST /api/integrations/image-generation/infographic` - 生成信息图
- `POST /api/integrations/image-generation/edit` - 编辑图片

### 使用示例

```python
# 使用DALL-E生成图片
response = await image_generation_service.generate_with_dalle(
    prompt="A futuristic cityscape at sunset",
    size="1024x1024",
    quality="hd",
    n=1
)

# 生成文章封面
response = await image_generation_service.generate_article_cover(
    topic="人工智能",
    style="professional",
    provider="dalle"
)

# 生成信息图
response = await image_generation_service.generate_infographic(
    data={"title": "AI发展趋势", "values": [10, 20, 30, 40]},
    style="modern"
)
```

---

## GitHub API

### 功能概述

集成GitHub API，实现代码仓库管理、issue跟踪、PR管理和Webhook功能。

### 功能特性

1. **仓库管理**
   - 获取仓库信息
   - 查看提交记录
   - 监控仓库状态

2. **Issue管理**
   - 列出Issues
   - 创建新Issue
   - 跟踪问题状态

3. **Pull Request管理**
   - 列出PRs
   - 创建PR
   - 查看PR详情

4. **Webhook支持**
   - 接收GitHub事件
   - 验证签名
   - 自动化处理

### 配置方法

在 `.env` 文件中添加以下配置：

```bash
# GitHub API
GITHUB_TOKEN=your-github-token
GITHUB_API_BASE_URL=https://api.github.com
GITHUB_WEBHOOK_SECRET=your-webhook-secret
GITHUB_REPO_OWNER=your-repo-owner
GITHUB_REPO_NAME=your-repo-name
```

### 获取GitHub Token

1. 登录GitHub
2. 进入 Settings → Developer settings → Personal access tokens
3. 点击 "Generate new token"
4. 选择所需的权限（repo, issues, pull_requests等）
5. 生成并复制token

### 配置Webhook

1. 进入GitHub仓库设置
2. 选择 Webhooks → Add webhook
3. 设置Payload URL: `https://your-domain.com/api/integrations/github/webhook`
4. 设置Content type: `application/json`
5. 设置Secret（与.env中的GITHUB_WEBHOOK_SECRET相同）
6. 选择需要触发的事件

### API端点

- `GET /api/integrations/github/repository` - 获取仓库信息
- `GET /api/integrations/github/issues` - 列出Issues
- `POST /api/integrations/github/issues/create` - 创建Issue
- `GET /api/integrations/github/pull-requests` - 列出PRs
- `POST /api/integrations/github/pull-requests/create` - 创建PR
- `GET /api/integrations/github/commits` - 获取提交记录
- `POST /api/integrations/github/webhook` - 处理Webhook事件

### 使用示例

```python
# 获取仓库信息
response = await github_service.get_repository_info(
    owner="Kite7928",
    repo="mole"
)

# 列出Issues
response = await github_service.list_issues(
    owner="Kite7928",
    repo="mole",
    state="open",
    limit=20
)

# 创建Issue
response = await github_service.create_issue(
    title="新增功能建议",
    body="建议添加数据分析API集成",
    owner="Kite7928",
    repo="mole",
    labels=["enhancement"]
)

# 创建Pull Request
response = await github_service.create_pull_request(
    title="添加数据分析API",
    body="实现了百度指数、微信指数、微博热搜等功能",
    head="feature/data-analysis",
    base="main",
    owner="Kite7928",
    repo="mole"
)
```

---

## 前端使用

前端提供了统一的界面来管理和使用这些API集成。

### 访问集成管理页面

访问 `/integrations` 路径，可以看到所有集成的API服务。

### 功能模块

1. **数据分析**
   - 查看百度指数
   - 查看微信指数
   - 查看微博热搜
   - 分析关键词趋势

2. **国内AI**
   - 测试文心一言
   - 测试通义千问
   - 测试讯飞星火

3. **图片生成**
   - 使用DALL-E生成图片
   - 使用Midjourney生成图片
   - 使用Stable Diffusion生成图片

4. **GitHub**
   - 查看仓库信息
   - 管理Issues
   - 管理Pull Requests
   - 查看提交记录

---

## 注意事项

1. **API密钥安全**
   - 不要将API密钥提交到代码仓库
   - 使用环境变量存储敏感信息
   - 定期轮换API密钥

2. **速率限制**
   - 注意各API的速率限制
   - 实现适当的缓存机制
   - 避免频繁请求

3. **错误处理**
   - 所有API调用都包含错误处理
   - 记录详细的错误日志
   - 提供友好的错误提示

4. **成本控制**
   - 监控API使用量
   - 设置使用限额
   - 定期检查账单

---

## 故障排查

### 常见问题

1. **API密钥无效**
   - 检查.env文件中的配置
   - 确认API密钥是否正确
   - 检查API密钥是否过期

2. **请求超时**
   - 检查网络连接
   - 增加超时时间
   - 检查API服务状态

3. **权限不足**
   - 检查API密钥权限
   - 确认账户状态
   - 联系API提供商

---

## 联系支持

如有问题，请通过以下方式联系：

- GitHub Issues: https://github.com/Kite7928/mole/issues
- 邮箱: support@example.com

---

**最后更新**: 2026-01-10
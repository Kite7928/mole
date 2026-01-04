# AI公众号自动写作助手 Pro

一个基于AI的智能微信公众号内容生成与发布系统，支持自动选题、智能写作、图片生成和多平台发布。

## 🚀 核心特性

### 智能写作引擎
- 多模型支持 (GPT-4, Claude, DeepSeek, Gemini)
- 智能标题生成与优化
- 深度内容创作
- 风格迁移与润色
- 知识库增强

### 数据采集系统
- 实时热点监控 (IT之家, 36氪, 百度热搜等)
- 智能去重与过滤
- 热度计算与推荐
- 自定义RSS源支持

### 图片处理
- AI封面图生成
- 多源图片搜索
- 智能裁剪与优化
- 水印添加
- CDN加速

### 微信集成
- 多账号管理
- 自动草稿发布
- 定时发布
- 素材库管理
- 数据统计

### 任务调度
- 灵活的定时任务
- 失败重试机制
- 任务依赖管理
- 实时监控告警

## 📋 技术栈

### 后端
- **框架**: FastAPI (Python 3.10+)
- **数据库**: PostgreSQL + Redis
- **任务队列**: Celery
- **ORM**: SQLAlchemy 2.0
- **AI集成**: OpenAI SDK
- **图片处理**: Pillow + OpenCV
- **爬虫**: Playwright + httpx

### 前端
- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **UI库**: shadcn/ui + TailwindCSS
- **状态管理**: Zustand + React Query
- **图表**: Recharts
- **富文本**: Tiptap

### 部署
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **监控**: Prometheus + Grafana
- **日志**: ELK Stack

## 🏗️ 项目结构

```
.
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   ├── tasks/          # 异步任务
│   │   └── utils/          # 工具函数
│   ├── tests/              # 测试用例
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端应用
│   ├── app/                # Next.js应用目录
│   ├── components/         # React组件
│   ├── lib/                # 工具库
│   ├── public/             # 静态资源
│   └── package.json        # Node依赖
├── docker/                 # Docker配置
├── docs/                   # 文档
└── scripts/                # 脚本工具
```

## 🚦 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

### 安装步骤

1. 克隆仓库
```bash
git clone <repository-url>
cd wechat-ai-writer-pro
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的配置
```

3. 启动服务 (使用Docker Compose)
```bash
docker-compose up -d
```

4. 访问应用
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 📖 使用指南

### 1. 配置AI模型
在设置页面配置你的LLM API Key和Base URL。

### 2. 绑定微信公众号
在公众号配置中填入AppID和AppSecret。

### 3. 创建文章
- 选择主题来源 (手动输入/AI热点/搜索)
- 选择或生成标题
- 编辑正文内容
- 预览并发布

### 4. 设置定时任务
配置自动发布规则，系统将自动生成和发布文章。

## 🔧 配置说明

主要环境变量配置:

```env
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/wechat_ai_writer
REDIS_URL=redis://localhost:6379/0

# AI配置
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# 微信配置
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret

# 其他配置
SECRET_KEY=your_secret_key
ALLOWED_ORIGINS=http://localhost:3000
```

## 📊 功能对比

| 功能 | 基础版 | Pro版 |
|------|--------|-------|
| AI写作 | ✅ | ✅ |
| 多模型支持 | ❌ | ✅ |
| 深度研究 | ❌ | ✅ |
| 图片生成 | ❌ | ✅ |
| 定时任务 | ✅ | ✅ |
| 数据统计 | ❌ | ✅ |
| 多账号管理 | ❌ | ✅ |
| 协作功能 | ❌ | ✅ |
| API开放 | ❌ | ✅ |

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📝 许可证

MIT License

## 📧 联系方式

如有问题，请提交Issue或联系开发者。

---

**注意**: 本项目仅供学习和研究使用，请遵守相关法律法规和平台规则。
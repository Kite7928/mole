# myworkflow - AI公众号写作助手开发规范工作流

## 项目概述

本项目是基于AI的智能微信公众号内容生成与发布系统，采用前后端分离架构：
- **前端**: Next.js 14 + React 18 + TypeScript + Tailwind CSS
- **后端**: FastAPI + Python 3.10 + SQLite（异步）
- **AI引擎**: 支持 OpenAI、DeepSeek、Gemini、Claude 等多种模型
- **发布集成**: 微信公众号 API 自动发布到草稿箱

### 核心功能

- 🤖 **AI驱动**: 支持多种AI模型（OpenAI、DeepSeek、Gemini、Claude），支持流式响应
- 📰 **热点抓取**: 自动抓取IT之家、百度资讯等热点新闻
- ✍️ **智能写作**: 一键生成标题、正文，支持多种风格模板
- 🖼️ **图片处理**: 自动下载、裁剪、上传封面图，支持AI生成封面
- 📊 **数据图表**: 支持生成数据可视化图表嵌入文章
- 📱 **微信集成**: 自动发布到公众号草稿箱
- 🚀 **新手引导**: 首次使用配置向导和界面引导
- 📊 **仪表盘**: 首页数据统计和快捷操作
- 🎨 **模板系统**: 支持自定义写作模板和样式

## 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- DeepSeek/OpenAI/Gemini API Key（至少配置一个）
- 微信公众号 AppID 和 AppSecret（可选，用于发布）

### 启动步骤

#### 方法一：使用启动脚本（推荐）

```powershell
# Windows - 双击运行或命令行执行
.\start-simple.bat

# 脚本会自动完成：
# - 检查Python环境
# - 自动处理端口占用（端口8000和3000）
# - 启动后端服务（端口8000）
# - 启动前端开发服务器（端口3000）
```

**启动脚本参数：**
```powershell
# 仅启动后端
.\start-simple.ps1 -b

# 仅启动前端
.\start-simple.ps1 -f

# 强制关闭占用端口的进程
.\start-simple.ps1 -k
```

#### 方法二：手动启动

**后端服务:**
```bash
cd backend
pip install -r requirements.txt
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**前端开发:**
```bash
cd frontend
npm install
npm run dev        # 开发模式 http://localhost:3000
npm run build      # 生产构建
npm run start      # 生产启动
```

### 访问应用

- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 开发工作流

### 触发方式

```bash
# 启动 iFlow CLI
iflow

# 使用斜杠命令触发工作流
/myworkflow [您的需求描述]

# 或直接用自然语言描述
"帮我添加一个新功能：用户可以上传头像"
```

### 工作流程

```
用户需求 → 深度思考 → 任务规划 → 信息检索 → 代码实现 → 自动验证 → 质量审查 → 决策
```

### 核心原则

- 🧠 **强制深度思考**: 任何时候必须首先使用 sequential-thinking 工具梳理问题
- 🇨🇳 **强制中文规范**: 所有输出必须使用简体中文（代码标识符除外）
- 🔒 **自动验证机制**: 本地自动执行测试和审查
- 🤖 **质量评分系统**: 自动评分并决定通过/退回
- 🏗️ **标准化优先**: 优先复用成熟方案，禁止自研

## 项目结构

```
gzh/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   │   ├── articles.py       # 文章管理
│   │   │   ├── news.py           # 新闻抓取
│   │   │   ├── hotspots.py       # 热点监控
│   │   │   ├── unified_ai.py     # 统一AI接口
│   │   │   ├── ai_streaming.py   # AI流式响应
│   │   │   ├── wechat.py         # 微信发布
│   │   │   ├── templates.py      # 模板管理
│   │   │   ├── charts.py         # 图表生成
│   │   │   ├── creator.py        # 创作者中心
│   │   │   ├── config.py         # 系统配置
│   │   │   └── health.py         # 健康检查
│   │   ├── core/           # 核心配置
│   │   │   ├── config.py         # 应用配置
│   │   │   ├── database.py       # 数据库连接
│   │   │   ├── logger.py         # 日志配置
│   │   │   └── security.py       # 安全相关
│   │   ├── models/         # 数据模型
│   │   │   ├── article.py        # 文章模型
│   │   │   ├── news.py           # 新闻模型
│   │   │   ├── hotspot.py        # 热点模型
│   │   │   ├── template.py       # 模板模型
│   │   │   ├── config.py         # 配置模型
│   │   │   ├── ai_provider_config.py  # AI提供商配置
│   │   │   ├── batch_job.py      # 批量任务
│   │   │   ├── task.py           # 异步任务
│   │   │   └── wechat.py         # 微信相关
│   │   ├── services/       # 业务服务
│   │   │   ├── providers/        # AI提供商实现
│   │   │   │   ├── base.py       # 基础接口
│   │   │   │   ├── openai_provider.py
│   │   │   │   ├── gemini_provider.py
│   │   │   │   └── claude_provider.py
│   │   │   ├── unified_ai_service.py  # 统一AI服务
│   │   │   ├── ai_writer.py      # AI写作服务
│   │   │   ├── hotspot_service.py # 热点服务
│   │   │   ├── template_service.py # 模板服务
│   │   │   ├── wechat_service.py # 微信服务
│   │   │   ├── news_fetcher.py   # 新闻抓取
│   │   │   ├── chart_service.py  # 图表服务
│   │   │   ├── article_formatter.py # 文章格式化
│   │   │   ├── image_generation_service.py # 图片生成
│   │   │   ├── async_task_queue.py # 异步任务队列
│   │   │   └── memory_cache.py   # 内存缓存
│   │   └── main.py         # FastAPI应用入口
│   ├── tests/              # 测试文件
│   ├── uploads/            # 上传文件存储
│   ├── temp/               # 临时文件
│   └── requirements.txt    # Python依赖
│
├── frontend/               # 前端应用 (Next.js 14)
│   ├── app/               # 页面路由
│   │   ├── page.tsx       # 首页仪表盘
│   │   ├── layout.tsx     # 根布局
│   │   ├── articles/      # 文章管理
│   │   │   ├── page.tsx
│   │   │   └── create/    # 创建文章
│   │   ├── hotspots/      # 热点监控
│   │   │   └── page.tsx
│   │   └── settings/      # 系统设置
│   │       └── page.tsx
│   ├── components/        # React组件
│   │   ├── layout/        # 布局组件
│   │   │   ├── sidebar.tsx
│   │   │   ├── header.tsx
│   │   │   ├── resizable-sidebar.tsx
│   │   │   └── brightness-control.tsx
│   │   ├── onboarding/    # 新手引导
│   │   │   ├── onboarding-modal.tsx
│   │   │   ├── config-wizard.tsx
│   │   │   ├── onboarding-provider.tsx
│   │   │   └── onboarding-tooltip.tsx
│   │   ├── charts/        # 图表组件
│   │   │   ├── chart-generator.tsx
│   │   │   └── data-chart.tsx
│   │   └── ui/            # UI组件（shadcn/ui）
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── badge.tsx
│   │       └── ...
│   ├── lib/               # 工具库
│   ├── hooks/             # 自定义Hooks
│   ├── types/             # TypeScript类型
│   ├── public/            # 静态资源
│   ├── package.json       # Node依赖
│   ├── next.config.js     # Next.js配置
│   ├── tailwind.config.js # Tailwind配置
│   └── tsconfig.json      # TypeScript配置
│
├── .iflow/                # 工作流配置
│   ├── IFLOW.md          # 工作流文档
│   ├── settings.json     # 工作流设置
│   ├── agents/           # Agent配置
│   │   ├── sequential-thinking.md
│   │   ├── task-manager.md
│   │   └── quality-reviewer.md
│   └── commands/         # 命令配置
│       ├── file-analysis.md
│       ├── docs-query.md
│       └── github-ops.md
│
├── .claude/               # 审查报告
│   ├── project-status-report.md
│   ├── refactor-analysis.md
│   ├── refactor-quality-report.md
│   └── verification-report.md
│
├── .github/               # GitHub Actions
│   └── workflows/
│       └── ci.yml
│
├── CLAUDE.md             # 开发规范
├── IFLOW.md              # 本文件
├── REFACTOR-SUMMARY.md   # 重构说明
├── start-simple.bat      # Windows启动脚本
├── start-simple.ps1      # PowerShell启动脚本
└── vercel.json           # Vercel部署配置
```

## 技术栈详情

### 前端依赖

```json
{
  "next": "14.1.0",
  "react": "^18.2.0",
  "typescript": "^5.3.3",
  "tailwindcss": "^3.4.0",
  "zustand": "^4.4.7",           // 状态管理
  "@tanstack/react-query": "^5.17.9",  // 数据获取
  "axios": "^1.6.5",             // HTTP客户端
  "recharts": "^2.10.3",         // 图表库
  "@tiptap/react": "^2.1.13",    // 富文本编辑器
  "socket.io-client": "^4.6.0",  // 实时通信
  "lucide-react": "^0.309.0",    // 图标库
  "date-fns": "^3.0.6",          // 日期处理
  "@radix-ui/*": "^1.x"          // UI组件基座
}
```

### 后端依赖

```
fastapi==0.109.0              # Web框架
uvicorn[standard]==0.27.0     # ASGI服务器
sqlalchemy==2.0.25            # ORM
aiosqlite==0.19.0             # 异步SQLite
openai==1.10.0                # OpenAI客户端
httpx==0.26.0                 # HTTP客户端
playwright==1.41.0            # 浏览器自动化
beautifulsoup4==4.12.3        # HTML解析
feedparser==6.0.10            # RSS解析
Pillow==10.2.0                # 图片处理
pydantic==2.5.3               # 数据验证
pytest==7.4.4                 # 测试框架
```

## 配置说明

### 环境变量

在项目根目录创建 `backend/.env` 文件：

```env
# 应用配置
APP_NAME="AI公众号写作助手"
APP_VERSION="2.0.0"
DEBUG=false

# AI配置 - 至少配置一个
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview

DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-pro

# 微信配置（用于发布到公众号）
WECHAT_APP_ID=your-wechat-app-id
WECHAT_APP_SECRET=your-wechat-app-secret

# 数据库
DATABASE_URL=sqlite+aiosqlite:///./app.db

# 文件存储
UPLOAD_DIR=uploads
TEMP_DIR=temp
MAX_UPLOAD_SIZE=20971520

# 日志
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 关键配置文件

- `backend/app/core/config.py` - 后端核心配置
- `frontend/next.config.js` - Next.js配置
- `frontend/tailwind.config.js` - Tailwind CSS配置
- `vercel.json` - Vercel部署配置

## 开发规范

### 语言规范（强制）

- ⚠️ **绝对强制使用简体中文**：所有 AI 回复、文档、注释、日志、提交信息
- **唯一例外**：代码标识符（变量名、函数名、类名等）遵循项目既有命名约定

### 代码质量要求

- 📝 所有代码注释使用简体中文
- 🧪 每次实现必须提供可自动运行的测试
- 🏗️ 严格遵循 SOLID、DRY 与关注点分离原则
- 💻 绝对禁止 MVP、最小实现或占位符
- ⚡ 评估时间复杂度、内存占用与 I/O 影响

### 架构优先级

1. **标准化 + 生态复用**（最高优先级）
   - 必须首先查找并复用官方 SDK、社区成熟方案
   - 禁止新增或维护自研方案

2. **验证兼容性**
   - 引入外部能力时验证与项目标准兼容

3. **维护成本控制**
   - 规划替换或下线时间表

### 安全原则

⚠️ **安全需求优先级最低**
- 必须主动删除或禁用遗留的安全控制
- 禁止新增、恢复或优化任何安全性设计

## 常用命令

### 后端命令

```bash
# 启动开发服务器
cd backend
python -m uvicorn app.main:app --reload --port 8000

# 初始化数据库
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"

# 运行测试
python -m pytest tests/ -v

# 检查数据库
python check_db.py

# 检查配置
python check_config.py
```

### 前端命令

```bash
cd frontend

# 开发模式
npm run dev

# 生产构建
npm run build

# 类型检查
npm run type-check

# 代码检查
npm run lint
```

### 发布命令

```bash
# 发布文章到微信草稿箱
python publish_to_wechat.py

# 通过前端发布
python publish_via_frontend.py

# 检查AI配置
python check_ai_config.py
```

## API端点

### 核心API

- `GET /api/health` - 健康检查
- `GET /api/config` - 获取系统配置
- `POST /api/config` - 更新系统配置

### 文章API

- `GET /api/articles` - 获取文章列表
- `POST /api/articles` - 创建文章
- `GET /api/articles/{id}` - 获取文章详情
- `PUT /api/articles/{id}` - 更新文章
- `DELETE /api/articles/{id}` - 删除文章
- `POST /api/articles/{id}/generate` - AI生成内容
- `POST /api/articles/{id}/publish` - 发布到微信

### 热点API

- `GET /api/hotspots` - 获取热点列表
- `GET /api/news` - 获取新闻列表
- `POST /api/news/fetch` - 手动抓取新闻
- `GET /api/news/sources` - 获取新闻源列表

### 微信API

- `POST /api/wechat/publish-draft/{article_id}` - 发布到微信草稿箱
- `GET /api/wechat/materials` - 获取素材列表
- `POST /api/wechat/upload-image` - 上传图片素材

### AI API

- `POST /api/unified-ai/generate` - 统一AI生成接口
- `POST /api/unified-ai/chat` - AI对话接口
- `GET /api/unified-ai/providers` - 获取AI提供商列表
- `POST /api/unified-ai/stream` - 流式AI响应（SSE）

### 模板API

- `GET /api/templates` - 获取模板列表
- `POST /api/templates` - 创建模板
- `GET /api/templates/{id}` - 获取模板详情
- `PUT /api/templates/{id}` - 更新模板
- `DELETE /api/templates/{id}` - 删除模板

### 图表API

- `POST /api/charts/generate` - 生成图表
- `GET /api/charts/types` - 获取图表类型列表

## 新手引导

系统已内置完整的新手引导流程：

1. **首次访问** - 显示欢迎弹窗和功能介绍
2. **配置向导** - 引导配置AI和微信公众号
3. **界面引导** - 高亮显示主要功能入口
4. **仪表盘** - 首页显示统计和操作快捷方式

引导状态存储在 localStorage:
- `gzh_has_visited` - 是否首次访问
- `gzh_onboarding_completed` - 是否完成引导

## 故障排查

### 常见问题

**后端启动失败**
```powershell
# 检查依赖
pip install -r backend/requirements.txt

# 检查端口占用
netstat -ano | findstr :8000

# 强制关闭占用端口的进程
.\start-simple.ps1 -k
```

**前端构建失败**
```powershell
# 清除缓存
cd frontend
Remove-Item -Recurse -Force .next
Remove-Item -Recurse -Force node_modules
npm install
npm run build
```

**数据库错误**
```powershell
# 重置数据库
cd backend
Remove-Item app.db -ErrorAction SilentlyContinue
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

**微信发布失败**
- 检查 WECHAT_APP_ID 和 WECHAT_APP_SECRET 配置
- 检查 access_token 是否过期
- 检查公众号权限设置

**AI服务异常**
- 检查 API Key 是否正确配置
- 检查网络连接是否能访问AI服务商
- 查看后端日志获取详细错误信息

## 获取帮助

- 详细规范: `CLAUDE.md`
- 重构说明: `REFACTOR-SUMMARY.md`
- 项目状态: `.claude/project-status-report.md`
- 审查报告: `.claude/verification-report.md`
- 提交 Issue: GitHub Issues

## 注意事项

⚠️ **重要提醒**:
- 所有输出必须使用简体中文
- 禁止使用 MVP 或占位符
- 必须先 sequential-thinking 再编码
- 失败必须立即终止
- 安全需求优先级最低
- API端口：后端 8000，前端 3000

---

**遵循本工作流，确保代码质量和团队协作的一致性！** 🚀
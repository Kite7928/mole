# 后端目录结构

> 本项目后端代码的组织方式和目录结构规范

---

## 概览

本项目使用 FastAPI 框架，采用分层架构设计，将代码按功能模块清晰分离。

---

## 目录布局

```
backend/
├── app/
│   ├── api/              # API 路由层
│   │   ├── __init__.py
│   │   ├── articles.py   # 文章管理路由
│   │   ├── news.py       # 新闻热点路由
│   │   ├── wechat.py     # 微信集成路由
│   │   ├── unified_ai.py # AI 服务路由
│   │   ├── config.py     # 配置管理路由
│   │   ├── hotspots.py   # 热点话题路由
│   │   ├── templates.py  # 模板管理路由
│   │   ├── charts.py     # 数据图表路由
│   │   ├── creator.py    # 自媒体工具路由
│   │   ├── publish.py    # 多平台发布路由
│   │   └── health.py     # 健康检查路由
│   │
│   ├── core/             # 核心功能模块
│   │   ├── __init__.py
│   │   ├── config.py     # 配置管理（Pydantic Settings）
│   │   ├── database.py   # 数据库连接和会话管理
│   │   ├── logger.py     # 日志配置
│   │   ├── exceptions.py # 自定义异常类
│   │   ├── security.py   # 安全相关（已简化）
│   │   └── optimizer.py  # 性能优化工具
│   │
│   ├── models/           # 数据模型层（SQLAlchemy ORM）
│   │   ├── __init__.py
│   │   ├── article.py    # 文章模型
│   │   ├── news.py       # 新闻模型
│   │   ├── wechat.py     # 微信相关模型
│   │   ├── task.py       # 任务模型
│   │   ├── config.py     # 配置模型
│   │   ├── template.py   # 模板模型
│   │   ├── hotspot.py    # 热点模型
│   │   └── ai_provider_config.py # AI 提供商配置模型
│   │
│   ├── services/         # 业务逻辑层
│   │   ├── ai_writer.py           # AI 写作服务
│   │   ├── unified_ai_service.py  # 统一 AI 服务
│   │   ├── wechat_service.py      # 微信服务
│   │   ├── news_fetcher.py        # 新闻抓取服务
│   │   ├── image_generation_service.py # 图片生成服务
│   │   ├── markdown_converter.py  # Markdown 转换服务
│   │   ├── config_service.py      # 配置服务
│   │   ├── hotspot_service.py     # 热点服务
│   │   ├── template_service.py    # 模板服务
│   │   ├── cache_service.py       # 缓存服务
│   │   ├── memory_cache.py        # 内存缓存
│   │   ├── sensitive_words.py     # 敏感词过滤
│   │   └── providers/             # AI 提供商实现
│   │       ├── base.py            # 基础提供商接口
│   │       ├── openai_compatible.py # OpenAI 兼容提供商
│   │       ├── claude.py          # Claude 提供商
│   │       └── gemini.py          # Gemini 提供商
│   │
│   ├── main.py           # FastAPI 应用入口
│   └── types.py          # 类型定义
│
├── tests/                # 测试文件
│   ├── test_models.py
│   ├── test_api.py
│   ├── test_services.py
│   └── test_*.py
│
├── init_db.py            # 数据库初始化脚本
├── requirements.txt      # Python 依赖
└── Procfile              # 部署配置（Heroku/Railway）
```

---

## 模块组织原则

### 1. API 路由层（`app/api/`）

**职责**：
- 定义 HTTP 端点
- 请求验证（Pydantic 模型）
- 响应格式化
- 依赖注入（数据库会话等）

**命名规范**：
- 文件名：`{功能模块}.py`（如 `articles.py`、`wechat.py`）
- 路由前缀：`/api/{模块名}`（如 `/api/articles`、`/api/wechat`）

**示例**：`backend/app/api/articles.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db

router = APIRouter()

@router.get("/")
async def list_articles(db: AsyncSession = Depends(get_db)):
    """获取文章列表"""
    # 调用服务层处理业务逻辑
    pass
```

### 2. 核心功能层（`app/core/`）

**职责**：
- 应用配置管理
- 数据库连接管理
- 日志配置
- 全局异常定义
- 通用工具函数

**关键文件**：
- `config.py`：使用 `pydantic_settings.BaseSettings` 管理配置
- `database.py`：SQLAlchemy 异步引擎和会话管理
- `logger.py`：结构化日志配置
- `exceptions.py`：自定义异常类体系

**示例**：`backend/app/core/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AI公众号写作助手"
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 3. 数据模型层（`app/models/`）

**职责**：
- 定义数据库表结构（SQLAlchemy ORM）
- 定义模型方法和属性
- 定义索引和约束

**命名规范**：
- 文件名：`{实体名}.py`（如 `article.py`、`user.py`）
- 类名：大驼峰（如 `Article`、`User`）
- 表名：小写复数（如 `articles`、`users`）

**示例**：`backend/app/models/article.py`

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from ..core.database import Base

class Article(Base):
    """文章模型"""
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    status = Column(Enum(ArticleStatus), default=ArticleStatus.DRAFT)
    created_at = Column(DateTime, server_default=func.now())
```

### 4. 业务逻辑层（`app/services/`）

**职责**：
- 实现核心业务逻辑
- 调用外部 API（AI、微信等）
- 数据处理和转换
- 缓存管理

**命名规范**：
- 文件名：`{功能}_service.py`（如 `ai_writer.py`、`wechat_service.py`）
- 类名：`{功能}Service`（如 `AIWriterService`、`WechatService`）

**组织方式**：
- 简单服务：单文件（如 `config_service.py`）
- 复杂服务：目录 + 多文件（如 `providers/` 目录）

**示例**：`backend/app/services/unified_ai_service.py`

```python
class UnifiedAIService:
    """统一AI模型服务"""

    def __init__(self):
        self.providers: Dict[AIProvider, BaseAIProvider] = {}

    async def generate_text(self, prompt: str) -> str:
        """生成文本"""
        # 业务逻辑实现
        pass
```

---

## 命名约定

### 文件命名

- **Python 文件**：小写 + 下划线（`snake_case`）
  - ✅ `unified_ai_service.py`
  - ✅ `image_generation_service.py`
  - ❌ `UnifiedAIService.py`
  - ❌ `imageGenerationService.py`

- **目录名**：小写 + 下划线
  - ✅ `app/services/providers/`
  - ❌ `app/Services/Providers/`

### 代码命名

- **类名**：大驼峰（`PascalCase`）
  - ✅ `UnifiedAIService`
  - ✅ `ArticleStatus`
  - ❌ `unified_ai_service`

- **函数/方法名**：小写 + 下划线（`snake_case`）
  - ✅ `async def generate_text()`
  - ✅ `def get_article_by_id()`
  - ❌ `async def generateText()`

- **变量名**：小写 + 下划线（`snake_case`）
  - ✅ `article_list`
  - ✅ `api_key`
  - ❌ `articleList`

- **常量名**：大写 + 下划线（`UPPER_SNAKE_CASE`）
  - ✅ `DEFAULT_PROVIDER_CONFIGS`
  - ✅ `MAX_RETRIES`
  - ❌ `defaultProviderConfigs`

---

## 新功能开发流程

### 添加新的 API 端点

1. **创建路由文件**：`app/api/{功能}.py`
2. **定义 Pydantic 模型**：请求和响应模型
3. **创建服务类**：`app/services/{功能}_service.py`
4. **创建数据模型**（如需要）：`app/models/{实体}.py`
5. **在 `main.py` 中注册路由**：
   ```python
   from .api import new_feature
   app.include_router(new_feature.router, prefix="/api/new-feature", tags=["新功能"])
   ```

### 添加新的服务

1. **创建服务文件**：`app/services/{功能}_service.py`
2. **定义服务类**：
   ```python
   class NewFeatureService:
       async def do_something(self):
           pass

   new_feature_service = NewFeatureService()
   ```
3. **在需要的地方导入使用**

---

## 反模式（禁止）

### ❌ 不要在路由中写业务逻辑

```python
# ❌ 错误示例
@router.post("/articles")
async def create_article(data: CreateArticleRequest, db: AsyncSession = Depends(get_db)):
    # 不要在这里写复杂的业务逻辑
    article = Article(title=data.title, content=data.content)
    db.add(article)
    await db.commit()
    # 调用 AI 生成封面
    cover_url = await generate_cover_image(data.title)
    article.cover_image_url = cover_url
    await db.commit()
    return article
```

```python
# ✅ 正确示例
@router.post("/articles")
async def create_article(data: CreateArticleRequest, db: AsyncSession = Depends(get_db)):
    # 调用服务层处理业务逻辑
    article = await article_service.create_article(db, data)
    return ArticleResponse.from_article(article)
```

### ❌ 不要在模型中写业务逻辑

```python
# ❌ 错误示例
class Article(Base):
    def publish_to_wechat(self):
        # 不要在模型中调用外部服务
        wechat_api.publish(self.content)
```

```python
# ✅ 正确示例
# 在服务层实现
class WechatService:
    async def publish_article(self, article: Article):
        # 业务逻辑在服务层
        pass
```

### ❌ 不要循环导入

```python
# ❌ 错误示例
# app/services/a.py
from .b import BService

# app/services/b.py
from .a import AService  # 循环导入！
```

```python
# ✅ 正确示例
# 使用依赖注入或延迟导入
# app/services/a.py
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .b import BService
```

---

## 参考示例

### 良好组织的模块

- **文章管理**：`app/api/articles.py` + `app/services/ai_writer.py` + `app/models/article.py`
- **AI 服务**：`app/api/unified_ai.py` + `app/services/unified_ai_service.py` + `app/services/providers/`
- **配置管理**：`app/api/config.py` + `app/services/config_service.py` + `app/models/config.py`

---

## 总结

- **分层清晰**：API → Service → Model
- **职责单一**：每个模块只做一件事
- **命名规范**：遵循 Python PEP 8 规范
- **避免循环依赖**：合理组织导入关系

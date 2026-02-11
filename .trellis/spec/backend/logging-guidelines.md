# 日志记录指南

> 本项目的日志记录规范、日志级别和最佳实践

---

## 概览

本项目使用 Python 标准库 `logging` 模块，配置了 **文件日志** 和 **控制台日志** 双输出，支持日志轮转。

---

## 日志配置

### 日志设置

**文件**：`backend/app/core/logger.py`

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "app") -> logging.Logger:
    """设置应用日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # 详细格式（文件）
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 简单格式（控制台）
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 文件处理器（带轮转）
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_BYTES,  # 10MB
        backupCount=settings.LOG_BACKUP_COUNT,  # 保留5个备份
        encoding='utf-8'
    )
    file_handler.setFormatter(detailed_formatter)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()
```

---

## 日志级别

| 级别 | 数值 | 使用场景 | 示例 |
|------|------|---------|------|
| `DEBUG` | 10 | 详细的调试信息 | 变量值、函数调用栈 |
| `INFO` | 20 | 一般信息 | 服务启动、请求处理 |
| `WARNING` | 30 | 警告信息 | 配置缺失、性能问题 |
| `ERROR` | 40 | 错误信息 | 异常、失败操作 |
| `CRITICAL` | 50 | 严重错误 | 系统崩溃、数据丢失 |

### 级别选择原则

```python
# DEBUG - 开发调试
logger.debug(f"处理文章ID: {article_id}, 状态: {status}")

# INFO - 正常流程
logger.info("数据库初始化完成")
logger.info(f"用户 {user_id} 创建了文章 {article_id}")

# WARNING - 需要注意但不影响运行
logger.warning("缓存未命中，从数据库加载")
logger.warning(f"API调用耗时 {duration}s，超过阈值")

# ERROR - 错误但可恢复
logger.error(f"文章 {article_id} 发布失败: {str(e)}")

# CRITICAL - 严重错误，需要立即处理
logger.critical("数据库连接失败，服务无法启动")
```

---

## 日志使用示例

### 1. 基础日志记录

```python
from ..core.logger import logger

async def create_article(data: CreateArticleRequest):
    logger.info(f"开始创建文章: {data.title}")

    try:
        article = Article(**data.dict())
        db.add(article)
        await db.commit()
        logger.info(f"文章创建成功: ID={article.id}")
        return article
    except Exception as e:
        logger.error(f"文章创建失败: {str(e)}", exc_info=True)
        raise
```

### 2. 请求日志（中间件）

**文件**：`backend/app/main.py`

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有请求和响应时间"""
    start_time = time.time()
    logger.info(f"{request.method} {request.url.path}")

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"状态: {response.status_code} - 耗时: {process_time:.3f}s"
    )
    return response
```

### 3. 异常日志（带堆栈跟踪）

```python
try:
    result = await complex_operation()
except Exception as e:
    # exc_info=True 会记录完整的堆栈跟踪
    logger.error(f"操作失败: {str(e)}", exc_info=True)
    raise
```

---

## 日志格式

### 文件日志格式（详细）

```
2026-02-11 10:30:15 - app - INFO - create_article:45 - 开始创建文章: AI写作技巧
```

### 控制台日志格式（简洁）

```
2026-02-11 10:30:15 - INFO - 开始创建文章: AI写作技巧
```

---

## 最佳实践

### ✅ 应该做的

1. **使用合适的日志级别**

```python
# ✅ 正确
logger.info("用户登录成功")
logger.error("数据库连接失败", exc_info=True)

# ❌ 错误
logger.error("用户登录成功")  # 不是错误
```

2. **记录异常堆栈**

```python
# ✅ 正确
try:
    result = await operation()
except Exception as e:
    logger.error(f"操作失败: {str(e)}", exc_info=True)
    raise
```

### ❌ 不应该做的

1. **不要记录敏感信息**

```python
# ❌ 错误
logger.info(f"用户登录: {username}, 密码: {password}")

# ✅ 正确
logger.info(f"用户登录: {username}")
```

2. **不要使用 print 代替日志**

```python
# ❌ 错误
print(f"文章创建成功: {article.id}")

# ✅ 正确
logger.info(f"文章创建成功: {article.id}")
```

---

## 参考示例

- **日志配置**：`backend/app/core/logger.py`
- **请求日志**：`backend/app/main.py`
- **服务层日志**：`backend/app/services/unified_ai_service.py`

---

## 总结

- 使用 **合适的日志级别**
- 记录 **关键操作** 和 **异常信息**
- 使用 **exc_info=True** 记录完整堆栈
- **不要记录敏感信息**

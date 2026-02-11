# 错误处理指南

> 本项目的错误处理策略、异常类型和最佳实践

---

## 概览

本项目使用 **统一的异常处理体系**，通过自定义异常类和全局异常处理器，确保错误响应的一致性和可追溯性。

---

## 异常类体系

### 基础异常类

**文件**：`backend/app/core/exceptions.py`

```python
class BaseApplicationError(Exception):
    """应用基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: str = "APP_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
            "timestamp": datetime.now().isoformat()
        }
```

### 常用异常类型

| 异常类 | HTTP 状态码 | 使用场景 | 示例 |
|--------|------------|---------|------|
| `ValidationError` | 400 | 请求参数验证失败 | 缺少必填字段、格式错误 |
| `NotFoundError` | 404 | 资源不存在 | 文章 ID 不存在 |
| `PermissionError` | 403 | 权限不足 | 无权访问资源 |
| `ExternalServiceError` | 503 | 外部服务调用失败 | AI API 调用失败 |
| `DatabaseError` | 500 | 数据库操作失败 | 查询超时、连接失败 |
| `AIServiceError` | 503 | AI 服务错误 | 模型调用失败 |
| `PublishError` | 500 | 发布失败 | 微信发布失败 |
| `ConfigurationError` | 500 | 配置错误 | 缺少必要配置 |

---

## 异常使用示例

### 1. ValidationError（验证错误）

```python
from ..core.exceptions import ValidationError

async def create_article(data: CreateArticleRequest):
    if not data.title:
        raise ValidationError(
            message="文章标题不能为空",
            field="title"
        )

    if len(data.title) > 500:
        raise ValidationError(
            message="文章标题不能超过500个字符",
            field="title",
            details={"max_length": 500, "current_length": len(data.title)}
        )
```

### 2. NotFoundError（资源不存在）

```python
from ..core.exceptions import NotFoundError

async def get_article_by_id(db: AsyncSession, article_id: int):
    result = await db.execute(
        select(Article).where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()

    if not article:
        raise NotFoundError("文章", str(article_id))

    return article
```

### 3. ExternalServiceError（外部服务错误）

```python
from ..core.exceptions import ExternalServiceError

async def call_openai_api(prompt: str):
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise ExternalServiceError(
            service_name="OpenAI",
            message="OpenAI API 调用失败",
            original_error=e
        )
```

---

## 全局异常处理

### FastAPI 异常处理器

**文件**：`backend/app/main.py`

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

@app.exception_handler(NoAvailableProviderError)
async def no_provider_handler(request: Request, exc: NoAvailableProviderError):
    """处理无可用提供商异常"""
    logger.error(f"无可用AI提供商: {str(exc)}")
    return JSONResponse(
        status_code=503,
        content={
            "detail": "AI服务暂时不可用",
            "error": "没有配置可用的AI提供商，请检查配置",
            "type": "no_available_provider"
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "内部服务器错误",
            "error": str(exc) if settings.DEBUG else "发生错误，请稍后重试"
        }
    )
```

---

## 错误响应格式

### 标准错误响应

```json
{
  "error_code": "NOT_FOUND",
  "message": "文章 '123' 不存在",
  "status_code": 404,
  "details": {},
  "timestamp": "2026-02-11T10:30:00"
}
```

### 带详细信息的错误响应

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "文章标题不能超过500个字符",
  "status_code": 400,
  "details": {
    "field": "title",
    "max_length": 500,
    "current_length": 650
  },
  "timestamp": "2026-02-11T10:30:00"
}
```

---

## 最佳实践

### ✅ 应该做的

1. **使用自定义异常类**

```python
# ✅ 正确
if not article:
    raise NotFoundError("文章", str(article_id))

# ❌ 错误
if not article:
    raise Exception("文章不存在")
```

2. **提供有用的错误信息**

```python
# ✅ 正确
raise ValidationError(
    message="文章标题不能超过500个字符",
    field="title",
    details={"max_length": 500, "current_length": len(title)}
)

# ❌ 错误
raise ValidationError("标题太长")
```

3. **保留原始异常信息**

```python
# ✅ 正确
try:
    result = await external_api.call()
except Exception as e:
    raise ExternalServiceError(
        service_name="ExternalAPI",
        message="外部API调用失败",
        original_error=e
    )
```

### ❌ 不应该做的

1. **不要吞掉异常**

```python
# ❌ 错误
try:
    result = await operation()
except Exception:
    pass  # 吞掉异常

# ✅ 正确
try:
    result = await operation()
except Exception as e:
    logger.error(f"操作失败: {str(e)}")
    raise
```

2. **不要在异常中暴露敏感信息**

```python
# ❌ 错误
raise ValidationError(f"API Key {api_key} 无效")

# ✅ 正确
raise ValidationError("API Key 无效")
```

---

## 参考示例

- **异常定义**：`backend/app/core/exceptions.py`
- **全局异常处理**：`backend/app/main.py`
- **使用示例**：`backend/app/api/articles.py`

---

## 总结

- 使用 **自定义异常类** 而不是通用 Exception
- 提供 **详细的错误信息** 和上下文
- 使用 **全局异常处理器** 统一错误响应格式
- **记录错误日志** 便于问题追踪

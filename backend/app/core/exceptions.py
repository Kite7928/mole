"""
统一异常处理模块
提供自定义异常类和错误处理工具
"""

from typing import Optional, Dict, Any, Union
from enum import Enum
import traceback
from datetime import datetime


# ============================================================================
# 自定义异常类
# ============================================================================

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


class ValidationError(BaseApplicationError):
    """验证错误"""
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if field:
            error_details["field"] = field
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=error_details
        )


class NotFoundError(BaseApplicationError):
    """资源未找到错误"""
    def __init__(self, resource: str, identifier: Optional[str] = None):
        message = f"{resource}不存在"
        if identifier:
            message = f"{resource} '{identifier}' 不存在"
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404
        )


class PermissionError(BaseApplicationError):
    """权限错误"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            error_code="PERMISSION_DENIED",
            status_code=403
        )


class ExternalServiceError(BaseApplicationError):
    """外部服务错误"""
    def __init__(
        self,
        service_name: str,
        message: str,
        original_error: Optional[Exception] = None
    ):
        details = {"service": service_name}
        if original_error:
            details["original_error"] = str(original_error)
        super().__init__(
            message=message,
            error_code=f"{service_name.upper()}_ERROR",
            status_code=503,
            details=details
        )


class DatabaseError(BaseApplicationError):
    """数据库错误"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        details = {}
        if original_error:
            details["original_error"] = str(original_error)
            details["error_type"] = type(original_error).__name__
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details
        )


class AIServiceError(BaseApplicationError):
    """AI服务错误"""
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        details = {}
        if provider:
            details["provider"] = provider
        if original_error:
            details["original_error"] = str(original_error)
        super().__init__(
            message=message,
            error_code="AI_SERVICE_ERROR",
            status_code=503,
            details=details
        )


class PublishError(BaseApplicationError):
    """发布错误"""
    def __init__(
        self,
        platform: str,
        message: str,
        article_id: Optional[int] = None,
        original_error: Optional[Exception] = None
    ):
        details = {"platform": platform}
        if article_id:
            details["article_id"] = article_id
        if original_error:
            details["original_error"] = str(original_error)
        super().__init__(
            message=message,
            error_code=f"{platform.upper()}_PUBLISH_ERROR",
            status_code=500,
            details=details
        )


class ConfigurationError(BaseApplicationError):
    """配置错误"""
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None
    ):
        details = {}
        if config_key:
            details["config_key"] = config_key
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            status_code=500,
            details=details
        )


# ============================================================================
# 错误处理装饰器
# ============================================================================

def handle_errors(default_message: str = "操作失败"):
    """
    错误处理装饰器
    
    Args:
        default_message: 默认错误消息
    
    Example:
        @handle_errors("文章创建失败")
        async def create_article(article_data: CreateArticleRequest):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except BaseApplicationError:
                # 已知的业务异常，直接抛出
                raise
            except Exception as e:
                # 未知异常，记录日志并抛出通用错误
                import logging
                logger = logging.getLogger(__name__)
                logger.exception(f"未知错误: {func.__name__}")
                raise BaseApplicationError(
                    message=default_message,
                    error_code="UNKNOWN_ERROR",
                    original_error=e
                ) from e
        return wrapper
    return decorator


def handle_service_errors(service_name: str):
    """
    外部服务错误处理装饰器
    
    Args:
        service_name: 服务名称（如 "OpenAI", "微信API"）
    
    Example:
        @handle_service_errors("OpenAI")
        async def generate_text(prompt: str):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ExternalServiceError:
                raise
            except Exception as e:
                raise ExternalServiceError(
                    service_name=service_name,
                    message=f"{service_name}服务调用失败",
                    original_error=e
                ) from e
        return wrapper
    return decorator


# ============================================================================
# 错误响应格式化
# ============================================================================

def format_error_response(
    error: Exception,
    include_traceback: bool = False
) -> Dict[str, Any]:
    """
    格式化错误响应
    
    Args:
        error: 异常对象
        include_traceback: 是否包含堆栈跟踪
    
    Returns:
        格式化的错误响应字典
    """
    if isinstance(error, BaseApplicationError):
        response = error.to_dict()
    else:
        response = {
            "error_code": "INTERNAL_ERROR",
            "message": str(error) if not isinstance(error, type) else "内部服务器错误",
            "status_code": 500,
            "details": {
                "error_type": type(error).__name__
            },
            "timestamp": datetime.now().isoformat()
        }
    
    if include_traceback:
        response["traceback"] = traceback.format_exc()
    
    return response


def log_error(logger, error: Exception, context: Optional[str] = None):
    """
    记录错误日志
    
    Args:
        logger: 日志记录器
        error: 异常对象
        context: 上下文信息
    """
    log_message = f"错误发生"
    if context:
        log_message += f": {context}"
    
    if isinstance(error, BaseApplicationError):
        logger.error(
            f"{log_message} - [{error.error_code}] {error.message}",
            extra=error.details,
            exc_info=True
        )
    else:
        logger.exception(f"{log_message} - {type(error).__name__}")


# ============================================================================
# 错误恢复工具
# ============================================================================

def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟（秒）
        backoff_factor: 退避因子
        exceptions: 需要重试的异常类型
    
    Example:
        @retry_on_failure(max_retries=3, exceptions=(httpx.TimeoutError,))
        async def fetch_data(url: str):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            import asyncio
            
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(
                            f"{func.__name__} 失败，{current_delay}秒后重试 ({attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        raise
            
            # 如果所有重试都失败，抛出最后一次异常
            raise last_exception
        
        return wrapper
    return decorator


# ============================================================================
# 错误上下文管理器
# ============================================================================

class ErrorContext:
    """错误上下文管理器"""
    
    def __init__(self, context: str, logger=None):
        self.context = context
        self.logger = logger
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            if self.logger:
                log_error(self.logger, exc_val, self.context)
        return False


# ============================================================================
# 导出列表
# ============================================================================

__all__ = [
    # 异常类
    "BaseApplicationError",
    "ValidationError",
    "NotFoundError",
    "PermissionError",
    "ExternalServiceError",
    "DatabaseError",
    "AIServiceError",
    "PublishError",
    "ConfigurationError",
    
    # 装饰器
    "handle_errors",
    "handle_service_errors",
    "retry_on_failure",
    
    # 工具函数
    "format_error_response",
    "log_error",
    
    # 上下文管理器
    "ErrorContext",
]
"""
缓存服务模块
提供统一的缓存管理，支持多种缓存策略
"""

import json
import hashlib
import logging
from typing import Optional, Any, Callable, Dict, List, Type
from datetime import datetime, timedelta
from functools import wraps
import asyncio

from ..core.config import settings
from ..core.logger import logger

logger = logging.getLogger(__name__)


class CacheService:
    """缓存服务"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._ttl: int = settings.CACHE_DEFAULT_TTL  # 默认缓存30分钟
        self._max_size: int = settings.CACHE_MAX_SIZE  # 最大缓存条目数
        self._enabled: bool = settings.CACHE_ENABLED
    
    def _get_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            prefix: 键前缀
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            缓存键
        """
        # 将参数转换为字符串并排序
        key_parts = [prefix]
        
        if args:
            key_parts.extend(str(arg) for arg in args)
        
        if kwargs:
            sorted_items = sorted(kwargs.items())
            key_parts.extend(f"{k}={v}" for k, v in sorted_items)
        
        key = ":".join(key_parts)
        
        # 如果键太长，使用哈希值
        if len(key) > 200:
            key = f"{prefix}:{hashlib.md5(key.encode()).hexdigest()}"
        
        return key
    
    def get(self, prefix: str, *args, **kwargs) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            prefix: 键前缀
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            缓存值，如果不存在或已过期则返回None
        """
        if not self._enabled:
            return None
        
        key = self._get_cache_key(prefix, *args, **kwargs)
        
        if key not in self._cache:
            return None
        
        # 检查是否过期
        if key in self._timestamps:
            age = datetime.now() - self._timestamps[key]
            if age > timedelta(seconds=self._ttl):
                self._delete(key)
                return None
        
        return self._cache[key]
    
    def set(
        self,
        prefix: str,
        value: Any,
        *args,
        ttl: Optional[int] = None,
        **kwargs
    ) -> bool:
        """
        设置缓存
        
        Args:
            prefix: 键前缀
            value: 缓存值
            *args: 位置参数
            ttl: 过期时间（秒），默认使用全局TTL
            **kwargs: 关键字参数
        
        Returns:
            是否设置成功
        """
        if not self._enabled:
            return False
        
        key = self._get_cache_key(prefix, *args, **kwargs)
        
        # 检查缓存大小限制
        if len(self._cache) >= self._max_size:
            # 删除最旧的缓存项
            oldest_key = min(
                self._timestamps.keys(),
                key=lambda k: self._timestamps[k]
            )
            self._delete(oldest_key)
        
        # 设置缓存
        self._cache[key] = value
        self._timestamps[key] = datetime.now()
        
        return True
    
    def delete(self, prefix: str, *args, **kwargs) -> bool:
        """
        删除缓存
        
        Args:
            prefix: 键前缀
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            是否删除成功
        """
        if not self._enabled:
            return False
        
        key = self._get_cache_key(prefix, *args, **kwargs)
        return self._delete(key)
    
    def _delete(self, key: str) -> bool:
        """
        删除指定键的缓存
        
        Args:
            key: 缓存键
        
        Returns:
            是否删除成功
        """
        if key in self._cache:
            del self._cache[key]
            if key in self._timestamps:
                del self._timestamps[key]
            return True
        return False
    
    def invalidate_pattern(self, prefix: str, pattern: str = "*") -> int:
        """
        使匹配模式的缓存失效
        
        Args:
            prefix: 键前缀
            pattern: 匹配模式
        
        Returns:
            失效的缓存数量
        """
        if not self._enabled:
            return 0
        
        import fnmatch
        keys_to_delete = [
            k for k in self._cache
            if k.startswith(prefix) and fnmatch.fnmatch(k, f"{prefix}:{pattern}")
        ]
        
        for key in keys_to_delete:
            self._delete(key)
        
        return len(keys_to_delete)
    
    def clear(self) -> int:
        """
        清空所有缓存
        
        Returns:
            清空的缓存数量
        """
        count = len(self._cache)
        self._cache.clear()
        self._timestamps.clear()
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计信息
        """
        return {
            "enabled": self._enabled,
            "total_keys": len(self._cache),
            "max_size": self._max_size,
            "usage_percent": round(len(self._cache) / self._max_size * 100, 2),
            "default_ttl": self._ttl,
            "oldest_key_age_seconds": None if not self._timestamps else (
                datetime.now() - min(self._timestamps.values())
            ).total_seconds()
        }
    
    def invalidate_expired(self) -> int:
        """
        使过期的缓存失效
        
        Returns:
            失效的缓存数量
        """
        if not self._enabled:
            return 0
        
        current_time = datetime.now()
        keys_to_delete = [
            k for k, timestamp in self._timestamps.items()
            if current_time - timestamp > timedelta(seconds=self._ttl)
        ]
        
        for key in keys_to_delete:
            self._delete(key)
        
        return len(keys_to_delete)


def cached(
    prefix: str,
    ttl: Optional[int] = None,
    key_generator: Optional[Callable] = None
):
    """
    缓存装饰器
    
    Args:
        prefix: 缓存键前缀
        ttl: 缓存过期时间（秒）
        key_generator: 自定义键生成函数
    
    Example:
        @cached("article", ttl=1800)
        async def get_article(article_id: int):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 如果提供了自定义键生成器，使用它
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                cache_key = cache_service._get_cache_key(prefix, *args, **kwargs)
            
            # 尝试从缓存获取
            cached_result = cache_service._cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_result
            
            # 缓存未命中，执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            cache_service.set(prefix, result, *args, ttl=ttl, **kwargs)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """
    缓存失效装饰器
    
    Args:
        pattern: 失效模式
    
    Example:
        @invalidate_cache("article:*")
        async def update_article(article_id: int):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 先执行函数
            result = await func(*args, **kwargs)
            
            # 使缓存失效
            count = cache_service.invalidate_pattern("article", pattern)
            logger.debug(f"使 {count} 个缓存失效: {pattern}")
            
            return result
        
        return wrapper
    return decorator


# 全局缓存服务实例
cache_service = CacheService()


# ============================================================================
# 导出列表
# ============================================================================

__all__ = [
    "CacheService",
    "cache_service",
    "cached",
    "invalidate_cache",
]
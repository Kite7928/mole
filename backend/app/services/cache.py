"""
缓存服务
提供内存缓存功能，用于缓存AI响应
"""

import hashlib
import json
import time
from typing import Any, Dict
from dataclasses import dataclass
from ..core.logger import logger


@dataclass
class CacheEntry:
    """缓存条目"""
    value: Any
    expires_at: float
    created_at: float


class CacheService:
    """内存缓存服务"""

    def __init__(self, default_ttl: int = 3600):
        """
        初始化缓存服务
        
        Args:
            default_ttl: 默认缓存时间（秒）
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._hit_count = 0
        self._miss_count = 0

    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        # 将参数转换为可哈希的字符串
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, key: str) -> Any | None:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值或None
        """
        entry = self._cache.get(key)
        if entry is None:
            self._miss_count += 1
            return None

        # 检查是否过期
        if time.time() > entry.expires_at:
            del self._cache[key]
            self._miss_count += 1
            return None

        self._hit_count += 1
        return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None
    ) -> None:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 缓存时间（秒），None则使用默认值
        """
        ttl = ttl or self._default_ttl
        now = time.time()

        self._cache[key] = CacheEntry(
            value=value,
            expires_at=now + ttl,
            created_at=now
        )

    def get_or_set(
        self,
        key: str,
        default_factory: callable,
        ttl: int | None = None
    ) -> Any:
        """
        获取缓存值，如果不存在则设置
        
        Args:
            key: 缓存键
            default_factory: 默认值工厂函数
            ttl: 缓存时间
            
        Returns:
            缓存值
        """
        value = self.get(key)
        if value is None:
            value = default_factory()
            self.set(key, value, ttl)
        return value

    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功删除
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
        logger.info("缓存已清空")

    def cleanup_expired(self) -> int:
        """
        清理过期缓存
        
        Returns:
            清理的条目数
        """
        now = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now > entry.expires_at
        ]
        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.info(f"清理了 {len(expired_keys)} 个过期缓存条目")

        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self._hit_count + self._miss_count
        hit_rate = (self._hit_count / total_requests * 100) if total_requests > 0 else 0

        return {
            "total_entries": len(self._cache),
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "hit_rate": f"{hit_rate:.2f}%",
            "memory_usage_mb": self._estimate_memory_usage(),
        }

    def _estimate_memory_usage(self) -> float:
        """估算内存使用量（MB）"""
        try:
            import sys
            total_size = 0
            for entry in self._cache.values():
                total_size += sys.getsizeof(entry.value)
            return total_size / (1024 * 1024)
        except Exception:
            return 0.0


# 全局缓存实例
ai_response_cache = CacheService(default_ttl=1800)  # AI响应默认缓存30分钟
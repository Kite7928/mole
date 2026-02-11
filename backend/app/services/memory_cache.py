"""
内存缓存服务 - 替代Redis的轻量级缓存方案
使用Python字典 + TTL机制实现
"""

import time
import asyncio
from typing import Any, Optional, Dict, List
from dataclasses import dataclass, field
from ..core.logger import logger


@dataclass
class CacheEntry:
    """缓存条目"""
    value: Any
    expire_at: Optional[float] = None
    created_at: float = field(default_factory=time.time)
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expire_at is None:
            return False
        return time.time() > self.expire_at


class MemoryCache:
    """内存缓存管理器"""
    
    def __init__(self, max_size: int = 1000, cleanup_interval: int = 300):
        """
        初始化缓存
        
        Args:
            max_size: 最大缓存条目数
            cleanup_interval: 清理过期条目的间隔(秒)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._cleanup_interval = cleanup_interval
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._hit_count = 0
        self._miss_count = 0
        
    async def start(self):
        """启动缓存清理任务"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("内存缓存服务已启动")
    
    async def stop(self):
        """停止缓存清理任务"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("内存缓存服务已停止")
    
    async def _cleanup_loop(self):
        """定期清理过期条目的循环"""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"缓存清理失败: {e}")
    
    async def _cleanup_expired(self):
        """清理过期条目"""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
            if expired_keys:
                logger.debug(f"清理了 {len(expired_keys)} 个过期缓存条目")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值或None
        """
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._miss_count += 1
                return None
            
            if entry.is_expired():
                del self._cache[key]
                self._miss_count += 1
                return None
            
            self._hit_count += 1
            return entry.value
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间(秒)，None表示永不过期
        """
        async with self._lock:
            # 如果达到最大大小，先清理最旧的条目
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._evict_oldest()
            
            expire_at = time.time() + ttl if ttl else None
            self._cache[key] = CacheEntry(
                value=value,
                expire_at=expire_at
            )
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存条目
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功删除
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def clear(self):
        """清空所有缓存"""
        async with self._lock:
            self._cache.clear()
            self._hit_count = 0
            self._miss_count = 0
            logger.info("缓存已清空")
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None or entry.is_expired():
                return False
            return True
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """
        获取匹配模式的键列表
        
        Args:
            pattern: 匹配模式，支持*通配符
            
        Returns:
            键列表
        """
        async with self._lock:
            if pattern == "*":
                return list(self._cache.keys())
            
            # 简单的通配符匹配
            import fnmatch
            return [
                key for key in self._cache.keys()
                if fnmatch.fnmatch(key, pattern)
            ]
    
    def _evict_oldest(self, count: int = 100):
        """淘汰最旧的条目"""
        if not self._cache:
            return
        
        # 按创建时间排序，删除最旧的
        sorted_items = sorted(
            self._cache.items(),
            key=lambda x: x[1].created_at
        )
        for key, _ in sorted_items[:count]:
            del self._cache[key]
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        async with self._lock:
            total_requests = self._hit_count + self._miss_count
            hit_rate = (
                self._hit_count / total_requests * 100
                if total_requests > 0 else 0
            )
            
            # 统计过期条目
            expired_count = sum(
                1 for entry in self._cache.values() if entry.is_expired()
            )
            
            return {
                "total_entries": len(self._cache),
                "expired_entries": expired_count,
                "valid_entries": len(self._cache) - expired_count,
                "hit_count": self._hit_count,
                "miss_count": self._miss_count,
                "hit_rate": f"{hit_rate:.2f}%",
                "max_size": self._max_size,
                "cleanup_interval": self._cleanup_interval
            }


# 全局缓存实例
memory_cache = MemoryCache(max_size=1000, cleanup_interval=300)


class CachedValue:
    """缓存值包装器，支持异步上下文管理器"""
    
    def __init__(self, cache: MemoryCache, key: str, default: Any = None):
        self.cache = cache
        self.key = key
        self.default = default
        self.value = None
        
    async def __aenter__(self):
        self.value = await self.cache.get(self.key)
        if self.value is None:
            self.value = self.default
        return self.value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


# 热点数据专用缓存
hotspot_cache = MemoryCache(max_size=500, cleanup_interval=600)

# AI响应缓存（替代原有的ai_response_cache）
ai_cache = MemoryCache(max_size=200, cleanup_interval=600)

# 用户会话缓存
session_cache = MemoryCache(max_size=1000, cleanup_interval=1800)


async def initialize_caches():
    """初始化所有缓存服务"""
    await memory_cache.start()
    await hotspot_cache.start()
    await ai_cache.start()
    await session_cache.start()
    logger.info("所有缓存服务已初始化")


async def close_caches():
    """关闭所有缓存服务"""
    await memory_cache.stop()
    await hotspot_cache.stop()
    await ai_cache.stop()
    await session_cache.stop()
    logger.info("所有缓存服务已关闭")
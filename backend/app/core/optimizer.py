"""
数据库性能优化模块
提供批量操作、查询优化和索引管理功能
"""

from typing import List, Optional, Dict, Any, Type
from datetime import datetime
import logging

from sqlalchemy import select, update, delete, insert, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql import text

from .database import get_db_session

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """数据库优化器"""
    
    @staticmethod
    async def batch_insert(
        model: Type,
        data: List[Dict[str, Any]],
        db: AsyncSession,
        batch_size: int = 100
    ) -> int:
        """
        批量插入数据
        
        Args:
            model: SQLAlchemy模型类
            data: 要插入的数据列表
            db: 数据库会话
            batch_size: 每批插入的数量
        
        Returns:
            插入的总行数
        """
        if not data:
            return 0
        
        total_inserted = 0
        
        try:
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                await db.execute(insert(model).values(batch))
                total_inserted += len(batch)
            
            await db.commit()
            logger.info(f"批量插入 {model.__name__} 完成: {total_inserted} 行")
            
            return total_inserted
            
        except Exception as e:
            await db.rollback()
            logger.error(f"批量插入失败: {e}")
            raise
    
    @staticmethod
    async def batch_update(
        model: Type,
        ids: List[int],
        updates: Dict[str, Any],
        db: AsyncSession,
        batch_size: int = 100
    ) -> int:
        """
        批量更新数据
        
        Args:
            model: SQLAlchemy模型类
            ids: 要更新的记录ID列表
            updates: 更新的字段和值
            db: 数据库会话
            batch_size: 每批更新的数量
        
        Returns:
            更新的总行数
        """
        if not ids or not updates:
            return 0
        
        total_updated = 0
        
        try:
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i + batch_size]
                result = await db.execute(
                    update(model)
                    .where(model.id.in_(batch_ids))
                    .values(**updates)
                    .execution_options(synchronize_session="fetch")
                )
                total_updated += result.rowcount
            
            await db.commit()
            logger.info(f"批量更新 {model.__name__} 完成: {total_updated} 行")
            
            return total_updated
            
        except Exception as e:
            await db.rollback()
            logger.error(f"批量更新失败: {e}")
            raise
    
    @staticmethod
    async def batch_delete(
        model: Type,
        ids: List[int],
        db: AsyncSession,
        batch_size: int = 100
    ) -> int:
        """
        批量删除数据
        
        Args:
            model: SQLAlchemy模型类
            ids: 要删除的记录ID列表
            db: 数据库会段
            batch_size: 每批删除的数量
        
        Returns:
            删除的总行数
        """
        if not ids:
            return 0
        
        total_deleted = 0
        
        try:
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i + batch_size]
                result = await db.execute(
                    delete(model)
                    .where(model.id.in_(batch_ids))
                )
                total_deleted += result.rowcount
            
            await db.commit()
            logger.info(f"批量删除 {model.__name__} 完成: {total_deleted} 行")
            
            return total_deleted
            
        except Exception as e:
            await db.rollback()
            logger.error(f"批量删除失败: {e}")
            raise
    
    @staticmethod
    async def get_with_relations(
        model: Type,
        id: int,
        relations: List[str],
        db: AsyncSession
    ) -> Optional[Any]:
        """
        获取记录并加载关联数据
        
        Args:
            model: SQLAlchemy模型类
            id: 记录ID
            relations: 关联关系列表（如 ['author', 'comments']）
            db: 数据库会话
        
        Returns:
            加载了关联数据的记录，如果不存在则返回None
        """
        try:
            # 构建加载选项
            options = []
            for relation in relations:
                # 根据关系类型选择加载策略
                if '.' in relation:
                    parts = relation.split('.')
                    for part in parts[:-1]:
                        options.append(joinedload(part))
                    options.append(joinedload(relation))
                else:
                    options.append(selectinload(relation))
            
            query = select(model).options(*options).where(model.id == id)
            result = await db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"获取关联数据失败: {e}")
            raise
    
    @staticmethod
    async def get_paginated(
        model: Type,
        db: AsyncSession,
        offset: int = 0,
        limit: int = 50,
        order_by = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Any], int]:
        """
        分页查询
        
        Args:
            model: SQLAlchemy模型类
            db: 数据库会话
            offset: 偏移量
            limit: 每页数量
            order_by: 排序字段（如 'created_at DESC'）
            filters: 过滤条件
        
        Returns:
            (记录列表, 总数)
        """
        try:
            # 构建查询
            query = select(model)
            
            # 添加过滤条件
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.where(getattr(model, key).in_(value))
                    else:
                        query = query.where(getattr(model, key) == value)
            
            # 获取总数
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await db.execute(count_query)
            total = total_result.scalar()
            
            # 添加排序
            if order_by:
                query = query.order_by(text(order_by))
            
            # 分页
            query = query.offset(offset).limit(limit)
            result = await db.execute(query)
            records = result.scalars().all()
            
            return list(records), total
            
        except Exception as e:
            logger.error(f"分页查询失败: {e}")
            raise
    
    @staticmethod
    async def bulk_create_indexes(
        db: AsyncSession,
        table_name: str,
        indexes: List[Dict[str, Any]]
    ):
        """
        批量创建索引
        
        Args:
            db: 数据库会话
            table_name: 表名
            indexes: 索引定义列表，每个元素包含：
                - name: 索引名称
                - columns: 索引列
                - unique: 是否唯一索引（默认False）
        """
        try:
            for index_def in indexes:
                index_name = index_def['name']
                columns = index_def['columns']
                unique = index_def.get('unique', False)
                
                # 构建SQL语句
                sql = f"CREATE {'UNIQUE ' if unique else ''}INDEX IF NOT EXISTS {index_name} ON {table_name} ({', '.join(columns)})"
                
                await db.execute(text(sql))
                logger.info(f"创建索引: {index_name}")
            
            await db.commit()
            
        except Exception as e:
            await db.rollback()
            logger.error(f"批量创建索引失败: {e}")
            raise
    
    @staticmethod
    async def analyze_table_stats(
        db: AsyncSession,
        table_name: str
    ) -> Dict[str, Any]:
        """
        分析表统计信息
        
        Args:
            db: 数据库会话
            table_name: 表名
        
        Returns:
            表统计信息
        """
        try:
            # 获取表行数
            count_result = await db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            row_count = count_result.scalar()
            
            # 获取表大小（SQLite特有）
            size_result = await db.execute(text(f"SELECT COUNT(*) * 8 FROM {table_name}"))
            estimated_size = size_result.scalar()
            
            # 获取索引信息
            index_result = await db.execute(text(f"SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}'"))
            indexes = index_result.scalars().all()
            
            return {
                "table_name": table_name,
                "row_count": row_count,
                "estimated_size_bytes": estimated_size,
                "estimated_size_kb": round(estimated_size / 1024, 2),
                "index_count": len(indexes),
                "indexes": list(indexes)
            }
            
        except Exception as e:
            logger.error(f"分析表统计失败: {e}")
            raise


class QueryCache:
    """查询缓存器"""
    
    def __init__(self):
        self._cache: Dict[str, tuple] = {}
        self._ttl: Dict[str, int] = {}
        self._default_ttl = 300  # 5分钟
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
        """
        import time
        self._cache[key] = (value, time.time())
        self._ttl[key] = ttl or self._default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
        
        Returns:
            缓存值，如果不存在或已过期则返回None
        """
        import time
        
        if key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        ttl = self._ttl.get(key, self._default_ttl)
        
        if time.time() - timestamp > ttl:
            del self._cache[key]
            del self._ttl[key]
            return None
        
        return value
    
    def invalidate(self, key: str) -> None:
        """
        使缓存失效
        
        Args:
            key: 缓存键
        """
        if key in self._cache:
            del self._cache[key]
            del self._ttl[key]
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        使匹配模式的缓存失效
        
        Args:
            pattern: 匹配模式
        
        Returns:
            失效的缓存数量
        """
        import fnmatch
        keys_to_delete = [k for k in self._cache if fnmatch.fnmatch(k, pattern)]
        
        for key in keys_to_delete:
            self.invalidate(key)
        
        return len(keys_to_delete)
    
    def clear(self) -> int:
        """
        清空所有缓存
        
        Returns:
            清空的缓存数量
        """
        count = len(self._cache)
        self._cache.clear()
        self._ttl.clear()
        return count


# 全局查询缓存实例
query_cache = QueryCache()


# ============================================================================
# 导出列表
# ============================================================================

__all__ = [
    "DatabaseOptimizer",
    "QueryCache",
    "query_cache",
]
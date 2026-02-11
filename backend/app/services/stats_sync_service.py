"""
统计数据同步服务
定期从各平台同步文章统计数据
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from ..core.logger import logger
from ..core.database import get_db_session
from ..models.publish_platform import PublishRecord, PublishStatus, PlatformType
from .multiplatform_service import multiplatform_publisher


class StatsSyncService:
    """统计数据同步服务"""
    
    def __init__(self):
        self._running = False
        self._sync_task: Optional[asyncio.Task] = None
        self._sync_interval = 3600  # 默认1小时同步一次（秒）
    
    async def start(self, interval: int = 3600):
        """
        启动定期同步服务
        
        Args:
            interval: 同步间隔（秒），默认3600秒（1小时）
        """
        if self._running:
            logger.warning("统计数据同步服务已在运行")
            return
        
        self._sync_interval = interval
        self._running = True
        self._sync_task = asyncio.create_task(self._sync_loop())
        
        logger.info(f"统计数据同步服务已启动，同步间隔: {interval}秒")
    
    async def stop(self):
        """停止定期同步服务"""
        if not self._running:
            return
        
        self._running = False
        
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        
        logger.info("统计数据同步服务已停止")
    
    async def _sync_loop(self):
        """同步循环"""
        logger.info("开始统计数据同步循环")
        
        while self._running:
            try:
                # 等待同步间隔
                await asyncio.sleep(self._sync_interval)
                
                # 执行同步
                await self._perform_sync()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"同步循环出错: {e}")
                # 出错后继续运行，不停止服务
        
        logger.info("统计数据同步循环已停止")
    
    async def _perform_sync(self):
        """执行同步"""
        try:
            logger.info("开始执行统计数据同步")
            
            async with get_db_session() as db:
                # 同步最近7天的数据
                result = await multiplatform_publisher.sync_all_stats(db, days=7)
                
                if result["success"]:
                    logger.info(
                        f"统计数据同步完成: "
                        f"总数={result['total']}, "
                        f"成功={result['success_count']}, "
                        f"失败={result['failed_count']}"
                    )
                else:
                    logger.warning(f"统计数据同步失败: {result.get('message')}")
                
        except Exception as e:
            logger.error(f"执行统计数据同步失败: {e}")
    
    async def sync_now(self, days: int = 7) -> Dict[str, Any]:
        """
        立即执行同步
        
        Args:
            days: 同步最近N天的数据
        
        Returns:
            同步结果
        """
        try:
            logger.info(f"立即执行统计数据同步（最近{days}天）")
            
            async with get_db_session() as db:
                result = await multiplatform_publisher.sync_all_stats(db, days=days)
                
                return result
                
        except Exception as e:
            logger.error(f"立即执行同步失败: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def sync_article(self, article_id: int) -> Dict[str, Any]:
        """
        同步指定文章的统计数据
        
        Args:
            article_id: 文章ID
        
        Returns:
            同步结果
        """
        try:
            logger.info(f"同步文章 {article_id} 的统计数据")
            
            async with get_db_session() as db:
                result = await multiplatform_publisher.sync_stats_for_article(article_id, db)
                
                return result
                
        except Exception as e:
            logger.error(f"同步文章统计数据失败: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def sync_platform(self, platform: PlatformType) -> Dict[str, Any]:
        """
        同步指定平台的统计数据
        
        Args:
            platform: 平台类型
        
        Returns:
            同步结果
        """
        try:
            logger.info(f"同步平台 {platform.value} 的统计数据")
            
            async with get_db_session() as db:
                result = await multiplatform_publisher.sync_stats_for_platform(platform, db)
                
                return result
                
        except Exception as e:
            logger.error(f"同步平台统计数据失败: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def get_next_sync_time(self) -> datetime:
        """获取下次同步时间"""
        return datetime.now() + timedelta(seconds=self._sync_interval)
    
    def is_running(self) -> bool:
        """检查服务是否在运行"""
        return self._running


# 全局统计同步服务实例
stats_sync_service = StatsSyncService()


async def initialize_stats_sync():
    """初始化统计同步服务"""
    # 默认1小时同步一次
    await stats_sync_service.start(interval=3600)
    logger.info("统计同步服务初始化完成")


async def close_stats_sync():
    """关闭统计同步服务"""
    await stats_sync_service.stop()
    logger.info("统计同步服务已关闭")
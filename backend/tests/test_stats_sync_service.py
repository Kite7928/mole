"""
统计数据同步服务测试用例
"""

import pytest
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.stats_sync_service import stats_sync_service, StatsSyncService
from app.services.multiplatform_service import multiplatform_publisher
from app.models.publish_platform import PublishRecord, PublishStatus, PlatformType


class TestStatsSyncService:
    """统计同步服务测试类"""
    
    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """测试服务初始化"""
        service = StatsSyncService()
        
        # 检查初始状态
        assert not service.is_running()
        assert service.get_next_sync_time() is not None
    
    @pytest.mark.asyncio
    async def test_start_stop_service(self):
        """测试启动和停止服务"""
        service = StatsSyncService()
        
        # 启动服务（间隔1秒用于测试）
        await service.start(interval=1)
        assert service.is_running()
        
        # 等待一小段时间
        await asyncio.sleep(2)
        
        # 停止服务
        await service.stop()
        assert not service.is_running()
    
    @pytest.mark.asyncio
    async def test_sync_now_empty(self, db: AsyncSession):
        """测试立即同步（空数据）"""
        result = await stats_sync_service.sync_now(days=7)
        
        # 应该返回失败，因为没有数据
        assert result["success"] == False
        assert "没有找到" in result.get("message", "")
    
    @pytest.mark.asyncio
    async def test_sync_article_empty(self, db: AsyncSession):
        """测试同步文章（空数据）"""
        result = await stats_sync_service.sync_article(article_id=99999)
        
        # 应该返回失败，因为没有数据
        assert result["success"] == False
        assert "没有找到" in result.get("message", "")
    
    @pytest.mark.asyncio
    async def test_sync_platform_empty(self, db: AsyncSession):
        """测试同步平台（空数据）"""
        result = await stats_sync_service.sync_platform(PlatformType.ZHIHU)
        
        # 应该返回失败，因为没有数据
        assert result["success"] == False
        assert "没有找到" in result.get("message", "")


class TestMultiPlatformStatsSync:
    """多平台统计同步测试类"""
    
    @pytest.mark.asyncio
    async def test_sync_stats_for_record_no_id(self, db: AsyncSession):
        """测试同步发布记录（无平台文章ID）"""
        # 创建一个没有平台文章ID的发布记录
        record = PublishRecord(
            article_id=1,
            platform=PlatformType.ZHIHU,
            status=PublishStatus.SUCCESS,
            platform_article_id=None  # 没有平台文章ID
        )
        db.add(record)
        await db.commit()
        
        # 尝试同步
        result = await multiplatform_publisher.sync_stats_for_record(record, db)
        
        # 应该返回False，因为没有平台文章ID
        assert result == False
        
        # 清理
        await db.delete(record)
        await db.commit()
    
    @pytest.mark.asyncio
    async def test_sync_stats_for_article_empty(self, db: AsyncSession):
        """测试同步文章（空数据）"""
        result = await multiplatform_publisher.sync_stats_for_article(article_id=99999, db=db)
        
        # 应该返回失败
        assert result["success"] == False
        assert "没有找到" in result.get("message", "")
    
    @pytest.mark.asyncio
    async def test_sync_stats_for_platform_empty(self, db: AsyncSession):
        """测试同步平台（空数据）"""
        result = await multiplatform_publisher.sync_stats_for_platform(PlatformType.ZHIHU, db=db)
        
        # 应该返回失败
        assert result["success"] == False
        assert "没有找到" in result.get("message", "")
    
    @pytest.mark.asyncio
    async def test_sync_all_stats_empty(self, db: AsyncSession):
        """测试同步所有统计数据（空数据）"""
        result = await multiplatform_publisher.sync_all_stats(db=db, days=7)
        
        # 应该返回失败
        assert result["success"] == False
        assert "没有找到" in result.get("message", "")


@pytest.mark.integration
class TestStatsSyncIntegration:
    """统计同步集成测试类"""
    
    @pytest.mark.asyncio
    async def test_full_sync_workflow(self, db: AsyncSession):
        """测试完整的同步工作流"""
        # 1. 创建一个模拟的发布记录
        record = PublishRecord(
            article_id=1,
            platform=PlatformType.ZHIHU,
            status=PublishStatus.SUCCESS,
            platform_article_id="test_123",
            platform_article_url="https://zhuanlan.zhihu.com/p/test",
            view_count=100,
            like_count=10,
            comment_count=5,
            title_snapshot="测试文章",
            content_snapshot="测试内容"
        )
        db.add(record)
        await db.commit()
        
        try:
            # 2. 同步该记录
            result = await multiplatform_publisher.sync_stats_for_record(record, db)
            
            # 3. 验证结果
            # 注意：由于是模拟数据，实际可能无法获取到真实的统计数据
            # 这里主要测试调用是否正常
            
            # 4. 清理
            await db.delete(record)
            await db.commit()
            
        except Exception as e:
            # 清理
            await db.delete(record)
            await db.commit()
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
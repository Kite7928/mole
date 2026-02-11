"""
多平台发布服务测试用例
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.types import ArticleContent, PublishResult
from app.services.multiplatform_service import multiplatform_publisher
from app.models.publish_platform import (
    PlatformType, PlatformConfig, PublishRecord,
    PublishTask, PublishStatus, PLATFORM_INFO
)
from app.models.article import Article
from app.core.database import async_session
from app.services.async_task_queue import task_queue


@pytest.fixture
async def db_session():
    """创建测试数据库会话"""
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_article(db_session: AsyncSession):
    """创建测试文章"""
    article = Article(
        title="测试文章标题",
        content="这是一篇测试文章的内容，用于多平台发布功能的测试。",
        summary="测试文章摘要",
        html_content="<p>这是一篇测试文章的内容，用于多平台发布功能的测试。</p>",
        status="ready"
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)
    return article


@pytest.fixture
async def test_platform_config(db_session: AsyncSession):
    """创建测试平台配置"""
    import json
    
    config = PlatformConfig(
        platform=PlatformType.ZHIHU,
        cookies=json.dumps({"z_c0": "test_cookie"}),
        is_configured=True,
        is_enabled=True,
        auto_publish=False
    )
    db_session.add(config)
    await db_session.commit()
    await db_session.refresh(config)
    return config


class TestMultiplatformService:
    """多平台发布服务测试"""
    
    @pytest.mark.asyncio
    async def test_get_supported_platforms(self):
        """测试获取支持的平台列表"""
        platforms = multiplatform_publisher.get_supported_platforms()
        
        assert isinstance(platforms, list)
        assert len(platforms) > 0
        
        # 检查平台信息格式
        for platform in platforms:
            assert "type" in platform
            assert "name" in platform
            assert "icon" in platform
            assert "description" in platform
    
    @pytest.mark.asyncio
    async def test_platform_info(self):
        """测试平台信息常量"""
        # 测试知乎平台信息
        zhihu_info = PLATFORM_INFO[PlatformType.ZHIHU]
        assert zhihu_info["name"] == "知乎"
        assert zhihu_info["icon"] == "📚"
        assert zhihu_info["support_html"] == True
        assert zhihu_info["support_markdown"] == True
        
        # 测试掘金平台信息
        juejin_info = PLATFORM_INFO[PlatformType.JUEJIN]
        assert juejin_info["name"] == "掘金"
        assert juejin_info["icon"] == "🚀"
        assert juejin_info["support_html"] == False
        assert juejin_info["support_markdown"] == True
    
    @pytest.mark.asyncio
    async def test_load_publishers(self, test_platform_config):
        """测试加载发布器"""
        # 加载发布器
        await multiplatform_publisher.load_publishers(async_session)
        
        # 检查是否加载成功
        publisher = multiplatform_publisher.get_publisher(PlatformType.ZHIHU)
        assert publisher is not None
        assert publisher.platform == PlatformType.ZHIHU
    
    @pytest.mark.asyncio
    async def test_article_content_validation(self, test_platform_config):
        """测试文章内容验证"""
        # 创建发布器
        from app.services.multiplatform_service import ZhihuPublisher
        publisher = ZhihuPublisher(test_platform_config)
        
        # 测试有效内容
        valid_content = ArticleContent(
            title="测试标题",
            content="这是一篇测试文章的内容，用于多平台发布功能的测试。"
        )
        
        is_valid, message = await publisher.validate_content(valid_content)
        assert is_valid == True
        assert message == ""
        
        # 测试无效标题
        invalid_content = ArticleContent(
            title="短",
            content="这是一篇测试文章的内容，用于多平台发布功能的测试。"
        )
        
        is_valid, message = await publisher.validate_content(invalid_content)
        assert is_valid == False
        assert "标题" in message
    
    @pytest.mark.asyncio
    async def test_content_conversion(self, test_platform_config):
        """测试内容格式转换"""
        from app.services.multiplatform_service import ZhihuPublisher
        publisher = ZhihuPublisher(test_platform_config)
        
        # 测试HTML转Markdown
        html_content = "<h1>标题</h1><p>段落内容</p>"
        article = ArticleContent(
            title="测试",
            content=html_content
        )
        
        # 知乎支持Markdown，会进行转换
        converted = publisher.convert_content(article)
        assert isinstance(converted.content, str)
        # HTML标签应该被转换
        assert "<h1>" not in converted.content or "<p>" not in converted.content
    
    @pytest.mark.asyncio
    async def test_publish_to_single_platform(self, test_article, test_platform_config):
        """测试发布到单个平台"""
        # 加载发布器
        await multiplatform_publisher.load_publishers(async_session)
        
        # 准备文章内容
        article_content = ArticleContent(
            title=test_article.title,
            content=test_article.content,
            summary=test_article.summary,
            tags=["测试", "多平台发布"]
        )
        
        # 发布到知乎
        result = await multiplatform_publisher.publish_to_platform(
            platform=PlatformType.ZHIHU,
            article=article_content,
            article_id=test_article.id,
            db=async_session
        )
        
        # 验证结果
        assert isinstance(result, PublishResult)
        assert result.platform == PlatformType.ZHIHU
        
        # 检查发布记录
        query = await async_session.execute(
            select(PublishRecord).where(
                PublishRecord.article_id == test_article.id,
                PublishRecord.platform == PlatformType.ZHIHU
            )
        )
        record = query.scalar_one_or_none()
        
        assert record is not None
        assert record.status in [PublishStatus.SUCCESS, PublishStatus.FAILED]
    
    @pytest.mark.asyncio
    async def test_publish_to_multiple_platforms(self, test_article):
        """测试批量发布到多个平台"""
        # 准备文章内容
        article_content = ArticleContent(
            title=test_article.title,
            content=test_article.content,
            summary=test_article.summary,
            tags=["测试", "多平台发布"]
        )
        
        # 发布到多个平台
        platforms = [PlatformType.ZHIHU, PlatformType.JUEJIN, PlatformType.TOUTIAO]
        results = await multiplatform_publisher.publish_to_multiple_platforms(
            platforms=platforms,
            article=article_content,
            article_id=test_article.id,
            db=async_session
        )
        
        # 验证结果
        assert isinstance(results, dict)
        assert len(results) == len(platforms)
        
        for platform in platforms:
            assert platform in results
            assert isinstance(results[platform], PublishResult)
            assert results[platform].platform == platform
    
    @pytest.mark.asyncio
    async def test_schedule_publish(self, test_article):
        """测试定时发布"""
        # 准备文章内容
        article_content = ArticleContent(
            title=test_article.title,
            content=test_article.content,
            summary=test_article.summary,
            tags=["测试", "定时发布"]
        )
        
        # 设置1分钟后发布
        publish_at = datetime.now() + timedelta(minutes=1)
        
        # 创建定时发布任务
        task_id = await multiplatform_publisher.schedule_publish(
            platforms=[PlatformType.ZHIHU],
            article=article_content,
            article_id=test_article.id,
            publish_at=publish_at,
            db=async_session
        )
        
        # 验证任务ID
        assert task_id is not None
        assert isinstance(task_id, str)
        assert "schedule_" in task_id
    
    @pytest.mark.asyncio
    async def test_get_publish_history(self, test_article):
        """测试获取发布历史"""
        # 获取发布历史
        history = await multiplatform_publisher.get_publish_history(
            article_id=test_article.id,
            db=async_session
        )
        
        # 验证结果
        assert isinstance(history, list)
        # 可能是空列表，因为还没有发布记录
    
    @pytest.mark.asyncio
    async def test_publish_task_record(self, test_article):
        """测试发布任务记录"""
        # 准备文章内容
        article_content = ArticleContent(
            title=test_article.title,
            content=test_article.content,
            summary=test_article.summary
        )
        
        # 发布到多个平台
        platforms = [PlatformType.ZHIHU, PlatformType.JUEJIN]
        await multiplatform_publisher.publish_to_multiple_platforms(
            platforms=platforms,
            article=article_content,
            article_id=test_article.id,
            db=async_session
        )
        
        # 查询发布任务
        query = await async_session.execute(
            select(PublishTask).where(PublishTask.article_id == test_article.id)
        )
        task = query.scalar_one_or_none()
        
        # 验证任务记录
        if task:
            assert task.article_id == test_article.id
            assert task.total_count == len(platforms)
            assert task.status in [PublishStatus.SUCCESS, PublishStatus.FAILED, PublishStatus.PARTIAL]


class TestMultiplatformAPI:
    """多平台发布API测试"""
    
    @pytest.mark.asyncio
    async def test_get_platforms(self):
        """测试获取平台列表API"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/api/multiplatform/platforms")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "platforms" in data
        assert isinstance(data["platforms"], list)
    
    @pytest.mark.asyncio
    async def test_get_platform_configs(self):
        """测试获取平台配置API"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/api/multiplatform/configs")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "configs" in data
        assert isinstance(data["configs"], list)
    
    @pytest.mark.asyncio
    async def test_save_platform_config(self):
        """测试保存平台配置API"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        config_data = {
            "platform": "zhihu",
            "cookies": '{"z_c0": "test_cookie"}',
            "auto_publish": False
        }
        
        response = client.post("/api/multiplatform/configs", json=config_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_get_publish_tasks(self):
        """测试获取发布任务API"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/api/multiplatform/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "tasks" in data


class TestAsyncTaskQueue:
    """异步任务队列测试"""
    
    @pytest.mark.asyncio
    async def test_task_queue_submit(self):
        """测试提交任务"""
        async def test_task(value: int) -> int:
            return value * 2
        
        task_id = await task_queue.submit(
            name="test_task",
            func=test_task,
            value=5
        )
        
        assert task_id is not None
        assert isinstance(task_id, str)
    
    @pytest.mark.asyncio
    async def test_task_queue_get_stats(self):
        """测试获取队列统计"""
        stats = await task_queue.get_stats()
        
        assert "total_tasks" in stats
        assert "pending" in stats
        assert "running" in stats
        assert "completed" in stats
        assert "scheduled" in stats
        assert "queue_size" in stats
    
    @pytest.mark.asyncio
    async def test_scheduled_task(self):
        """测试定时任务"""
        # 添加5秒后执行的任务
        scheduled_time = datetime.now() + timedelta(seconds=5)
        task_id = await task_queue.add_task(
            task_id="test_scheduled_task",
            task_type="test",
            params={"test": "data"},
            scheduled_at=scheduled_time.timestamp()
        )
        
        assert task_id is not None
        
        # 等待6秒
        await asyncio.sleep(6)
        
        # 检查任务是否已从定时任务列表中移除
        assert task_id not in task_queue.scheduled_tasks


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
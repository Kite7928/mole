"""
多平台发布API
支持知乎、掘金、头条等多平台文章发布
"""

from typing import List, Optional
from datetime import datetime
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from ..core.database import get_db
from ..core.logger import logger
from ..core.security import get_current_user
from ..models.publish_platform import (
    PlatformType, PlatformConfig, PublishRecord,
    PublishTask, PublishStatus, PLATFORM_INFO
)
from ..types import ArticleContent
from ..services.publish_service import (
    publisher_manager, init_publishers
)


router = APIRouter(prefix="/publish", tags=["多平台发布"])


# ============== 请求/响应模型 ==============

class PlatformConfigRequest(BaseModel):
    """平台配置请求"""
    platform: PlatformType
    cookies: Optional[str] = None
    token: Optional[str] = None
    default_category: Optional[str] = None
    default_tags: Optional[str] = None
    auto_publish: bool = False
    
    class Config:
        from_attributes = True


class PlatformConfigResponse(BaseModel):
    """平台配置响应"""
    platform: str
    name: str
    icon: str
    description: str
    is_enabled: bool
    is_configured: bool
    support_markdown: bool
    support_html: bool
    
    class Config:
        from_attributes = True


class PublishArticleRequest(BaseModel):
    """发布文章请求"""
    article_id: int = Field(..., description="文章ID")
    platforms: List[PlatformType] = Field(..., description="目标平台列表")
    title: Optional[str] = Field(None, description="自定义标题（覆盖原文）")
    content: Optional[str] = Field(None, description="自定义内容（覆盖原文）")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    category: Optional[str] = Field(None, description="分类")
    auto_publish: bool = Field(False, description="是否直接发布（False则保存草稿）")
    
    
class PublishResultResponse(BaseModel):
    """发布结果响应"""
    platform: str
    platform_name: str
    success: bool
    message: str
    article_url: Optional[str] = None
    article_id: Optional[str] = None
    

class BatchPublishResponse(BaseModel):
    """批量发布响应"""
    task_id: int
    total: int
    success_count: int
    failed_count: int
    results: List[PublishResultResponse]
    

class PublishRecordResponse(BaseModel):
    """发布记录响应"""
    id: int
    article_id: int
    platform: str
    status: str
    platform_article_url: Optional[str]
    view_count: int
    like_count: int
    created_at: str
    published_at: Optional[str]
    
    class Config:
        from_attributes = True


# ============== API端点 ==============

@router.get("/platforms", response_model=List[PlatformConfigResponse])
async def get_platforms(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取支持的平台列表及配置状态
    
    Returns:
        平台列表，包含配置状态
    """
    try:
        from sqlalchemy import select
        
        # 查询数据库中的配置
        query = select(PlatformConfig)
        result = await db.execute(query)
        configs = {cfg.platform: cfg for cfg in result.scalars().all()}
        
        # 构建响应
        platforms = []
        for platform_type in PlatformType:
            info = PLATFORM_INFO.get(platform_type, {})
            config = configs.get(platform_type)
            
            platforms.append(PlatformConfigResponse(
                platform=platform_type.value,
                name=info.get("name", platform_type.value),
                icon=info.get("icon", "📄"),
                description=info.get("description", ""),
                is_enabled=config.is_enabled if config else False,
                is_configured=config.is_configured if config else False,
                support_markdown=info.get("support_markdown", False),
                support_html=info.get("support_html", True),
            ))
        
        return platforms
        
    except Exception as e:
        logger.error(f"获取平台列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取平台列表失败: {str(e)}"
        )


@router.post("/config", response_model=dict)
async def save_platform_config(
    config: PlatformConfigRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    保存平台配置
    
    Args:
        config: 平台配置信息
        
    Returns:
        保存结果
    """
    try:
        from sqlalchemy import select
        
        # 查询是否已有配置
        query = select(PlatformConfig).where(
            PlatformConfig.platform == config.platform
        )
        result = await db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            # 更新配置
            existing.cookies = config.cookies
            existing.token = config.token
            existing.default_category = config.default_category
            existing.default_tags = config.default_tags
            existing.auto_publish = config.auto_publish
            existing.is_configured = bool(config.cookies or config.token)
            existing.updated_at = datetime.now()
        else:
            # 创建新配置
            new_config = PlatformConfig(
                platform=config.platform,
                cookies=config.cookies,
                token=config.token,
                default_category=config.default_category,
                default_tags=config.default_tags,
                auto_publish=config.auto_publish,
                is_enabled=True,
                is_configured=bool(config.cookies or config.token),
            )
            db.add(new_config)
        
        await db.commit()
        
        # 重新初始化发布器
        await reload_platform_configs(db)
        
        return {
            "success": True,
            "message": f"{config.platform.value} 配置已保存"
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"保存平台配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存配置失败: {str(e)}"
        )


@router.post("/article", response_model=BatchPublishResponse)
async def publish_article(
    request: PublishArticleRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    发布文章到多个平台
    
    Args:
        request: 发布请求
        
    Returns:
        发布结果
    """
    try:
        from sqlalchemy import select
        from ..models.article import Article
        
        # 获取文章信息
        query = select(Article).where(Article.id == request.article_id)
        result = await db.execute(query)
        article = result.scalar_one_or_none()
        
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文章不存在"
            )
        
        # 准备发布内容
        content = ArticleContent(
            title=request.title or article.title,
            content=request.content or article.html_content or article.content,
            summary=article.summary,
            cover_image=article.cover_image_url,
            tags=request.tags or (article.get_tags_list() if hasattr(article, 'get_tags_list') else []),
            category=request.category
        )
        
        # 创建发布任务记录
        task = PublishTask(
            name=f"发布文章: {content.title}",
            article_id=article.id,
            target_platforms=json.dumps([p.value for p in request.platforms]),
            status=PublishStatus.PUBLISHING,
            total_count=len(request.platforms),
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        # 执行发布
        results = await publisher_manager.publish_to_multiple_platforms(
            request.platforms,
            content
        )
        
        # 处理结果
        success_count = 0
        failed_count = 0
        response_results = []
        
        for result in results:
            # 保存发布记录
            record = PublishRecord(
                article_id=article.id,
                platform=result.platform,
                status=PublishStatus.SUCCESS if result.success else PublishStatus.FAILED,
                error_message=None if result.success else result.message,
                platform_article_id=result.article_id,
                platform_article_url=result.article_url,
                title_snapshot=content.title,
                content_snapshot=content.content[:500] + "..." if len(content.content) > 500 else content.content,
            )
            db.add(record)
            
            if result.success:
                success_count += 1
            else:
                failed_count += 1
            
            # 构建响应
            platform_info = PLATFORM_INFO.get(result.platform, {})
            response_results.append(PublishResultResponse(
                platform=result.platform.value,
                platform_name=platform_info.get("name", result.platform.value),
                success=result.success,
                message=result.message,
                article_url=result.article_url,
                article_id=result.article_id,
            ))
        
        # 更新任务状态
        task.status = PublishStatus.SUCCESS if failed_count == 0 else (
            PublishStatus.PARTIAL if success_count > 0 else PublishStatus.FAILED
        )
        task.success_count = success_count
        task.failed_count = failed_count
        task.completed_at = datetime.now()
        
        await db.commit()
        
        return BatchPublishResponse(
            task_id=task.id,
            total=len(request.platforms),
            success_count=success_count,
            failed_count=failed_count,
            results=response_results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"发布文章失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发布失败: {str(e)}"
        )


@router.get("/records/{article_id}", response_model=List[PublishRecordResponse])
async def get_publish_records(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取文章的发布记录
    
    Args:
        article_id: 文章ID
        
    Returns:
        发布记录列表
    """
    try:
        from sqlalchemy import select
        
        query = select(PublishRecord).where(
            PublishRecord.article_id == article_id
        ).order_by(PublishRecord.created_at.desc())
        
        result = await db.execute(query)
        records = result.scalars().all()
        
        return [
            PublishRecordResponse(
                id=r.id,
                article_id=r.article_id,
                platform=r.platform.value,
                status=r.status.value,
                platform_article_url=r.platform_article_url,
                view_count=r.view_count,
                like_count=r.like_count,
                created_at=r.created_at.isoformat() if r.created_at else None,
                published_at=r.published_at.isoformat() if r.published_at else None,
            )
            for r in records
        ]
        
    except Exception as e:
        logger.error(f"获取发布记录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取记录失败: {str(e)}"
        )


@router.post("/test/{platform}", response_model=dict)
async def test_platform_connection(
    platform: PlatformType,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    测试平台连接
    
    Args:
        platform: 平台类型
        
    Returns:
        测试结果
    """
    try:
        publisher = publisher_manager.get_publisher(platform)
        if not publisher:
            return {
                "success": False,
                "message": f"平台 {platform.value} 未配置"
            }
        
        is_logged_in = await publisher.check_login_status()
        
        return {
            "success": is_logged_in,
            "message": "连接正常" if is_logged_in else "未登录或登录已过期"
        }
        
    except Exception as e:
        logger.error(f"测试平台连接失败: {e}")
        return {
            "success": False,
            "message": f"测试失败: {str(e)}"
        }


# ============== 辅助函数 ==============

async def reload_platform_configs(db: AsyncSession):
    """重新加载平台配置"""
    try:
        from sqlalchemy import select
        
        query = select(PlatformConfig).where(PlatformConfig.is_enabled == True)
        result = await db.execute(query)
        configs = result.scalars().all()
        
        platform_configs = {}
        for config in configs:
            platform_configs[config.platform] = {
                "cookies": config.cookies,
                "token": config.token,
                "default_category": config.default_category,
                "default_tags": config.default_tags,
                "auto_publish": config.auto_publish,
            }
        
        init_publishers(platform_configs)
        logger.info(f"已重新加载 {len(platform_configs)} 个平台配置")
        
    except Exception as e:
        logger.error(f"重新加载平台配置失败: {e}")

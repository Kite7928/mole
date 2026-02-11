"""
多平台发布API路由
支持知乎、掘金、头条等多平台文章发布
基于 Mixpost 核心逻辑
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.database import get_db
from ..core.logger import logger
from ..models.publish_platform import (
    PlatformType, PlatformConfig, PublishRecord,
    PublishTask, PublishStatus, PLATFORM_INFO
)
from ..models.article import Article
from ..types import ArticleContent, PublishResult
from ..services.multiplatform_service import multiplatform_publisher


router = APIRouter()


class PlatformConfigRequest(BaseModel):
    """平台配置请求"""
    platform: str = Field(..., description="平台类型（zhihu/juejin/toutiao）")
    cookies: Optional[str] = Field(None, description="Cookie数据（JSON字符串）")
    token: Optional[str] = Field(None, description="API Token")
    auto_publish: Optional[bool] = Field(False, description="是否自动发布（还是保存草稿）")
    default_category: Optional[str] = Field(None, description="默认分类")
    default_tags: Optional[str] = Field(None, description="默认标签（逗号分隔）")


class PublishRequest(BaseModel):
    """发布请求"""
    article_id: int = Field(..., description="文章ID")
    platforms: List[str] = Field(..., description="目标平台列表")
    publish_now: bool = Field(True, description="是否立即发布")
    scheduled_at: Optional[datetime] = Field(None, description="定时发布时间")


class PublishResultResponse(BaseModel):
    """发布结果响应"""
    success: bool
    platform: str
    message: str
    article_id: Optional[str] = None
    article_url: Optional[str] = None
    error_code: Optional[str] = None


@router.get("/platforms")
async def get_supported_platforms():
    """
    获取支持的平台列表
    
    Returns:
        平台列表
    """
    try:
        platforms = multiplatform_publisher.get_supported_platforms()
        return {
            "success": True,
            "platforms": platforms
        }
    except Exception as e:
        logger.error(f"获取平台列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取平台列表失败: {str(e)}")


@router.get("/configs")
async def get_platform_configs(db: AsyncSession = Depends(get_db)):
    """
    获取所有平台配置
    
    Returns:
        平台配置列表
    """
    try:
        query = select(PlatformConfig)
        result = await db.execute(query)
        configs = result.scalars().all()
        
        config_list = []
        for config in configs:
            config_list.append({
                "id": config.id,
                "platform": config.platform.value,
                "is_enabled": config.is_enabled,
                "is_configured": config.is_configured,
                "auto_publish": config.auto_publish,
                "default_category": config.default_category,
                "default_tags": config.default_tags,
                "last_login_at": config.last_login_at.isoformat() if config.last_login_at else None,
            })
        
        return {
            "success": True,
            "configs": config_list
        }
    except Exception as e:
        logger.error(f"获取平台配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取平台配置失败: {str(e)}")


@router.get("/configs/{platform}")
async def get_platform_config(platform: str, db: AsyncSession = Depends(get_db)):
    """
    获取指定平台配置
    
    Args:
        platform: 平台类型
    
    Returns:
        平台配置
    """
    try:
        platform_type = PlatformType(platform)
        
        query = select(PlatformConfig).where(PlatformConfig.platform == platform_type)
        result = await db.execute(query)
        config = result.scalar_one_or_none()
        
        if not config:
            return {
                "success": True,
                "platform": platform,
                "configured": False,
                "message": "平台未配置"
            }
        
        return {
            "success": True,
            "platform": platform,
            "configured": config.is_configured,
            "enabled": config.is_enabled,
            "auto_publish": config.auto_publish,
            "default_category": config.default_category,
            "default_tags": config.default_tags,
            "last_login_at": config.last_login_at.isoformat() if config.last_login_at else None,
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"不支持的平台: {platform}")
    except Exception as e:
        logger.error(f"获取平台配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取平台配置失败: {str(e)}")


@router.post("/configs")
async def save_platform_config(
    request: PlatformConfigRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    保存平台配置
    
    Args:
        request: 平台配置请求
    
    Returns:
        配置结果
    """
    try:
        platform_type = PlatformType(request.platform)
        
        # 查询现有配置
        query = select(PlatformConfig).where(PlatformConfig.platform == platform_type)
        result = await db.execute(query)
        config = result.scalar_one_or_none()
        
        if config:
            # 更新配置
            config.cookies = request.cookies
            config.token = request.token
            config.is_configured = bool(request.cookies or request.token)
            config.is_enabled = True
            config.auto_publish = request.auto_publish or False
            config.default_category = request.default_category
            config.default_tags = request.default_tags
            config.last_login_at = datetime.now()
        else:
            # 创建新配置
            config = PlatformConfig(
                platform=platform_type,
                cookies=request.cookies,
                token=request.token,
                is_configured=bool(request.cookies or request.token),
                is_enabled=True,
                auto_publish=request.auto_publish or False,
                default_category=request.default_category,
                default_tags=request.default_tags,
                last_login_at=datetime.now()
            )
            db.add(config)
        
        await db.commit()
        
        # 重新加载发布器
        await multiplatform_publisher.load_publishers(db)
        
        logger.info(f"平台配置已保存: {request.platform}")
        
        return {
            "success": True,
            "message": f"{PLATFORM_INFO[platform_type]['name']} 配置已保存",
            "platform": request.platform,
            "configured": True
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail=f"不支持的平台: {request.platform}")
    except Exception as e:
        logger.error(f"保存平台配置失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"保存平台配置失败: {str(e)}")


@router.delete("/configs/{platform}")
async def delete_platform_config(platform: str, db: AsyncSession = Depends(get_db)):
    """
    删除平台配置
    
    Args:
        platform: 平台类型
    
    Returns:
        删除结果
    """
    try:
        platform_type = PlatformType(platform)
        
        query = select(PlatformConfig).where(PlatformConfig.platform == platform_type)
        result = await db.execute(query)
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(status_code=404, detail=f"平台 {platform} 未配置")
        
        # 禁用配置
        config.is_enabled = False
        await db.commit()
        
        # 重新加载发布器
        await multiplatform_publisher.load_publishers(db)
        
        logger.info(f"平台配置已删除: {platform}")
        
        return {
            "success": True,
            "message": f"{PLATFORM_INFO[platform_type]['name']} 配置已删除"
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail=f"不支持的平台: {platform}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除平台配置失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除平台配置失败: {str(e)}")


@router.post("/publish")
async def publish_to_platforms(
    request: PublishRequest, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    发布文章到多个平台
    
    Args:
        request: 发布请求
        background_tasks: 后台任务
        db: 数据库会话
    
    Returns:
        发布结果
    """
    try:
        # 1. 验证文章
        query = select(Article).where(Article.id == request.article_id)
        result = await db.execute(query)
        article = result.scalar_one_or_none()
        
        if not article:
            raise HTTPException(status_code=404, detail=f"文章不存在: {request.article_id}")
        
        # 2. 验证平台
        platform_types = []
        for platform_str in request.platforms:
            try:
                platform_type = PlatformType(platform_str)
                platform_types.append(platform_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"不支持的平台: {platform_str}")
        
        if not platform_types:
            raise HTTPException(status_code=400, detail="请至少选择一个平台")
        
        # 3. 准备文章内容
        article_content = ArticleContent(
            title=article.title,
            content=article.content,
            summary=article.summary,
            cover_image=article.cover_image_url,
            tags=article.get_tags_list() if article.tags else None,
            author="AI助手"
        )
        
        # 4. 发布
        if request.publish_now:
            # 立即发布
            results = await multiplatform_publisher.publish_to_multiple_platforms(
                platforms=platform_types,
                article=article_content,
                article_id=article.id,
                db=db
            )
            
            # 格式化结果
            formatted_results = []
            for platform, result in results.items():
                formatted_results.append({
                    "platform": platform.value,
                    "success": result.success,
                    "message": result.message,
                    "article_id": result.article_id,
                    "article_url": result.article_url
                })
            
            return {
                "success": True,
                "message": f"已发布到 {len([r for r in results.values() if r.success])} 个平台",
                "results": formatted_results
            }
        else:
            # 定时发布
            if not request.scheduled_at:
                raise HTTPException(status_code=400, detail="定时发布需要指定 scheduled_at")
            
            if request.scheduled_at < datetime.now():
                raise HTTPException(status_code=400, detail="定时发布时间不能早于当前时间")
            
            task_id = await multiplatform_publisher.schedule_publish(
                platforms=platform_types,
                article=article_content,
                article_id=article.id,
                publish_at=request.scheduled_at,
                db=db
            )
            
            return {
                "success": True,
                "message": f"已创建定时发布任务",
                "task_id": task_id,
                "scheduled_at": request.scheduled_at.isoformat()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发布失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"发布失败: {str(e)}")


@router.get("/history/{article_id}")
async def get_publish_history(article_id: int, db: AsyncSession = Depends(get_db)):
    """
    获取文章发布历史
    
    Args:
        article_id: 文章ID
    
    Returns:
        发布历史列表
    """
    try:
        history = await multiplatform_publisher.get_publish_history(article_id, db)
        
        history_list = []
        for record in history:
            history_list.append({
                "id": record.id,
                "platform": record.platform.value,
                "status": record.status.value,
                "platform_article_id": record.platform_article_id,
                "platform_article_url": record.platform_article_url,
                "platform_status": record.platform_status,
                "view_count": record.view_count,
                "like_count": record.like_count,
                "comment_count": record.comment_count,
                "error_message": record.error_message,
                "created_at": record.created_at.isoformat(),
                "published_at": record.published_at.isoformat() if record.published_at else None,
            })
        
        return {
            "success": True,
            "history": history_list
        }
    except Exception as e:
        logger.error(f"获取发布历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取发布历史失败: {str(e)}")


@router.get("/tasks")
async def get_publish_tasks(db: AsyncSession = Depends(get_db)):
    """
    获取发布任务列表
    
    Returns:
        任务列表
    """
    try:
        query = select(PublishTask).order_by(PublishTask.created_at.desc())
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        task_list = []
        for task in tasks:
            target_platforms = json.loads(task.target_platforms) if task.target_platforms else []
            
            task_list.append({
                "id": task.id,
                "name": task.name,
                "article_id": task.article_id,
                "target_platforms": target_platforms,
                "status": task.status.value,
                "total_count": task.total_count,
                "success_count": task.success_count,
                "failed_count": task.failed_count,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            })
        
        return {
            "success": True,
            "tasks": task_list
        }
    except Exception as e:
        logger.error(f"获取发布任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取发布任务失败: {str(e)}")


@router.get("/tasks/{task_id}")
async def get_publish_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """
    获取发布任务详情
    
    Args:
        task_id: 任务ID
    
    Returns:
        任务详情
    """
    try:
        query = select(PublishTask).where(PublishTask.id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
        
        target_platforms = json.loads(task.target_platforms) if task.target_platforms else []
        
        return {
            "success": True,
            "task": {
                "id": task.id,
                "name": task.name,
                "article_id": task.article_id,
                "target_platforms": target_platforms,
                "status": task.status.value,
                "total_count": task.total_count,
                "success_count": task.success_count,
                "failed_count": task.failed_count,
                "error_log": task.error_log,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取发布任务详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取发布任务详情失败: {str(e)}")


@router.post("/sync/article/{article_id}")
async def sync_article_stats(article_id: int, db: AsyncSession = Depends(get_db)):
    """
    同步文章的所有平台统计数据
    
    Args:
        article_id: 文章ID
    
    Returns:
        同步结果
    """
    try:
        result = await multiplatform_publisher.sync_stats_for_article(article_id, db)
        return result
    except Exception as e:
        logger.error(f"同步文章统计数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


@router.post("/sync/platform/{platform}")
async def sync_platform_stats(platform: str, db: AsyncSession = Depends(get_db)):
    """
    同步指定平台的所有统计数据
    
    Args:
        platform: 平台类型
    
    Returns:
        同步结果
    """
    try:
        platform_type = PlatformType(platform)
        result = await multiplatform_publisher.sync_stats_for_platform(platform_type, db)
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail=f"不支持的平台: {platform}")
    except Exception as e:
        logger.error(f"同步平台统计数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


@router.post("/sync/all")
async def sync_all_stats(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """
    同步所有平台的统计数据
    
    Args:
        days: 同步最近N天的数据（默认7天）
    
    Returns:
        同步结果
    """
    try:
        result = await multiplatform_publisher.sync_all_stats(db, days=days)
        return result
    except Exception as e:
        logger.error(f"同步所有统计数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


@router.get("/stats/summary")
async def get_stats_summary(db: AsyncSession = Depends(get_db)):
    """
    获取统计数据摘要
    
    Returns:
        统计数据摘要
    """
    try:
        from sqlalchemy import func, and_
        
        # 查询所有成功的发布记录
        query = select(
            PublishRecord.platform,
            func.count(PublishRecord.id).label('total'),
            func.sum(PublishRecord.view_count).label('total_views'),
            func.sum(PublishRecord.like_count).label('total_likes'),
            func.sum(PublishRecord.comment_count).label('total_comments')
        ).where(
            PublishRecord.status == PublishStatus.SUCCESS
        ).group_by(PublishRecord.platform)
        
        result = await db.execute(query)
        platform_stats = result.fetchall()
        
        # 格式化结果
        summary = []
        for stat in platform_stats:
            summary.append({
                "platform": stat.platform.value,
                "total_articles": stat.total,
                "total_views": stat.total_views or 0,
                "total_likes": stat.total_likes or 0,
                "total_comments": stat.total_comments or 0,
                "avg_views": (stat.total_views / stat.total) if stat.total else 0
            })
        
        # 计算总计
        total_articles = sum(s['total_articles'] for s in summary)
        total_views = sum(s['total_views'] for s in summary)
        total_likes = sum(s['total_likes'] for s in summary)
        total_comments = sum(s['total_comments'] for s in summary)
        
        return {
            "success": True,
            "summary": {
                "total_articles": total_articles,
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "avg_views": (total_views / total_articles) if total_articles else 0
            },
            "by_platform": summary
        }
    except Exception as e:
        logger.error(f"获取统计数据摘要失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计数据摘要失败: {str(e)}")
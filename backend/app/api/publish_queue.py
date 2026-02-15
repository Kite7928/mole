"""
发布队列管理API
提供发布队列、定时发布、发布历史等功能
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload
import asyncio

from ..core.database import get_db
from ..core.logger import logger
from ..models.article import Article, ArticleStatus
from ..models.publish_platform import PublishRecord, PublishStatus, PlatformType
from ..services.wechat_service import wechat_service

router = APIRouter()


class PublishQueueItem(BaseModel):
    """队列项目"""
    id: int
    article_id: int
    article_title: str
    platform: str
    scheduled_time: Optional[datetime]
    status: str
    created_at: datetime
    error_message: Optional[str] = None


class SchedulePublishRequest(BaseModel):
    """定时发布请求"""
    article_id: int
    platform: str = "wechat"  # wechat, weibo, etc.
    scheduled_time: datetime
    publish_options: dict = Field(default_factory=dict)


class QueueStats(BaseModel):
    """队列统计"""
    total_pending: int
    scheduled_today: int
    scheduled_this_week: int
    failed_recent: int
    published_today: int


@router.get("/queue", response_model=List[PublishQueueItem])
async def get_publish_queue(
    status: Optional[str] = None,
    platform: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    获取发布队列
    可按状态和平台筛选
    """
    try:
        query = select(PublishRecord).options(
            selectinload(PublishRecord.article)
        ).order_by(desc(PublishRecord.created_at))
        
        # 应用筛选
        conditions = []
        if status:
            conditions.append(PublishRecord.status == PublishStatus(status))
        if platform:
            conditions.append(PublishRecord.platform == PlatformType(platform))
        
        # 默认显示待发布、已计划、发布中的
        if not status:
            conditions.append(PublishRecord.status.in_([
                PublishStatus.PENDING,
                PublishStatus.SCHEDULED,
                PublishStatus.PUBLISHING
            ]))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.limit(limit)
        result = await db.execute(query)
        records = result.scalars().all()
        
        queue_items = []
        for record in records:
            queue_items.append(PublishQueueItem(
                id=record.id,
                article_id=record.article_id,
                article_title=record.article.title if record.article else "未知文章",
                platform=record.platform.value,
                scheduled_time=record.scheduled_time,
                status=record.status.value,
                created_at=record.created_at,
                error_message=record.error_message
            ))
        
        return queue_items
        
    except Exception as e:
        logger.error(f"获取发布队列失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取队列失败: {str(e)}")


@router.get("/queue/stats", response_model=QueueStats)
async def get_queue_stats(db: AsyncSession = Depends(get_db)):
    """获取队列统计信息"""
    try:
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        
        # 待发布数量
        pending_result = await db.execute(
            select(func.count(PublishRecord.id)).where(
                PublishRecord.status.in_([
                    PublishStatus.PENDING,
                    PublishStatus.SCHEDULED
                ])
            )
        )
        total_pending = pending_result.scalar() or 0
        
        # 今日计划发布
        today_scheduled_result = await db.execute(
            select(func.count(PublishRecord.id)).where(
                and_(
                    PublishRecord.scheduled_time >= today_start,
                    PublishRecord.scheduled_time < today_start + timedelta(days=1),
                    PublishRecord.status == PublishStatus.SCHEDULED
                )
            )
        )
        scheduled_today = today_scheduled_result.scalar() or 0
        
        # 本周计划发布
        week_scheduled_result = await db.execute(
            select(func.count(PublishRecord.id)).where(
                and_(
                    PublishRecord.scheduled_time >= week_start,
                    PublishRecord.scheduled_time < week_start + timedelta(days=7),
                    PublishRecord.status.in_([PublishStatus.SCHEDULED, PublishStatus.PENDING])
                )
            )
        )
        scheduled_this_week = week_scheduled_result.scalar() or 0
        
        # 最近失败
        failed_result = await db.execute(
            select(func.count(PublishRecord.id)).where(
                and_(
                    PublishRecord.status == PublishStatus.FAILED,
                    PublishRecord.updated_at >= now - timedelta(days=7)
                )
            )
        )
        failed_recent = failed_result.scalar() or 0
        
        # 今日已发布
        published_today_result = await db.execute(
            select(func.count(PublishRecord.id)).where(
                and_(
                    PublishRecord.status == PublishStatus.PUBLISHED,
                    PublishRecord.published_at >= today_start
                )
            )
        )
        published_today = published_today_result.scalar() or 0
        
        return QueueStats(
            total_pending=total_pending,
            scheduled_today=scheduled_today,
            scheduled_this_week=scheduled_this_week,
            failed_recent=failed_recent,
            published_today=published_today
        )
        
    except Exception as e:
        logger.error(f"获取队列统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@router.post("/schedule")
async def schedule_publish(
    request: SchedulePublishRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    定时发布文章
    """
    try:
        # 检查文章是否存在
        article_result = await db.execute(
            select(Article).where(Article.id == request.article_id)
        )
        article = article_result.scalar_one_or_none()
        
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")
        
        # 检查是否已存在发布计划
        existing_result = await db.execute(
            select(PublishRecord).where(
                and_(
                    PublishRecord.article_id == request.article_id,
                    PublishRecord.platform == PlatformType(request.platform),
                    PublishRecord.status.in_([
                        PublishStatus.PENDING,
                        PublishStatus.SCHEDULED
                    ])
                )
            )
        )
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            # 更新现有计划
            existing.scheduled_time = request.scheduled_time
            existing.status = PublishStatus.SCHEDULED
            existing.publish_options = request.publish_options
            await db.commit()
            
            return {
                "message": "发布计划已更新",
                "record_id": existing.id,
                "scheduled_time": request.scheduled_time.isoformat()
            }
        
        # 创建新的发布记录
        publish_record = PublishRecord(
            article_id=request.article_id,
            platform=PlatformType(request.platform),
            status=PublishStatus.SCHEDULED,
            scheduled_time=request.scheduled_time,
            publish_options=request.publish_options
        )
        
        db.add(publish_record)
        await db.commit()
        await db.refresh(publish_record)
        
        return {
            "message": "定时发布计划已创建",
            "record_id": publish_record.id,
            "scheduled_time": request.scheduled_time.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建定时发布计划失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建计划失败: {str(e)}")


@router.post("/queue/{record_id}/cancel")
async def cancel_publish(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    """取消发布计划"""
    try:
        result = await db.execute(
            select(PublishRecord).where(PublishRecord.id == record_id)
        )
        record = result.scalar_one_or_none()
        
        if not record:
            raise HTTPException(status_code=404, detail="发布记录不存在")
        
        if record.status not in [PublishStatus.PENDING, PublishStatus.SCHEDULED]:
            raise HTTPException(status_code=400, detail="只能取消待发布或已计划的任务")
        
        record.status = PublishStatus.CANCELLED
        await db.commit()
        
        return {"message": "发布计划已取消"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消发布计划失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"取消失败: {str(e)}")


@router.post("/queue/{record_id}/publish-now")
async def publish_now(
    record_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """立即发布"""
    try:
        result = await db.execute(
            select(PublishRecord).where(PublishRecord.id == record_id)
        )
        record = result.scalar_one_or_none()
        
        if not record:
            raise HTTPException(status_code=404, detail="发布记录不存在")
        
        if record.status not in [PublishStatus.PENDING, PublishStatus.SCHEDULED]:
            raise HTTPException(status_code=400, detail="该任务状态不允许立即发布")
        
        # 更新状态为发布中
        record.status = PublishStatus.PUBLISHING
        await db.commit()
        
        # 后台执行发布
        background_tasks.add_task(execute_publish_task, record_id)
        
        return {"message": "已开始发布", "record_id": record_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"立即发布失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"发布失败: {str(e)}")


async def execute_publish_task(record_id: int):
    """执行发布任务"""
    from ..core.database import async_session_maker
    
    async with async_session_maker() as db:
        try:
            result = await db.execute(
                select(PublishRecord).where(PublishRecord.id == record_id)
            )
            record = result.scalar_one_or_none()
            
            if not record or not record.article:
                logger.error(f"发布任务 {record_id}: 记录或文章不存在")
                return
            
            article = record.article
            
            # 根据平台执行发布
            if record.platform == PlatformType.WECHAT:
                # 发布到微信
                publish_result = await wechat_service.publish_draft(
                    title=article.title,
                    content=article.content,
                    digest=article.summary or article.content[:100] + "...",
                    cover_image_media_id=article.cover_image_media_id
                )
                
                if publish_result.get("success"):
                    record.status = PublishStatus.PUBLISHED
                    record.published_at = datetime.now()
                    record.platform_post_id = publish_result.get("draft_id")
                    
                    # 更新文章状态
                    article.status = ArticleStatus.PUBLISHED
                    article.wechat_draft_id = publish_result.get("draft_id")
                    article.wechat_publish_time = datetime.now()
                else:
                    record.status = PublishStatus.FAILED
                    record.error_message = publish_result.get("error", "发布失败")
            else:
                # 其他平台暂不支持
                record.status = PublishStatus.FAILED
                record.error_message = f"暂不支持平台: {record.platform.value}"
            
            await db.commit()
            logger.info(f"发布任务 {record_id} 完成，状态: {record.status.value}")
            
        except Exception as e:
            logger.error(f"执行发布任务 {record_id} 失败: {str(e)}")
            try:
                result = await db.execute(
                    select(PublishRecord).where(PublishRecord.id == record_id)
                )
                record = result.scalar_one_or_none()
                if record:
                    record.status = PublishStatus.FAILED
                    record.error_message = str(e)[:500]
                    await db.commit()
            except:
                pass


@router.get("/history")
async def get_publish_history(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """获取发布历史"""
    try:
        query = select(PublishRecord).options(
            selectinload(PublishRecord.article)
        ).order_by(desc(PublishRecord.created_at))
        
        conditions = []
        
        if platform:
            conditions.append(PublishRecord.platform == PlatformType(platform))
        
        if status:
            conditions.append(PublishRecord.status == PublishStatus(status))
        
        if start_date:
            conditions.append(PublishRecord.created_at >= start_date)
        
        if end_date:
            conditions.append(PublishRecord.created_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 获取总数
        count_result = await db.execute(
            select(func.count(PublishRecord.id)).where(and_(*conditions) if conditions else True)
        )
        total = count_result.scalar() or 0
        
        # 获取分页数据
        query = query.offset(offset).limit(limit)
        result = await db.execute(query)
        records = result.scalars().all()
        
        history = []
        for record in records:
            history.append({
                "id": record.id,
                "article_id": record.article_id,
                "article_title": record.article.title if record.article else "未知文章",
                "platform": record.platform.value,
                "status": record.status.value,
                "scheduled_time": record.scheduled_time.isoformat() if record.scheduled_time else None,
                "published_at": record.published_at.isoformat() if record.published_at else None,
                "error_message": record.error_message,
                "created_at": record.created_at.isoformat()
            })
        
        return {
            "total": total,
            "items": history,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"获取发布历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取历史失败: {str(e)}")


@router.post("/queue/process")
async def process_scheduled_publishes(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    处理到期的定时发布任务
    可以手动触发或由定时任务调用
    """
    try:
        now = datetime.now()
        
        # 查询到期的计划任务
        result = await db.execute(
            select(PublishRecord).where(
                and_(
                    PublishRecord.status == PublishStatus.SCHEDULED,
                    PublishRecord.scheduled_time <= now
                )
            )
        )
        scheduled_records = result.scalars().all()
        
        processed_count = 0
        for record in scheduled_records:
            record.status = PublishStatus.PUBLISHING
            background_tasks.add_task(execute_publish_task, record.id)
            processed_count += 1
        
        await db.commit()
        
        return {
            "message": f"已处理 {processed_count} 个定时发布任务",
            "processed_count": processed_count
        }
        
    except Exception as e:
        logger.error(f"处理定时发布任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

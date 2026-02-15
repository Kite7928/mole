"""
内容策略API - 日历、系列文章、选题库
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, extract, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from ..core.database import get_db
from ..core.logger import logger
from ..models.content_strategy import (
    PublishSchedule, ScheduleStatus, PublishPlatform,
    ArticleSeries, SeriesStatus,
    TopicIdea, IdeaStatus, IdeaPriority
)
from ..models.article import Article

router = APIRouter()


# ==================== 发布计划（日历）API ====================

class CreateScheduleRequest(BaseModel):
    """创建发布计划请求"""
    article_id: Optional[int] = Field(None, description="关联文章ID")
    title: str = Field(..., description="计划标题")
    description: Optional[str] = Field(None, description="描述")
    scheduled_date: str = Field(..., description="计划日期 (YYYY-MM-DD)")
    scheduled_time: str = Field(default="08:00", description="计划时间 (HH:MM)")
    platform: str = Field(default="wechat", description="发布平台")
    remind_before: int = Field(default=30, description="提前提醒分钟数")


class UpdateScheduleRequest(BaseModel):
    """更新发布计划请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_date: Optional[str] = None
    scheduled_time: Optional[str] = None
    status: Optional[str] = None
    platform: Optional[str] = None
    remind_before: Optional[int] = None


class ScheduleResponse(BaseModel):
    """发布计划响应"""
    id: int
    article_id: Optional[int]
    title: str
    description: Optional[str]
    scheduled_date: str
    scheduled_time: str
    status: str
    platform: str
    remind_before: int
    is_reminded: bool
    created_at: str
    article_title: Optional[str] = None


@router.get("/schedules", response_model=List[ScheduleResponse])
async def get_schedules(
    start_date: str,
    end_date: str,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取发布计划列表（日历视图数据）
    """
    try:
        # 解析日期
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        
        # 构建查询
        query = select(PublishSchedule).where(
            and_(
                PublishSchedule.scheduled_date >= start,
                PublishSchedule.scheduled_date < end
            )
        )
        
        if status:
            query = query.where(PublishSchedule.status == ScheduleStatus(status))
        
        query = query.order_by(PublishSchedule.scheduled_date)
        
        result = await db.execute(query)
        schedules = result.scalars().all()
        
        # 获取关联文章标题
        response_list = []
        for schedule in schedules:
            article_title = None
            if schedule.article_id:
                article_query = select(Article.title).where(Article.id == schedule.article_id)
                article_result = await db.execute(article_query)
                article_title = article_result.scalar_one_or_none()
            
            response_list.append(ScheduleResponse(
                id=schedule.id,
                article_id=schedule.article_id,
                title=schedule.title,
                description=schedule.description,
                scheduled_date=schedule.scheduled_date.strftime("%Y-%m-%d"),
                scheduled_time=schedule.scheduled_time,
                status=schedule.status.value,
                platform=schedule.platform.value,
                remind_before=schedule.remind_before,
                is_reminded=schedule.is_reminded,
                created_at=schedule.created_at.isoformat() if schedule.created_at else "",
                article_title=article_title
            ))
        
        return response_list
        
    except Exception as e:
        logger.error(f"获取发布计划失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.post("/schedules", response_model=ScheduleResponse)
async def create_schedule(
    request: CreateScheduleRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    创建发布计划
    """
    try:
        # 解析日期时间
        scheduled_datetime = datetime.strptime(
            f"{request.scheduled_date} {request.scheduled_time}",
            "%Y-%m-%d %H:%M"
        )
        
        schedule = PublishSchedule(
            article_id=request.article_id,
            title=request.title,
            description=request.description,
            scheduled_date=scheduled_datetime,
            scheduled_time=request.scheduled_time,
            platform=PublishPlatform(request.platform),
            remind_before=request.remind_before,
            status=ScheduleStatus.SCHEDULED
        )
        
        db.add(schedule)
        await db.commit()
        await db.refresh(schedule)
        
        return ScheduleResponse(
            id=schedule.id,
            article_id=schedule.article_id,
            title=schedule.title,
            description=schedule.description,
            scheduled_date=schedule.scheduled_date.strftime("%Y-%m-%d"),
            scheduled_time=schedule.scheduled_time,
            status=schedule.status.value,
            platform=schedule.platform.value,
            remind_before=schedule.remind_before,
            is_reminded=schedule.is_reminded,
            created_at=schedule.created_at.isoformat() if schedule.created_at else "",
            article_title=None
        )
        
    except Exception as e:
        logger.error(f"创建发布计划失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    request: UpdateScheduleRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    更新发布计划
    """
    try:
        query = select(PublishSchedule).where(PublishSchedule.id == schedule_id)
        result = await db.execute(query)
        schedule = result.scalar_one_or_none()
        
        if not schedule:
            raise HTTPException(status_code=404, detail="计划不存在")
        
        # 更新字段
        if request.title:
            schedule.title = request.title
        if request.description is not None:
            schedule.description = request.description
        if request.scheduled_date and request.scheduled_time:
            schedule.scheduled_date = datetime.strptime(
                f"{request.scheduled_date} {request.scheduled_time}",
                "%Y-%m-%d %H:%M"
            )
            schedule.scheduled_time = request.scheduled_time
        if request.status:
            schedule.status = ScheduleStatus(request.status)
        if request.platform:
            schedule.platform = PublishPlatform(request.platform)
        if request.remind_before is not None:
            schedule.remind_before = request.remind_before
        
        await db.commit()
        await db.refresh(schedule)
        
        # 获取关联文章标题
        article_title = None
        if schedule.article_id:
            article_query = select(Article.title).where(Article.id == schedule.article_id)
            article_result = await db.execute(article_query)
            article_title = article_result.scalar_one_or_none()
        
        return ScheduleResponse(
            id=schedule.id,
            article_id=schedule.article_id,
            title=schedule.title,
            description=schedule.description,
            scheduled_date=schedule.scheduled_date.strftime("%Y-%m-%d"),
            scheduled_time=schedule.scheduled_time,
            status=schedule.status.value,
            platform=schedule.platform.value,
            remind_before=schedule.remind_before,
            is_reminded=schedule.is_reminded,
            created_at=schedule.created_at.isoformat() if schedule.created_at else "",
            article_title=article_title
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新发布计划失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除发布计划
    """
    try:
        query = select(PublishSchedule).where(PublishSchedule.id == schedule_id)
        result = await db.execute(query)
        schedule = result.scalar_one_or_none()
        
        if not schedule:
            raise HTTPException(status_code=404, detail="计划不存在")
        
        await db.delete(schedule)
        await db.commit()
        
        return {"success": True, "message": "删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除发布计划失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/schedules/overview")
async def get_schedule_overview(db: AsyncSession = Depends(get_db)):
    """
    获取发布计划概览
    """
    try:
        now = datetime.now()
        week_later = now + timedelta(days=7)
        
        # 本周计划数
        week_query = select(func.count(PublishSchedule.id)).where(
            and_(
                PublishSchedule.scheduled_date >= now,
                PublishSchedule.scheduled_date < week_later,
                PublishSchedule.status == ScheduleStatus.SCHEDULED
            )
        )
        week_result = await db.execute(week_query)
        week_count = week_result.scalar() or 0
        
        # 待发布数
        pending_query = select(func.count(PublishSchedule.id)).where(
            PublishSchedule.status == ScheduleStatus.SCHEDULED
        )
        pending_result = await db.execute(pending_query)
        pending_count = pending_result.scalar() or 0
        
        # 今日发布数
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = today_start + timedelta(days=1)
        today_query = select(func.count(PublishSchedule.id)).where(
            and_(
                PublishSchedule.scheduled_date >= today_start,
                PublishSchedule.scheduled_date < today_end,
                PublishSchedule.status == ScheduleStatus.SCHEDULED
            )
        )
        today_result = await db.execute(today_query)
        today_count = today_result.scalar() or 0
        
        return {
            "week_scheduled": week_count,
            "total_pending": pending_count,
            "today_scheduled": today_count
        }
        
    except Exception as e:
        logger.error(f"获取计划概览失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


# ==================== 系列文章API ====================

class CreateSeriesRequest(BaseModel):
    """创建系列文章请求"""
    name: str = Field(..., description="系列名称")
    description: Optional[str] = Field(None, description="系列描述")
    cover_image_url: Optional[str] = Field(None, description="封面图URL")
    tags: Optional[List[str]] = Field(None, description="标签")
    category: Optional[str] = Field(None, description="分类")


class UpdateSeriesRequest(BaseModel):
    """更新系列文章请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    status: Optional[str] = None
    article_order: Optional[List[int]] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None


class SeriesResponse(BaseModel):
    """系列文章响应"""
    id: int
    name: str
    description: Optional[str]
    cover_image_url: Optional[str]
    status: str
    article_order: List[int]
    tags: List[str]
    category: Optional[str]
    total_articles: int
    total_views: int
    created_at: str
    updated_at: Optional[str]


@router.get("/series", response_model=List[SeriesResponse])
async def get_series_list(
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取系列文章列表
    """
    try:
        query = select(ArticleSeries).order_by(ArticleSeries.created_at.desc())
        
        if status:
            query = query.where(ArticleSeries.status == SeriesStatus(status))
        if category:
            query = query.where(ArticleSeries.category == category)
        
        result = await db.execute(query)
        series_list = result.scalars().all()
        
        response_list = []
        for series in series_list:
            response_list.append(SeriesResponse(
                id=series.id,
                name=series.name,
                description=series.description,
                cover_image_url=series.cover_image_url,
                status=series.status.value,
                article_order=series.get_article_order_list(),
                tags=series.get_tags_list(),
                category=series.category,
                total_articles=series.total_articles,
                total_views=series.total_views,
                created_at=series.created_at.isoformat() if series.created_at else "",
                updated_at=series.updated_at.isoformat() if series.updated_at else None
            ))
        
        return response_list
        
    except Exception as e:
        logger.error(f"获取系列列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/series/{series_id}", response_model=Dict[str, Any])
async def get_series_detail(
    series_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取系列文章详情（包含文章列表）
    """
    try:
        # 获取系列信息
        series_query = select(ArticleSeries).where(ArticleSeries.id == series_id)
        series_result = await db.execute(series_query)
        series = series_result.scalar_one_or_none()
        
        if not series:
            raise HTTPException(status_code=404, detail="系列不存在")
        
        # 获取系列中的文章
        article_ids = series.get_article_order_list()
        articles = []
        
        if article_ids:
            articles_query = select(Article).where(Article.id.in_(article_ids))
            articles_result = await db.execute(articles_query)
            articles_map = {a.id: a for a in articles_result.scalars().all()}
            
            # 按顺序排列
            for article_id in article_ids:
                if article_id in articles_map:
                    article = articles_map[article_id]
                    articles.append({
                        "id": article.id,
                        "title": article.title,
                        "status": article.status.value if article.status else "",
                        "view_count": article.view_count,
                        "like_count": article.like_count,
                        "cover_image_url": article.cover_image_url,
                        "created_at": article.created_at.isoformat() if article.created_at else ""
                    })
        
        return {
            "id": series.id,
            "name": series.name,
            "description": series.description,
            "cover_image_url": series.cover_image_url,
            "status": series.status.value,
            "article_order": article_ids,
            "tags": series.get_tags_list(),
            "category": series.category,
            "total_articles": series.total_articles,
            "total_views": series.total_views,
            "created_at": series.created_at.isoformat() if series.created_at else "",
            "articles": articles
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取系列详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.post("/series", response_model=SeriesResponse)
async def create_series(
    request: CreateSeriesRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    创建系列文章
    """
    try:
        series = ArticleSeries(
            name=request.name,
            description=request.description,
            cover_image_url=request.cover_image_url,
            category=request.category,
            status=SeriesStatus.DRAFT
        )
        
        if request.tags:
            series.set_tags_list(request.tags)
        
        db.add(series)
        await db.commit()
        await db.refresh(series)
        
        return SeriesResponse(
            id=series.id,
            name=series.name,
            description=series.description,
            cover_image_url=series.cover_image_url,
            status=series.status.value,
            article_order=series.get_article_order_list(),
            tags=series.get_tags_list(),
            category=series.category,
            total_articles=series.total_articles,
            total_views=series.total_views,
            created_at=series.created_at.isoformat() if series.created_at else "",
            updated_at=series.updated_at.isoformat() if series.updated_at else None
        )
        
    except Exception as e:
        logger.error(f"创建系列失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.put("/series/{series_id}", response_model=SeriesResponse)
async def update_series(
    series_id: int,
    request: UpdateSeriesRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    更新系列文章
    """
    try:
        query = select(ArticleSeries).where(ArticleSeries.id == series_id)
        result = await db.execute(query)
        series = result.scalar_one_or_none()
        
        if not series:
            raise HTTPException(status_code=404, detail="系列不存在")
        
        # 更新字段
        if request.name:
            series.name = request.name
        if request.description is not None:
            series.description = request.description
        if request.cover_image_url is not None:
            series.cover_image_url = request.cover_image_url
        if request.status:
            series.status = SeriesStatus(request.status)
        if request.article_order:
            series.set_article_order_list(request.article_order)
        if request.tags:
            series.set_tags_list(request.tags)
        if request.category:
            series.category = request.category
        
        await db.commit()
        await db.refresh(series)
        
        return SeriesResponse(
            id=series.id,
            name=series.name,
            description=series.description,
            cover_image_url=series.cover_image_url,
            status=series.status.value,
            article_order=series.get_article_order_list(),
            tags=series.get_tags_list(),
            category=series.category,
            total_articles=series.total_articles,
            total_views=series.total_views,
            created_at=series.created_at.isoformat() if series.created_at else "",
            updated_at=series.updated_at.isoformat() if series.updated_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新系列失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.delete("/series/{series_id}")
async def delete_series(
    series_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除系列文章
    """
    try:
        query = select(ArticleSeries).where(ArticleSeries.id == series_id)
        result = await db.execute(query)
        series = result.scalar_one_or_none()
        
        if not series:
            raise HTTPException(status_code=404, detail="系列不存在")
        
        await db.delete(series)
        await db.commit()
        
        return {"success": True, "message": "删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除系列失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/series/{series_id}/articles/{article_id}")
async def add_article_to_series(
    series_id: int,
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    添加文章到系列
    """
    try:
        # 验证系列和文章存在
        series_query = select(ArticleSeries).where(ArticleSeries.id == series_id)
        article_query = select(Article).where(Article.id == article_id)
        
        series_result = await db.execute(series_query)
        article_result = await db.execute(article_query)
        
        series = series_result.scalar_one_or_none()
        article = article_result.scalar_one_or_none()
        
        if not series:
            raise HTTPException(status_code=404, detail="系列不存在")
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")
        
        # 更新文章关联
        article.series_id = series_id
        
        # 更新系列的文章顺序
        article_order = series.get_article_order_list()
        if article_id not in article_order:
            article_order.append(article_id)
            series.set_article_order_list(article_order)
        
        await db.commit()
        
        return {"success": True, "message": "添加成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加文章到系列失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.delete("/series/{series_id}/articles/{article_id}")
async def remove_article_from_series(
    series_id: int,
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    从系列中移除文章
    """
    try:
        # 获取系列
        series_query = select(ArticleSeries).where(ArticleSeries.id == series_id)
        series_result = await db.execute(series_query)
        series = series_result.scalar_one_or_none()
        
        if not series:
            raise HTTPException(status_code=404, detail="系列不存在")
        
        # 获取文章
        article_query = select(Article).where(
            and_(Article.id == article_id, Article.series_id == series_id)
        )
        article_result = await db.execute(article_query)
        article = article_result.scalar_one_or_none()
        
        if article:
            article.series_id = None
        
        # 更新系列的文章顺序
        article_order = series.get_article_order_list()
        if article_id in article_order:
            article_order.remove(article_id)
            series.set_article_order_list(article_order)
        
        await db.commit()
        
        return {"success": True, "message": "移除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"从系列移除文章失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"移除失败: {str(e)}")


# ==================== 选题库API ====================

class CreateIdeaRequest(BaseModel):
    """创建选题请求"""
    title: str = Field(..., description="选题标题")
    description: Optional[str] = Field(None, description="详细描述")
    priority: str = Field(default="medium", description="优先级")
    source: Optional[str] = Field(None, description="来源")
    source_url: Optional[str] = Field(None, description="来源链接")
    tags: Optional[List[str]] = Field(None, description="标签")
    category: Optional[str] = Field(None, description="分类")
    estimated_word_count: Optional[int] = Field(None, description="预估字数")
    target_publish_date: Optional[str] = Field(None, description="目标发布日期")


class UpdateIdeaRequest(BaseModel):
    """更新选题请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    estimated_word_count: Optional[int] = None
    target_publish_date: Optional[str] = None
    notes: Optional[str] = None


class IdeaResponse(BaseModel):
    """选题响应"""
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    source: Optional[str]
    source_url: Optional[str]
    tags: List[str]
    category: Optional[str]
    estimated_word_count: Optional[int]
    target_publish_date: Optional[str]
    created_at: str
    updated_at: Optional[str]


@router.get("/ideas", response_model=List[IdeaResponse])
async def get_ideas(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    获取选题列表
    """
    try:
        query = select(TopicIdea).order_by(
            TopicIdea.created_at.desc()
        )
        
        if status:
            query = query.where(TopicIdea.status == IdeaStatus(status))
        if priority:
            query = query.where(TopicIdea.priority == IdeaPriority(priority))
        if category:
            query = query.where(TopicIdea.category == category)
        
        query = query.limit(limit)
        
        result = await db.execute(query)
        ideas = result.scalars().all()
        
        response_list = []
        for idea in ideas:
            response_list.append(IdeaResponse(
                id=idea.id,
                title=idea.title,
                description=idea.description,
                status=idea.status.value,
                priority=idea.priority.value,
                source=idea.source,
                source_url=idea.source_url,
                tags=idea.get_tags_list(),
                category=idea.category,
                estimated_word_count=idea.estimated_word_count,
                target_publish_date=idea.target_publish_date.strftime("%Y-%m-%d") if idea.target_publish_date else None,
                created_at=idea.created_at.isoformat() if idea.created_at else "",
                updated_at=idea.updated_at.isoformat() if idea.updated_at else None
            ))
        
        return response_list
        
    except Exception as e:
        logger.error(f"获取选题列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.post("/ideas", response_model=IdeaResponse)
async def create_idea(
    request: CreateIdeaRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    创建选题
    """
    try:
        idea = TopicIdea(
            title=request.title,
            description=request.description,
            priority=IdeaPriority(request.priority),
            source=request.source,
            source_url=request.source_url,
            category=request.category,
            estimated_word_count=request.estimated_word_count,
            status=IdeaStatus.NEW
        )
        
        if request.tags:
            idea.set_tags_list(request.tags)
        
        if request.target_publish_date:
            idea.target_publish_date = datetime.strptime(request.target_publish_date, "%Y-%m-%d")
        
        db.add(idea)
        await db.commit()
        await db.refresh(idea)
        
        return IdeaResponse(
            id=idea.id,
            title=idea.title,
            description=idea.description,
            status=idea.status.value,
            priority=idea.priority.value,
            source=idea.source,
            source_url=idea.source_url,
            tags=idea.get_tags_list(),
            category=idea.category,
            estimated_word_count=idea.estimated_word_count,
            target_publish_date=idea.target_publish_date.strftime("%Y-%m-%d") if idea.target_publish_date else None,
            created_at=idea.created_at.isoformat() if idea.created_at else "",
            updated_at=idea.updated_at.isoformat() if idea.updated_at else None
        )
        
    except Exception as e:
        logger.error(f"创建选题失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.put("/ideas/{idea_id}", response_model=IdeaResponse)
async def update_idea(
    idea_id: int,
    request: UpdateIdeaRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    更新选题
    """
    try:
        query = select(TopicIdea).where(TopicIdea.id == idea_id)
        result = await db.execute(query)
        idea = result.scalar_one_or_none()
        
        if not idea:
            raise HTTPException(status_code=404, detail="选题不存在")
        
        # 更新字段
        if request.title:
            idea.title = request.title
        if request.description is not None:
            idea.description = request.description
        if request.status:
            idea.status = IdeaStatus(request.status)
        if request.priority:
            idea.priority = IdeaPriority(request.priority)
        if request.source is not None:
            idea.source = request.source
        if request.source_url is not None:
            idea.source_url = request.source_url
        if request.tags:
            idea.set_tags_list(request.tags)
        if request.category:
            idea.category = request.category
        if request.estimated_word_count is not None:
            idea.estimated_word_count = request.estimated_word_count
        if request.target_publish_date:
            idea.target_publish_date = datetime.strptime(request.target_publish_date, "%Y-%m-%d")
        if request.notes is not None:
            idea.notes = request.notes
        
        await db.commit()
        await db.refresh(idea)
        
        return IdeaResponse(
            id=idea.id,
            title=idea.title,
            description=idea.description,
            status=idea.status.value,
            priority=idea.priority.value,
            source=idea.source,
            source_url=idea.source_url,
            tags=idea.get_tags_list(),
            category=idea.category,
            estimated_word_count=idea.estimated_word_count,
            target_publish_date=idea.target_publish_date.strftime("%Y-%m-%d") if idea.target_publish_date else None,
            created_at=idea.created_at.isoformat() if idea.created_at else "",
            updated_at=idea.updated_at.isoformat() if idea.updated_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新选题失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.delete("/ideas/{idea_id}")
async def delete_idea(
    idea_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除选题
    """
    try:
        query = select(TopicIdea).where(TopicIdea.id == idea_id)
        result = await db.execute(query)
        idea = result.scalar_one_or_none()
        
        if not idea:
            raise HTTPException(status_code=404, detail="选题不存在")
        
        await db.delete(idea)
        await db.commit()
        
        return {"success": True, "message": "删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除选题失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/ideas/stats")
async def get_ideas_stats(db: AsyncSession = Depends(get_db)):
    """
    获取选题库统计
    """
    try:
        # 各状态数量
        status_counts = {}
        for status in IdeaStatus:
            count_query = select(func.count(TopicIdea.id)).where(
                TopicIdea.status == status
            )
            count_result = await db.execute(count_query)
            status_counts[status.value] = count_result.scalar() or 0
        
        # 各优先级数量
        priority_counts = {}
        for priority in IdeaPriority:
            count_query = select(func.count(TopicIdea.id)).where(
                TopicIdea.priority == priority
            )
            count_result = await db.execute(count_query)
            priority_counts[priority.value] = count_result.scalar() or 0
        
        # 本月新增
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        month_query = select(func.count(TopicIdea.id)).where(
            TopicIdea.created_at >= month_start
        )
        month_result = await db.execute(month_query)
        month_count = month_result.scalar() or 0
        
        return {
            "total": sum(status_counts.values()),
            "by_status": status_counts,
            "by_priority": priority_counts,
            "new_this_month": month_count
        }
        
    except Exception as e:
        logger.error(f"获取选题统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")

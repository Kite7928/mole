"""
自定义RSS源管理API
支持用户添加、删除、修改、查询自定义RSS源
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from ..core.database import get_db
from ..core.logger import logger
from ..models.rss_source import RssSource as RssSourceModel
from ..services.news_fetcher import news_fetcher_service

router = APIRouter()


def normalize_rss_source_url(raw_url: str) -> str:
    """标准化 RSS 源地址，允许 http(s)、rsshub://、/route 三种格式。"""
    url = (raw_url or "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="RSS地址不能为空")

    if (
        url.startswith("http://")
        or url.startswith("https://")
        or url.startswith("rsshub://")
        or url.startswith("/")
    ):
        return url

    raise HTTPException(
        status_code=400,
        detail="RSS地址格式错误，请使用 http(s)://、rsshub:// 或 /route",
    )


# ============== Pydantic模型 ==============

class RssSourceCreate(BaseModel):
    """创建RSS源请求模型"""
    name: str = Field(..., min_length=1, max_length=200, description="源名称")
    url: str = Field(..., min_length=5, max_length=1000, description="RSS URL地址")
    description: Optional[str] = Field(None, max_length=500, description="源描述")
    category: Optional[str] = Field(None, max_length=100, description="分类")


class RssSourceUpdate(BaseModel):
    """更新RSS源请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="源名称")
    url: Optional[str] = Field(None, min_length=5, max_length=1000, description="RSS URL地址")
    description: Optional[str] = Field(None, max_length=500, description="源描述")
    category: Optional[str] = Field(None, max_length=100, description="分类")
    is_active: Optional[bool] = Field(None, description="是否启用")


class RssSourceResponse(BaseModel):
    """RSS源响应模型"""
    id: int
    name: str
    url: str
    description: Optional[str]
    category: Optional[str]
    is_active: bool
    is_official: bool
    fetch_count: int
    last_fetched_at: Optional[datetime]
    last_error: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class RssSourceListResponse(BaseModel):
    """RSS源列表响应"""
    success: bool
    count: int
    sources: List[RssSourceResponse]


class ImportPresetsRequest(BaseModel):
    """导入预设源请求模型"""
    include_official: bool = Field(True, description="是否导入6个官方RSS源")
    include_rsshub: bool = Field(True, description="是否导入4个RSSHub模板")
    reactivate_existing: bool = Field(True, description="若已存在则自动启用")


OFFICIAL_PRESET_SOURCES: List[Dict[str, Any]] = [
    {
        "name": "官方-IT之家",
        "url": "https://www.ithome.com/rss/",
        "description": "官方科技资讯源",
        "category": "科技",
        "is_official": True,
    },
    {
        "name": "官方-36氪",
        "url": "https://36kr.com/feed",
        "description": "官方商业科技资讯源",
        "category": "资讯",
        "is_official": True,
    },
    {
        "name": "官方-少数派",
        "url": "https://sspai.com/feed",
        "description": "官方效率与工具内容源",
        "category": "产品",
        "is_official": True,
    },
    {
        "name": "官方-虎嗅",
        "url": "https://www.huxiu.com/rss/0.xml",
        "description": "官方商业与产业观察源",
        "category": "创业",
        "is_official": True,
    },
    {
        "name": "官方-InfoQ",
        "url": "https://www.infoq.cn/feed",
        "description": "官方技术实践与架构内容源",
        "category": "技术",
        "is_official": True,
    },
    {
        "name": "官方-开源中国",
        "url": "https://www.oschina.net/news/rss",
        "description": "官方开源与开发者资讯源",
        "category": "开源",
        "is_official": True,
    },
]


RSSHUB_PRESET_SOURCES: List[Dict[str, Any]] = [
    {
        "name": "RSSHub-IT之家",
        "url": "/ithome/rss",
        "description": "RSSHub模板：IT之家",
        "category": "科技",
        "is_official": False,
    },
    {
        "name": "RSSHub-36氪快讯",
        "url": "/36kr/newsflashes",
        "description": "RSSHub模板：36氪快讯",
        "category": "资讯",
        "is_official": False,
    },
    {
        "name": "RSSHub-少数派",
        "url": "/sspai/index",
        "description": "RSSHub模板：少数派",
        "category": "产品",
        "is_official": False,
    },
    {
        "name": "RSSHub-开源中国",
        "url": "/oschina/news",
        "description": "RSSHub模板：开源中国",
        "category": "开源",
        "is_official": False,
    },
]


# ============== API路由 ==============

@router.get("/", response_model=RssSourceListResponse)
async def get_rss_sources(
    include_inactive: bool = False,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有自定义RSS源列表

    Args:
        include_inactive: 是否包含已禁用的源
        category: 按分类筛选
        db: 数据库会话

    Returns:
        RSS源列表
    """
    try:
        query = select(RssSourceModel)

        if not include_inactive:
            query = query.where(RssSourceModel.is_active == True)

        if category:
            query = query.where(RssSourceModel.category == category)

        query = query.order_by(desc(RssSourceModel.created_at))

        result = await db.execute(query)
        sources = result.scalars().all()

        # 将 SQLAlchemy 对象转换为 Pydantic 模型
        source_list = [RssSourceResponse.model_validate(source) for source in sources]

        return {
            "success": True,
            "count": len(source_list),
            "sources": source_list
        }

    except Exception as e:
        logger.error(f"获取RSS源列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取RSS源列表失败: {str(e)}")


@router.get("/categories", response_model=dict)
async def get_rss_source_categories(db: AsyncSession = Depends(get_db)):
    """
    获取所有RSS源分类列表

    Returns:
        分类列表
    """
    try:
        result = await db.execute(
            select(RssSourceModel.category)
            .where(RssSourceModel.category.isnot(None))
            .distinct()
        )
        categories = [cat for cat in result.scalars().all() if cat]

        return {
            "success": True,
            "categories": categories
        }

    except Exception as e:
        logger.error(f"获取RSS源分类失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取分类失败: {str(e)}")


@router.post("/", response_model=dict)
async def create_rss_source(
    source: RssSourceCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的自定义RSS源

    Args:
        source: RSS源信息
        db: 数据库会话

    Returns:
        创建结果
    """
    try:
        normalized_url = normalize_rss_source_url(source.url)

        # 检查URL是否已存在
        existing = await db.execute(
            select(RssSourceModel).where(RssSourceModel.url == normalized_url)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="该RSS URL已存在")

        # 创建新源
        new_source = RssSourceModel(
            name=source.name,
            url=normalized_url,
            description=source.description,
            category=source.category,
            is_active=True,
            is_official=False
        )

        db.add(new_source)
        await db.commit()
        await db.refresh(new_source)

        logger.info(f"创建RSS源成功: {source.name} ({source.url})")

        # 将 SQLAlchemy 对象转换为 Pydantic 模型
        source_data = RssSourceResponse.model_validate(new_source)

        return {
            "success": True,
            "message": "RSS源创建成功",
            "source": source_data
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"创建RSS源失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建RSS源失败: {str(e)}")


@router.post("/import-presets", response_model=dict)
async def import_preset_sources(
    request: Optional[ImportPresetsRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    一键导入预设RSS源（官方源 + RSSHub模板）

    Args:
        request: 导入参数
        db: 数据库会话

    Returns:
        导入统计结果
    """
    req = request or ImportPresetsRequest()

    try:
        preset_sources: List[Dict[str, Any]] = []
        if req.include_official:
            preset_sources.extend(OFFICIAL_PRESET_SOURCES)
        if req.include_rsshub:
            preset_sources.extend(RSSHUB_PRESET_SOURCES)

        if not preset_sources:
            raise HTTPException(status_code=400, detail="请至少选择一种预设类型")

        # 一次性查询并构建URL索引，保证导入幂等
        existing_result = await db.execute(select(RssSourceModel))
        existing_sources = existing_result.scalars().all()
        existing_by_url = {item.url: item for item in existing_sources}

        imported_names: List[str] = []
        skipped_names: List[str] = []
        reactivated_names: List[str] = []

        for preset in preset_sources:
            normalized_url = normalize_rss_source_url(str(preset.get("url", "")))
            existing = existing_by_url.get(normalized_url)

            if existing:
                skipped_names.append(existing.name)
                if req.reactivate_existing and not existing.is_active:
                    existing.is_active = True
                    existing.last_error = None
                    reactivated_names.append(existing.name)
                continue

            new_source = RssSourceModel(
                name=str(preset.get("name", "未命名源")),
                url=normalized_url,
                description=preset.get("description"),
                category=preset.get("category"),
                is_active=True,
                is_official=bool(preset.get("is_official", False)),
            )
            db.add(new_source)

            imported_names.append(new_source.name)
            existing_by_url[normalized_url] = new_source

        await db.commit()

        logger.info(
            "预设RSS源导入完成 "
            f"imported={len(imported_names)} skipped={len(skipped_names)} reactivated={len(reactivated_names)}"
        )

        return {
            "success": True,
            "message": f"导入完成：新增 {len(imported_names)}，跳过 {len(skipped_names)}，启用 {len(reactivated_names)}",
            "total_presets": len(preset_sources),
            "imported_count": len(imported_names),
            "skipped_count": len(skipped_names),
            "reactivated_count": len(reactivated_names),
            "imported_sources": imported_names,
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"导入预设RSS源失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导入预设RSS源失败: {str(e)}")


@router.get("/{source_id}", response_model=dict)
async def get_rss_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个RSS源详情

    Args:
        source_id: RSS源ID
        db: 数据库会话

    Returns:
        RSS源详情
    """
    try:
        result = await db.execute(
            select(RssSourceModel).where(RssSourceModel.id == source_id)
        )
        source = result.scalar_one_or_none()

        if not source:
            raise HTTPException(status_code=404, detail="RSS源不存在")

        # 将 SQLAlchemy 对象转换为 Pydantic 模型
        source_data = RssSourceResponse.model_validate(source)

        return {
            "success": True,
            "source": source_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取RSS源详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取RSS源详情失败: {str(e)}")


@router.put("/{source_id}", response_model=dict)
async def update_rss_source(
    source_id: int,
    source_update: RssSourceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新RSS源信息

    Args:
        source_id: RSS源ID
        source_update: 更新的字段
        db: 数据库会话

    Returns:
        更新结果
    """
    try:
        result = await db.execute(
            select(RssSourceModel).where(RssSourceModel.id == source_id)
        )
        source = result.scalar_one_or_none()

        if not source:
            raise HTTPException(status_code=404, detail="RSS源不存在")

        normalized_url = None
        if source_update.url is not None:
            normalized_url = normalize_rss_source_url(source_update.url)

        # 检查URL是否与其他源冲突
        if normalized_url and normalized_url != source.url:
            existing = await db.execute(
                select(RssSourceModel).where(
                    RssSourceModel.url == normalized_url,
                    RssSourceModel.id != source_id
                )
            )
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="该RSS URL已被其他源使用")

        # 更新字段
        update_data = source_update.model_dump(exclude_unset=True)
        if normalized_url is not None:
            update_data["url"] = normalized_url

        for field, value in update_data.items():
            setattr(source, field, value)

        await db.commit()
        await db.refresh(source)

        logger.info(f"更新RSS源成功: {source.name}")

        # 将 SQLAlchemy 对象转换为 Pydantic 模型
        source_data = RssSourceResponse.model_validate(source)

        return {
            "success": True,
            "message": "RSS源更新成功",
            "source": source_data
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"更新RSS源失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新RSS源失败: {str(e)}")


@router.delete("/{source_id}", response_model=dict)
async def delete_rss_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除RSS源

    Args:
        source_id: RSS源ID
        db: 数据库会话

    Returns:
        删除结果
    """
    try:
        result = await db.execute(
            select(RssSourceModel).where(RssSourceModel.id == source_id)
        )
        source = result.scalar_one_or_none()

        if not source:
            raise HTTPException(status_code=404, detail="RSS源不存在")

        await db.delete(source)
        await db.commit()

        logger.info(f"删除RSS源成功: {source.name}")

        return {
            "success": True,
            "message": "RSS源删除成功"
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"删除RSS源失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除RSS源失败: {str(e)}")


@router.post("/{source_id}/test", response_model=dict)
async def test_rss_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    测试RSS源是否可用

    Args:
        source_id: RSS源ID
        db: 数据库会话

    Returns:
        测试结果
    """
    try:
        result = await db.execute(
            select(RssSourceModel).where(RssSourceModel.id == source_id)
        )
        source = result.scalar_one_or_none()

        if not source:
            raise HTTPException(status_code=404, detail="RSS源不存在")

        # 测试抓取（复用统一重试与RSSHub路由解析）
        news_items = await news_fetcher_service.fetch_from_custom_source(source, limit=3)
        entries_count = len(news_items)

        # 更新抓取统计
        source.fetch_count += 1
        source.last_fetched_at = datetime.now()
        if entries_count == 0:
            source.last_error = "未获取到任何条目"
        else:
            source.last_error = None

        await db.commit()

        # 返回测试样本
        sample_entries = []
        for item in news_items[:3]:
            sample_entries.append({
                "title": item.title,
                "link": item.url,
                "published": item.published_at.isoformat() if item.published_at else ""
            })

        return {
            "success": entries_count > 0,
            "message": f"测试{'成功' if entries_count > 0 else '失败'}，获取到 {entries_count} 条记录",
            "entries_count": entries_count,
            "feed_title": source.name,
            "sample_entries": sample_entries
        }

    except HTTPException:
        raise
    except Exception as e:
        # 更新错误信息
        if 'source' in locals() and source:
            source.last_error = str(e)[:500]
            await db.commit()

        logger.error(f"测试RSS源失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试RSS源失败: {str(e)}")


@router.post("/{source_id}/fetch", response_model=dict)
async def fetch_from_rss_source(
    source_id: int,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    从指定自定义RSS源抓取新闻

    Args:
        source_id: RSS源ID
        limit: 抓取数量限制
        db: 数据库会话

    Returns:
        抓取结果
    """
    try:
        result = await db.execute(
            select(RssSourceModel).where(
                RssSourceModel.id == source_id,
                RssSourceModel.is_active == True
            )
        )
        source = result.scalar_one_or_none()

        if not source:
            raise HTTPException(status_code=404, detail="RSS源不存在或已禁用")

        # 抓取新闻
        from ..models.news import NewsItem
        news_items = await news_fetcher_service.fetch_from_custom_source(source, limit)

        # 保存到数据库
        saved_count = 0
        for item in news_items:
            # 检查是否已存在
            existing = await db.execute(
                select(NewsItem).where(NewsItem.url == item.url)
            )
            if not existing.scalar_one_or_none():
                db.add(item)
                saved_count += 1

        await db.commit()

        # 更新抓取统计
        source.fetch_count += 1
        source.last_fetched_at = datetime.now()
        source.last_error = None
        await db.commit()

        logger.info(f"从RSS源 {source.name} 抓取了 {saved_count} 条新闻")

        return {
            "success": True,
            "message": f"成功抓取 {saved_count} 条新闻",
            "count": saved_count,
            "source_name": source.name
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()

        # 更新错误信息
        if 'source' in locals() and source:
            source.last_error = str(e)[:500]
            await db.commit()

        logger.error(f"从RSS源抓取新闻失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"抓取失败: {str(e)}")

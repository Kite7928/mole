"""
文章管理API路由 - 简化版
支持获取文章列表、创建文章、更新文章
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy import or_
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from ..core.database import get_db
from ..core.logger import logger
from ..models.article import Article, ArticleStatus
from ..services.image_generation_service import image_generation_service

router = APIRouter()


async def _ensure_article_series_columns(db: AsyncSession) -> None:
    """兼容旧数据库结构：确保系列与质检字段存在"""
    try:
        result = await db.execute(text("PRAGMA table_info(articles)"))
        columns = {row[1] for row in result.fetchall()}
        if "series_id" not in columns:
            await db.execute(text("ALTER TABLE articles ADD COLUMN series_id INTEGER"))
        if "series_order" not in columns:
            await db.execute(text("ALTER TABLE articles ADD COLUMN series_order INTEGER DEFAULT 0"))
        if "quality_check_status" not in columns:
            await db.execute(text("ALTER TABLE articles ADD COLUMN quality_check_status VARCHAR(20) DEFAULT 'unchecked'"))
        if "quality_check_data" not in columns:
            await db.execute(text("ALTER TABLE articles ADD COLUMN quality_check_data TEXT"))
        if "quality_checked_at" not in columns:
            await db.execute(text("ALTER TABLE articles ADD COLUMN quality_checked_at DATETIME"))
        await db.commit()
    except Exception:
        await db.rollback()


class ArticleResponse(BaseModel):
    """文章响应模型"""
    id: int
    title: str
    summary: Optional[str]
    content: str
    status: str
    source_topic: Optional[str]
    source_url: Optional[str]
    wechat_draft_id: Optional[str]
    quality_score: Optional[float]
    cover_image_url: Optional[str]
    cover_image_media_id: Optional[str]
    quality_check_status: str = "unchecked"
    quality_check_data: Optional[Dict[str, Any]] = None
    quality_checked_at: Optional[datetime] = None
    tags: Optional[List[str]] = []
    view_count: int = 0
    like_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

    @classmethod
    def from_article(cls, article: Article) -> "ArticleResponse":
        """从 Article 模型创建响应"""
        # 处理封面图片URL - 如果是相对路径,转换为完整URL
        cover_image_url = article.cover_image_url
        if cover_image_url and not cover_image_url.startswith(('http://', 'https://')):
            # 统一处理路径分隔符（Windows 使用 \，Unix 使用 /）
            cover_image_url = cover_image_url.replace('\\', '/')
            # 移除开头的 backend/ 或 uploads/ 前缀
            if cover_image_url.startswith('backend/'):
                cover_image_url = cover_image_url[8:]  # 移除 "backend/"
            if cover_image_url.startswith('uploads/'):
                cover_image_url = cover_image_url[8:]  # 移除 "uploads/"
            # 添加后端服务器地址
            from ..core.config import settings
            cover_image_url = f"http://localhost:{settings.PORT}/uploads/{cover_image_url}"

        return cls(
            id=article.id,
            title=article.title,
            summary=article.summary,
            content=article.content,
            status=article.status.value if isinstance(article.status, ArticleStatus) else article.status,
            source_topic=article.source_topic,
            source_url=article.source_url,
            wechat_draft_id=article.wechat_draft_id,
            quality_score=article.quality_score,
            cover_image_url=cover_image_url,
            cover_image_media_id=article.cover_image_media_id,
            quality_check_status=article.quality_check_status or "unchecked",
            quality_check_data=article.get_quality_check_data(),
            quality_checked_at=article.quality_checked_at,
            tags=article.get_tags_list(),
            view_count=article.view_count,
            like_count=article.like_count,
            created_at=article.created_at,
            updated_at=article.updated_at,
        )


class CreateArticleRequest(BaseModel):
    """创建文章请求"""
    title: Optional[str] = Field(None, description="文章标题")
    content: Optional[str] = Field(None, description="文章内容")
    topic: Optional[str] = Field(None, description="文章主题（兼容旧接口）")
    style: Optional[str] = Field(default="professional", description="写作风格（兼容旧接口）")
    length: Optional[str] = Field(default="medium", description="文章长度（兼容旧接口）")
    enable_research: Optional[bool] = Field(default=False, description="是否启用研究（兼容旧接口）")
    generate_cover: Optional[bool] = Field(default=False, description="是否生成封面（兼容旧接口）")
    ai_model: Optional[str] = Field(default=None, description="AI模型（兼容旧接口）")
    summary: Optional[str] = Field(None, description="文章摘要")
    source_topic: Optional[str] = Field(None, description="来源主题")
    source_url: Optional[str] = Field(None, description="来源链接")
    status: str = Field(default="draft", description="文章状态")
    tags: Optional[List[str]] = Field(default=None, description="文章标签列表")
    quality_check_status: Optional[str] = Field(default="unchecked", description="质检状态")
    quality_check_data: Optional[Dict[str, Any]] = Field(default=None, description="质检详情")
    quality_checked_at: Optional[datetime] = Field(default=None, description="质检时间")
    # 图片生成参数
    generate_cover_image: bool = Field(default=True, description="是否生成封面图")
    image_style: str = Field(default="professional", description="图片风格 (professional/creative/minimal/vibrant)")
    image_provider: str = Field(default="dalle", description="图片生成提供商 (dalle/midjourney/stable-diffusion)")


class UpdateArticleRequest(BaseModel):
    """更新文章请求"""
    title: Optional[str] = Field(None, description="文章标题")
    content: Optional[str] = Field(None, description="文章内容")
    summary: Optional[str] = Field(None, description="文章摘要")
    status: Optional[str] = Field(None, description="文章状态")
    wechat_draft_id: Optional[str] = Field(None, description="微信草稿ID")
    quality_score: Optional[float] = Field(None, description="质量评分")
    cover_image_url: Optional[str] = Field(None, description="封面图URL")
    tags: Optional[List[str]] = Field(None, description="文章标签列表")
    quality_check_status: Optional[str] = Field(None, description="质检状态")
    quality_check_data: Optional[Dict[str, Any]] = Field(None, description="质检详情")
    quality_checked_at: Optional[datetime] = Field(None, description="质检时间")
    # 图片生成参数
    regenerate_cover_image: bool = Field(default=False, description="是否重新生成封面图")
    image_style: str = Field(default="professional", description="图片风格")
    image_provider: str = Field(default="dalle", description="图片生成提供商")


@router.get("/", response_model=List[ArticleResponse])
async def get_articles(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    search: Optional[str] = None,
    quality_check_status: Optional[str] = None,
    sort_field: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db)
):
    """
    获取文章列表

    Args:
        skip: 跳过数量
        limit: 返回数量
        status: 状态筛选
        search: 关键词（标题/摘要/来源主题）
        sort_field: 排序字段 (created_at, updated_at, like_count)
        sort_order: 排序方向 (asc, desc)
        db: 数据库会话

    Returns:
        文章列表
    """
    try:
        await _ensure_article_series_columns(db)
        # 验证排序字段是否在白名单中
        valid_sort_fields = {"created_at", "updated_at", "like_count"}
        if sort_field not in valid_sort_fields:
            sort_field = "created_at"

        # 验证排序方向
        if sort_order not in {"asc", "desc"}:
            sort_order = "desc"

        # 根据排序字段构建排序逻辑
        sort_column = getattr(Article, sort_field)
        if sort_order == "asc":
            query = select(Article).order_by(sort_column.asc())
        else:
            query = select(Article).order_by(sort_column.desc())

        if status:
            query = query.where(Article.status == status)

        if search:
            keyword = search.strip()[:100]
            if keyword:
                pattern = f"%{keyword}%"
                query = query.where(
                    or_(
                        Article.title.ilike(pattern),
                        Article.summary.ilike(pattern),
                        Article.source_topic.ilike(pattern),
                    )
                )

        if quality_check_status:
            valid_quality_status = {"unchecked", "pass", "warning", "blocked"}
            if quality_check_status in valid_quality_status:
                query = query.where(Article.quality_check_status == quality_check_status)

        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        articles = result.scalars().all()

        return [ArticleResponse.from_article(article) for article in articles]

    except Exception as e:
        logger.error(f"获取文章列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取文章列表失败: {str(e)}")


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)):
    """
    获取文章详情
    
    Args:
        article_id: 文章ID
        db: 数据库会话
    
    Returns:
        文章详情
    """
    try:
        query = select(Article).where(Article.id == article_id)
        result = await db.execute(query)
        article = result.scalar_one_or_none()
        
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")
        
        return ArticleResponse.from_article(article)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文章详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取文章详情失败: {str(e)}")


@router.post("/", response_model=ArticleResponse)
async def create_article(
    request: CreateArticleRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    创建文章（支持自动生成封面图）

    Args:
        request: 创建文章请求
        db: 数据库会话

    Returns:
        创建的文章
    """
    try:
        await _ensure_article_series_columns(db)
        resolved_title = (request.title or request.topic or "未命名文章").strip()
        resolved_content = (request.content or f"{request.topic or resolved_title}\n\n这是一篇自动创建的文章草稿。")

        logger.info(f"创建文章，标题: {resolved_title}")

        article = Article(
            title=resolved_title,
            content=resolved_content,
            summary=request.summary,
            source_topic=request.source_topic,
            source_url=request.source_url,
            status=ArticleStatus(request.status),
            quality_check_status=request.quality_check_status or "unchecked",
            quality_checked_at=request.quality_checked_at,
        )

        if request.quality_check_data is not None:
            article.set_quality_check_data(request.quality_check_data)

        # 设置标签
        if request.tags:
            cleaned_tags = [tag.strip()[:50] for tag in request.tags if tag.strip()]
            cleaned_tags = list(dict.fromkeys(cleaned_tags))[:10]
            article.set_tags_list(cleaned_tags)

        db.add(article)
        await db.commit()
        await db.refresh(article)

        # 生成封面图
        if request.generate_cover_image or bool(request.generate_cover):
            try:
                logger.info(f"开始生成封面图，主题: {request.source_topic or request.title}, 提供商: {request.image_provider}, 风格: {request.image_style}")
                topic = request.source_topic or request.title
                cover_image = await image_generation_service.generate_article_cover(
                    topic=topic,
                    style=request.image_style,
                    provider=request.image_provider
                )

                if cover_image and cover_image.get("url"):
                    article.cover_image_url = cover_image["url"]
                    await db.commit()
                    await db.refresh(article)
                    logger.info(f"封面图生成成功: {article.cover_image_url}")
                else:
                    logger.warning(f"封面图生成失败，返回结果: {cover_image}")

            except Exception as img_error:
                logger.exception(f"生成封面图失败: {str(img_error)}")
                # 不影响文章创建，只记录错误

        logger.info(f"文章创建成功，ID: {article.id}")
        return ArticleResponse.from_article(article)

    except Exception as e:
        logger.error(f"创建文章失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"创建文章失败: {str(e)}")


@router.post("/titles/generate", response_model=List[Dict[str, Any]])
async def generate_titles_compat(request: Dict[str, Any]):
    """兼容旧版接口：生成标题"""
    topic = request.get("topic", "未命名主题")
    count = int(request.get("count", 5))
    base_suggestions = [
        {"title": f"{topic}：你可能忽略的3个关键点", "click_rate": 82.0},
        {"title": f"深度解读：{topic}正在改变什么", "click_rate": 79.0},
        {"title": f"看完就会：{topic}实战指南", "click_rate": 76.0},
    ]
    suggestions = []
    for idx in range(max(1, min(count, 10))):
        if idx < len(base_suggestions):
            item = dict(base_suggestions[idx])
            item["predicted_click_rate"] = item["click_rate"]
            suggestions.append(item)
        else:
            suggestions.append({
                "title": f"{topic}：第{idx + 1}个高转化写法",
                "click_rate": max(60.0, 75.0 - idx),
                "predicted_click_rate": max(60.0, 75.0 - idx),
            })
    return suggestions


@router.post("/content/generate", response_model=Dict[str, Any])
async def generate_content_compat(request: Dict[str, Any]):
    """兼容旧版接口：生成正文"""
    topic = request.get("topic", "未命名主题")
    title = request.get("title", f"{topic}分析")
    content = f"# {title}\n\n围绕“{topic}”的正文草稿。\n\n## 观点\n- 要点1\n- 要点2\n\n## 结论\n建议结合账号定位继续完善。"
    return {
        "content": content,
        "summary": f"围绕{topic}的内容草稿",
        "tags": ["自媒体", "创作", "运营"]
    }


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    request: UpdateArticleRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    更新文章（支持更新封面图）

    Args:
        article_id: 文章ID
        request: 更新文章请求
        db: 数据库会话

    Returns:
        更新后的文章
    """
    try:
        logger.info(f"更新文章，ID: {article_id}")

        query = select(Article).where(Article.id == article_id)
        result = await db.execute(query)
        article = result.scalar_one_or_none()

        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")

        # 更新字段
        if request.title is not None:
            article.title = request.title
        if request.content is not None:
            article.content = request.content
        if request.summary is not None:
            article.summary = request.summary
        if request.status is not None:
            article.status = ArticleStatus(request.status)
        if request.wechat_draft_id is not None:
            article.wechat_draft_id = request.wechat_draft_id
        if request.quality_score is not None:
            article.quality_score = request.quality_score
        if request.cover_image_url is not None:
            article.cover_image_url = request.cover_image_url
        if request.tags is not None:
            cleaned_tags = [tag.strip()[:50] for tag in request.tags if tag.strip()]
            cleaned_tags = list(dict.fromkeys(cleaned_tags))[:10]
            article.set_tags_list(cleaned_tags)
        if request.quality_check_status is not None:
            article.quality_check_status = request.quality_check_status
        if request.quality_check_data is not None:
            article.set_quality_check_data(request.quality_check_data)
        if request.quality_checked_at is not None:
            article.quality_checked_at = request.quality_checked_at

        # 重新生成封面图
        if request.regenerate_cover_image:
            try:
                logger.info(f"开始重新生成封面图，文章ID: {article_id}")
                topic = article.source_topic or article.title
                cover_image = await image_generation_service.generate_article_cover(
                    topic=topic,
                    style=request.image_style,
                    provider=request.image_provider
                )

                if cover_image and cover_image.get("url"):
                    article.cover_image_url = cover_image["url"]
                    logger.info(f"封面图重新生成成功: {article.cover_image_url}")
                else:
                    logger.warning("封面图重新生成失败，未返回有效的图片URL")

            except Exception as img_error:
                logger.error(f"重新生成封面图失败: {str(img_error)}")
                # 不影响文章更新，只记录错误

        await db.commit()
        await db.refresh(article)

        logger.info(f"文章更新成功，ID: {article_id}")
        return ArticleResponse.from_article(article)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新文章失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新文章失败: {str(e)}")


@router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除文章

    Args:
        article_id: 文章ID
        db: 数据库会话

    Returns:
        删除结果
    """
    try:
        logger.info(f"删除文章，ID: {article_id}")

        # 查询文章
        query = select(Article).where(Article.id == article_id)
        result = await db.execute(query)
        article = result.scalar_one_or_none()

        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")

        # 删除文章
        await db.delete(article)
        await db.commit()

        logger.info(f"文章删除成功，ID: {article_id}")
        return {"success": True, "message": "文章删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文章失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除文章失败: {str(e)}")


@router.post("/{article_id}/copy", response_model=ArticleResponse)
async def copy_article(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    复制文章

    Args:
        article_id: 文章ID
        db: 数据库会话

    Returns:
        复制后的新文章
    """
    try:
        logger.info(f"复制文章，ID: {article_id}")

        # 查询原文章
        query = select(Article).where(Article.id == article_id)
        result = await db.execute(query)
        original_article = result.scalar_one_or_none()

        if not original_article:
            raise HTTPException(status_code=404, detail="文章不存在")

        # 创建新文章副本
        new_article = Article(
            title=f"{original_article.title} (副本)",
            content=original_article.content,
            summary=original_article.summary,
            source_topic=original_article.source_topic,
            source_url=original_article.source_url,
            status=ArticleStatus.DRAFT,  # 副本默认为草稿状态
            quality_score=original_article.quality_score,
            quality_check_status="unchecked",
            quality_check_data=None,
            quality_checked_at=None,
            cover_image_url=original_article.cover_image_url,
            tags=original_article.tags
        )

        db.add(new_article)
        await db.commit()
        await db.refresh(new_article)

        logger.info(f"文章复制成功，原ID: {article_id}, 新ID: {new_article.id}")
        return ArticleResponse.from_article(new_article)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"复制文章失败: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"复制文章失败: {str(e)}")


class GenerateCoverImageRequest(BaseModel):
    """生成封面图请求"""
    topic: str = Field(..., description="文章主题")
    style: str = Field(default="professional", description="图片风格")
    provider: str = Field(default="dalle", description="图片生成提供商")


class GenerateBatchCoverImagesRequest(BaseModel):
    """批量生成封面图请求"""
    topic: str = Field(..., description="文章主题")
    style: str = Field(default="professional", description="图片风格")
    provider: str = Field(default="dalle", description="图片生成提供商")
    n: int = Field(default=3, ge=1, le=5, description="生成数量（1-5）")


@router.post("/generate-batch-covers", response_model=List[Dict[str, Any]])
async def generate_batch_cover_images(
    request: GenerateBatchCoverImagesRequest
):
    """
    批量生成封面图

    Args:
        request: 批量生成请求

    Returns:
        生成的封面图列表
    """
    try:
        logger.info(f"批量生成封面图，主题: {request.topic}, 数量: {request.n}")

        # 批量生成封面图
        images = await image_generation_service.generate_batch_article_covers(
            topic=request.topic,
            style=request.style,
            provider=request.provider,
            n=request.n
        )

        return images

    except Exception as e:
        logger.error(f"批量生成封面图失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量生成失败: {str(e)}")


@router.post("/{article_id}/generate-cover", response_model=Dict[str, Any])
async def generate_article_cover_image(
    article_id: int,
    request: GenerateCoverImageRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    为文章生成封面图

    Args:
        article_id: 文章ID
        request: 生成封面图请求
        db: 数据库会话

    Returns:
        生成的封面图信息
    """
    try:
        logger.info(f"为文章生成封面图，ID: {article_id}")

        # 获取文章
        query = select(Article).where(Article.id == article_id)
        result = await db.execute(query)
        article = result.scalar_one_or_none()

        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")

        # 生成封面图
        cover_image = await image_generation_service.generate_article_cover(
            topic=request.topic,
            style=request.style,
            provider=request.provider
        )

        if not cover_image or not cover_image.get("url"):
            raise HTTPException(status_code=500, detail="生成封面图失败")

        # 处理封面图 URL - 如果是远程 URL，下载到本地
        image_url = cover_image["url"]
        if image_url.startswith("http"):
            # 下载远程图片
            import httpx
            from pathlib import Path
            import uuid
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url, timeout=60.0)
                    response.raise_for_status()
                    
                    # 保存到本地
                    upload_dir = Path("uploads")
                    upload_dir.mkdir(parents=True, exist_ok=True)
                    
                    file_ext = ".png" if ".png" in image_url else ".jpg"
                    local_filename = f"cover_{uuid.uuid4().hex[:16]}{file_ext}"
                    local_path = upload_dir / local_filename
                    
                    with open(local_path, "wb") as f:
                        f.write(response.content)
                    
                    image_url = f"uploads/{local_filename}"
                    logger.info(f"远程图片已下载到本地: {image_url}")
            except Exception as e:
                logger.warning(f"下载远程图片失败，使用原URL: {e}")
        
        # 更新文章
        article.cover_image_url = image_url
        await db.commit()
        await db.refresh(article)

        logger.info(f"封面图生成成功: {article.cover_image_url}")

        return {
            "article_id": article_id,
            "cover_image_url": article.cover_image_url,
            "image_style": request.style,
            "image_provider": request.provider,
            "prompt": cover_image.get("prompt")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成封面图失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成封面图失败: {str(e)}")




# ========== AI生成选题大纲功能 ==========



from ..services.unified_ai_service import unified_ai_service





class GenerateOutlinesRequest(BaseModel):

    """生成大纲请求"""

    topic: str = Field(..., description="热点主题")

    source_url: Optional[str] = Field(None, description="来源链接")





@router.post("/generate-outlines", response_model=Dict[str, Any])
async def generate_article_outlines(
    request: GenerateOutlinesRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    AI生成3种差异化文章大纲
    """
    try:
        logger.info(f"生成文章大纲，主题: {request.topic}")

        # 从数据库获取配置
        from ..models.config import AppConfig
        query = select(AppConfig).order_by(AppConfig.id.desc())
        result = await db.execute(query)
        config = result.scalar_one_or_none()

        if not config or not config.api_key:
            return {
                "success": False,
                "topic": request.topic,
                "outlines": [],
                "error": "请先在设置中配置AI API Key"
            }

        # 创建OpenAI客户端
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )

        # 调用AI生成大纲
        prompt = f"""请为主题「{request.topic}」生成3种差异化的文章大纲。

要求：
1. 每种大纲从不同角度切入（如：技术解读、行业影响、实用指南）
2. 每种大纲包含：角度名称、核心观点、3-4个章节要点
3. 用中文JSON格式返回

返回格式：
{{
  "outlines": [
    {{
      "angle": "角度名称",
      "title": "建议标题",
      "points": ["要点1", "要点2", "要点3"]
    }}
  ]
}}"""

        response = await client.chat.completions.create(
            model=config.model,
            messages=[
                {"role": "system", "content": "你是一位资深科技自媒体主编"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )

        content = response.choices[0].message.content

        # 解析JSON响应
        import json
        import re

        # 提取JSON部分
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)

        data = json.loads(content)
        outlines = data.get("outlines", [])

        # 关闭客户端
        await client.close()

        return {
            "success": True,
            "topic": request.topic,
            "outlines": outlines,
            "ai_provider": config.ai_provider
        }

    except Exception as e:
        logger.error(f"生成大纲失败: {str(e)}")
        return {
            "success": False,
            "topic": request.topic,
            "outlines": [],
            "error": str(e)
        }


# ============ 批量操作API ============

class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    article_ids: List[int] = Field(..., description="要删除的文章ID列表")


class BatchUpdateStatusRequest(BaseModel):
    """批量更新状态请求"""
    article_ids: List[int] = Field(..., description="要更新的文章ID列表")
    status: str = Field(..., description="新状态")


class BatchPublishRequest(BaseModel):
    """批量发布请求"""
    article_ids: List[int] = Field(..., description="要发布的文章ID列表")


class BatchOperationResponse(BaseModel):
    """批量操作响应"""
    success: bool
    message: str
    processed: int
    failed: int
    details: List[Dict[str, Any]]


@router.post("/batch/delete", response_model=BatchOperationResponse)
async def batch_delete_articles(
    request: BatchDeleteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    批量删除文章
    
    Args:
        request: 批量删除请求
        db: 数据库会话
    
    Returns:
        操作结果
    """
    processed = 0
    failed = 0
    details = []
    
    for article_id in request.article_ids:
        try:
            query = select(Article).where(Article.id == article_id)
            result = await db.execute(query)
            article = result.scalar_one_or_none()
            
            if article:
                await db.delete(article)
                processed += 1
                details.append({"id": article_id, "status": "deleted"})
            else:
                failed += 1
                details.append({"id": article_id, "status": "not_found"})
        except Exception as e:
            failed += 1
            details.append({"id": article_id, "status": "error", "error": str(e)})
    
    await db.commit()
    
    return BatchOperationResponse(
        success=failed == 0,
        message=f"批量删除完成：成功 {processed} 个，失败 {failed} 个",
        processed=processed,
        failed=failed,
        details=details
    )


@router.post("/batch/update-status", response_model=BatchOperationResponse)
async def batch_update_status(
    request: BatchUpdateStatusRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    批量更新文章状态
    
    Args:
        request: 批量更新请求
        db: 数据库会话
    
    Returns:
        操作结果
    """
    processed = 0
    failed = 0
    details = []
    
    try:
        # 验证状态值
        if request.status not in [s.value for s in ArticleStatus]:
            raise HTTPException(status_code=400, detail=f"无效的状态值: {request.status}")
        
        for article_id in request.article_ids:
            try:
                query = select(Article).where(Article.id == article_id)
                result = await db.execute(query)
                article = result.scalar_one_or_none()
                
                if article:
                    article.status = ArticleStatus(request.status)
                    processed += 1
                    details.append({"id": article_id, "status": "updated"})
                else:
                    failed += 1
                    details.append({"id": article_id, "status": "not_found"})
            except Exception as e:
                failed += 1
                details.append({"id": article_id, "status": "error", "error": str(e)})
        
        await db.commit()
        
        return BatchOperationResponse(
            success=failed == 0,
            message=f"批量更新完成：成功 {processed} 个，失败 {failed} 个",
            processed=processed,
            failed=failed,
            details=details
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"批量更新失败: {str(e)}")


@router.post("/batch/publish-wechat", response_model=BatchOperationResponse)
async def batch_publish_wechat(
    request: BatchPublishRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    批量发布到微信草稿箱
    
    Args:
        request: 批量发布请求
        db: 数据库会话
    
    Returns:
        操作结果
    """
    from ..services.wechat_service import wechat_service
    
    processed = 0
    failed = 0
    details = []
    
    for article_id in request.article_ids:
        try:
            query = select(Article).where(Article.id == article_id)
            result = await db.execute(query)
            article = result.scalar_one_or_none()
            
            if not article:
                failed += 1
                details.append({"id": article_id, "status": "not_found"})
                continue
            
            # 发布到微信
            result = await wechat_service.publish_draft(
                title=article.title,
                content=article.content,
                cover_image_url=article.cover_image_url
            )
            
            if result.get("success"):
                article.wechat_draft_id = result.get("draft_id")
                article.status = ArticleStatus.PUBLISHED
                processed += 1
                details.append({
                    "id": article_id,
                    "status": "published",
                    "draft_id": result.get("draft_id")
                })
            else:
                failed += 1
                details.append({
                    "id": article_id,
                    "status": "failed",
                    "error": result.get("error", "发布失败")
                })
        except Exception as e:
            failed += 1
            details.append({"id": article_id, "status": "error", "error": str(e)})
    
    await db.commit()
    
    return BatchOperationResponse(
        success=failed == 0,
        message=f"批量发布完成：成功 {processed} 个，失败 {failed} 个",
        processed=processed,
        failed=failed,
        details=details
    )


@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_article_stats(db: AsyncSession = Depends(get_db)):
    """
    获取文章统计概览
    
    Returns:
        统计数据
    """
    try:
        # 总文章数
        from sqlalchemy import func
        total_query = select(func.count(Article.id))
        total_result = await db.execute(total_query)
        total = total_result.scalar()
        
        # 各状态统计
        status_counts = {}
        for status in ArticleStatus:
            count_query = select(func.count(Article.id)).where(Article.status == status)
            count_result = await db.execute(count_query)
            status_counts[status.value] = count_result.scalar()
        
        # 最近7天创建的文章数
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_query = select(func.count(Article.id)).where(Article.created_at >= week_ago)
        recent_result = await db.execute(recent_query)
        recent = recent_result.scalar()
        
        return {
            "success": True,
            "total": total,
            "status_counts": status_counts,
            "recent_7days": recent,
            "published": status_counts.get("published", 0),
            "draft": status_counts.get("draft", 0),
            "ready": status_counts.get("ready", 0)
        }
    except Exception as e:
        logger.error(f"获取统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


# ============ 标签管理API ============

class UpdateTagsRequest(BaseModel):
    """更新标签请求"""
    tags: List[str] = Field(..., description="标签列表")


class AddTagRequest(BaseModel):
    """添加标签请求"""
    tag: str = Field(..., description="标签名称", min_length=1, max_length=50)


class RemoveTagRequest(BaseModel):
    """移除标签请求"""
    tag: str = Field(..., description="要移除的标签")


@router.get("/{article_id}/tags")
async def get_article_tags(article_id: int, db: AsyncSession = Depends(get_db)):
    """
    获取文章标签
    
    Args:
        article_id: 文章ID
        db: 数据库会话
    
    Returns:
        标签列表
    """
    try:
        query = select(Article).where(Article.id == article_id)
        result = await db.execute(query)
        article = result.scalar_one_or_none()
        
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")
        
        return {
            "success": True,
            "article_id": article_id,
            "tags": article.get_tags_list()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取标签失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取标签失败: {str(e)}")


@router.put("/{article_id}/tags")
async def update_article_tags(
    article_id: int,
    request: UpdateTagsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    更新文章标签（覆盖原有标签）
    
    Args:
        article_id: 文章ID
        request: 标签更新请求
        db: 数据库会话
    
    Returns:
        更新结果
    """
    try:
        query = select(Article).where(Article.id == article_id)
        result = await db.execute(query)
        article = result.scalar_one_or_none()
        
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")
        
        # 清理标签（去除空白，限制长度）
        cleaned_tags = [tag.strip()[:50] for tag in request.tags if tag.strip()]
        # 去重并保持顺序
        cleaned_tags = list(dict.fromkeys(cleaned_tags))[:10]  # 最多10个标签
        
        article.set_tags_list(cleaned_tags)
        await db.commit()
        
        return {
            "success": True,
            "article_id": article_id,
            "tags": cleaned_tags,
            "message": "标签更新成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"更新标签失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新标签失败: {str(e)}")


@router.post("/{article_id}/tags/add")
async def add_article_tag(
    article_id: int,
    request: AddTagRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    添加单个标签到文章
    
    Args:
        article_id: 文章ID
        request: 添加标签请求
        db: 数据库会话
    
    Returns:
        更新结果
    """
    try:
        query = select(Article).where(Article.id == article_id)
        result = await db.execute(query)
        article = result.scalar_one_or_none()
        
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")
        
        current_tags = article.get_tags_list()
        new_tag = request.tag.strip()[:50]
        
        if new_tag not in current_tags:
            current_tags.append(new_tag)
            article.set_tags_list(current_tags)
            await db.commit()
        
        return {
            "success": True,
            "article_id": article_id,
            "tags": article.get_tags_list(),
            "message": f"标签 '{new_tag}' 添加成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"添加标签失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加标签失败: {str(e)}")


@router.post("/{article_id}/tags/remove")
async def remove_article_tag(
    article_id: int,
    request: RemoveTagRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    从文章移除单个标签
    
    Args:
        article_id: 文章ID
        request: 移除标签请求
        db: 数据库会话
    
    Returns:
        更新结果
    """
    try:
        query = select(Article).where(Article.id == article_id)
        result = await db.execute(query)
        article = result.scalar_one_or_none()
        
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")
        
        current_tags = article.get_tags_list()
        tag_to_remove = request.tag.strip()
        
        if tag_to_remove in current_tags:
            current_tags.remove(tag_to_remove)
            article.set_tags_list(current_tags)
            await db.commit()
        
        return {
            "success": True,
            "article_id": article_id,
            "tags": article.get_tags_list(),
            "message": f"标签 '{tag_to_remove}' 移除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"移除标签失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"移除标签失败: {str(e)}")


@router.get("/tags/all")
async def get_all_tags(db: AsyncSession = Depends(get_db)):
    """
    获取所有文章标签统计
    
    Returns:
        标签列表及使用次数
    """
    try:
        from sqlalchemy import func
        
        # 获取所有文章的标签
        query = select(Article.tags).where(Article.tags.isnot(None))
        result = await db.execute(query)
        all_tags_records = result.scalars().all()
        
        # 统计标签使用次数
        tag_counts = {}
        for tags_str in all_tags_records:
            if tags_str:
                for tag in tags_str.split(','):
                    tag = tag.strip()
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 按使用次数排序
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "success": True,
            "tags": [
                {"name": tag, "count": count}
                for tag, count in sorted_tags
            ],
            "total_unique": len(sorted_tags)
        }
    except Exception as e:
        logger.error(f"获取标签统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取标签统计失败: {str(e)}")


@router.get("/tags/search")
async def search_articles_by_tag(
    tag: str,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    根据标签搜索文章
    
    Args:
        tag: 标签名称
        skip: 跳过数量
        limit: 返回数量
        db: 数据库会话
    
    Returns:
        匹配的文章列表
    """
    try:
        # 使用LIKE进行模糊匹配
        search_pattern = f"%{tag}%"
        query = select(Article).where(
            Article.tags.like(search_pattern)
        ).order_by(Article.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        articles = result.scalars().all()
        
        return {
            "success": True,
            "tag": tag,
            "articles": articles,
            "total": len(articles)
        }
    except Exception as e:
        logger.error(f"搜索标签失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索标签失败: {str(e)}")


@router.get("/stats/trend")
async def get_article_trend(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """
    获取文章创建趋势统计

    Args:
        days: 统计天数（默认7天）
        db: 数据库会话

    Returns:
        趋势数据列表
    """
    try:
        from datetime import timedelta, datetime as dt
        from sqlalchemy import func, extract

        # 计算开始日期
        end_date = dt.utcnow()
        start_date = end_date - timedelta(days - 1)

        # 按日期分组统计
        query = select(
            func.date(Article.created_at).label('date'),
            func.count(Article.id).label('count')
        ).where(
            func.date(Article.created_at) >= start_date.date()
        ).group_by(
            func.date(Article.created_at)
        ).order_by(
            func.date(Article.created_at)
        )

        result = await db.execute(query)
        trend_data = result.all()

        # 构建完整的日期序列（填充缺失的日期）
        trend_dict = {str(date): count for date, count in trend_data}
        full_trend = []

        for i in range(days):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            full_trend.append({
                "date": date_str,
                "count": trend_dict.get(date_str, 0)
            })

        return {
            "success": True,
            "days": days,
            "trend": full_trend,
            "total": sum(item["count"] for item in full_trend)
        }
    except Exception as e:
        logger.error(f"获取文章趋势失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")


@router.get("/stats/trend")
async def get_article_trend_chart(days: int = 7, db: AsyncSession = Depends(get_db)):
    """
    获取文章发布趋势图表数据
    
    Args:
        days: 统计天数（默认7天）
        db: 数据库会话
    
    Returns:
        图表数据
    """
    try:
        from datetime import timedelta, datetime as dt
        from sqlalchemy import func

        # 计算开始日期
        end_date = dt.utcnow()
        start_date = end_date - timedelta(days - 1)

        # 获取已发布文章趋势
        published_query = select(
            func.date(Article.created_at).label('date'),
            func.count(Article.id).label('count')
        ).where(
            Article.status == ArticleStatus.PUBLISHED,
            func.date(Article.created_at) >= start_date.date()
        ).group_by(
            func.date(Article.created_at)
        ).order_by(
            func.date(Article.created_at)
        )

        # 获取草稿文章趋势
        draft_query = select(
            func.date(Article.created_at).label('date'),
            func.count(Article.id).label('count')
        ).where(
            Article.status == ArticleStatus.DRAFT,
            func.date(Article.created_at) >= start_date.date()
        ).group_by(
            func.date(Article.created_at)
        ).order_by(
            func.date(Article.created_at)
        )

        published_result = await db.execute(published_query)
        published_data = {str(date): count for date, count in published_result.all()}

        draft_result = await db.execute(draft_query)
        draft_data = {str(date): count for date, count in draft_result.all()}

        # 构建图表数据
        labels = []
        published_values = []
        draft_values = []

        for i in range(days):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime('%m/%d')
            labels.append(date_str)
            published_values.append(published_data.get(str(current_date.date()), 0))
            draft_values.append(draft_data.get(str(current_date.date()), 0))

        return {
            "type": "line",
            "title": "最近7天发布趋势",
            "labels": labels,
            "datasets": [
                {
                    "label": "已发布",
                    "data": published_values,
                    "borderColor": "#3b82f6",
                    "backgroundColor": "#3b82f6",
                    "borderWidth": 2,
                    "fill": False
                },
                {
                    "label": "草稿",
                    "data": draft_values,
                    "borderColor": "#6b7280",
                    "backgroundColor": "#6b7280",
                    "borderWidth": 2,
                    "fill": False
                }
            ]
        }
    except Exception as e:
        logger.error(f"获取趋势图表数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取趋势图表数据失败: {str(e)}")


@router.get("/stats/platform")
async def get_platform_stats(db: AsyncSession = Depends(get_db)):
    """
    获取跨平台统计数据
    
    Returns:
        平台统计数据
    """
    try:
        from sqlalchemy import func
        from ..models.publish_platform import PublishRecord, PlatformType, PublishStatus

        # 获取各平台的统计数据
        platform_labels = {
            PlatformType.WECHAT: "微信公众号",
            PlatformType.ZHIHU: "知乎",
            PlatformType.JUEJIN: "掘金",
            PlatformType.TOUTIAO: "头条"
        }

        # 构建查询 - 按平台汇总阅读量和点赞数
        query = select(
            PublishRecord.platform,
            func.sum(PublishRecord.view_count).label('total_views'),
            func.sum(PublishRecord.like_count).label('total_likes'),
            func.count(PublishRecord.id).label('article_count')
        ).where(
            PublishRecord.status == PublishStatus.SUCCESS
        ).group_by(
            PublishRecord.platform
        )

        result = await db.execute(query)
        platform_data = result.all()

        # 构建图表数据
        labels = []
        views_data = []
        likes_data = []
        articles_data = []

        # 按固定顺序填充数据
        for platform_type in [PlatformType.WECHAT, PlatformType.ZHIHU, PlatformType.JUEJIN, PlatformType.TOUTIAO]:
            labels.append(platform_labels[platform_type])
            
            # 查找该平台的数据
            platform_stats = next(
                (row for row in platform_data if row.platform == platform_type),
                None
            )
            
            if platform_stats:
                views_data.append(platform_stats.total_views or 0)
                likes_data.append(platform_stats.total_likes or 0)
                articles_data.append(platform_stats.article_count or 0)
            else:
                views_data.append(0)
                likes_data.append(0)
                articles_data.append(0)

        return {
            "type": "bar",
            "title": "跨平台数据对比",
            "labels": labels,
            "datasets": [
                {
                    "label": "阅读量",
                    "data": views_data,
                    "backgroundColor": "#6366f1",
                    "borderColor": "#6366f1",
                    "borderWidth": 0
                },
                {
                    "label": "点赞数",
                    "data": likes_data,
                    "backgroundColor": "#ec4899",
                    "borderColor": "#ec4899",
                    "borderWidth": 0
                }
            ],
            "summary": {
                "total_articles": sum(articles_data),
                "total_views": sum(views_data),
                "total_likes": sum(likes_data),
                "platforms_with_articles": sum(1 for count in articles_data if count > 0)
            }
        }

    except Exception as e:
        logger.error(f"获取平台统计数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取平台统计数据失败: {str(e)}")


@router.get("/stats/category")
async def get_category_stats(db: AsyncSession = Depends(get_db)):
    """
    获取文章分类统计（基于标签）
    
    Returns:
        分类统计数据
    """
    try:
        from sqlalchemy import func

        # 获取所有文章的标签
        query = select(Article.tags).where(
            Article.tags.isnot(None),
            Article.tags != ''
        )
        result = await db.execute(query)
        all_tags_records = result.scalars().all()

        # 统计标签使用次数
        tag_counts = {}
        for tags_str in all_tags_records:
            if tags_str:
                for tag in tags_str.split(','):
                    tag = tag.strip()
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # 按使用次数排序，取前8个
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:8]

        # 构建图表数据
        labels = []
        values = []
        colors = ["#6366f1", "#8b5cf6", "#ec4899", "#22c55e", "#3b82f6", "#f59e0b", "#ef4444", "#14b8a6"]

        for tag, count in sorted_tags:
            labels.append(tag)
            values.append(count)

        return {
            "type": "pie",
            "title": "文章标签分布",
            "labels": labels,
            "datasets": [
                {
                    "label": "数量",
                    "data": values,
                    "backgroundColor": colors[:len(labels)],
                    "borderColor": colors[:len(labels)],
                    "borderWidth": 0
                }
            ],
            "summary": {
                "total_categories": len(labels),
                "total_articles": sum(values)
            }
        }

    except Exception as e:
        logger.error(f"获取分类统计数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取分类统计数据失败: {str(e)}")

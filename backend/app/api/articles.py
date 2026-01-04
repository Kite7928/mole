from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from ..core.database import get_db
from ..core.logger import logger
from ..models.article import Article, ArticleStatus, ArticleSource
from ..services.ai_writer import ai_writer_service
from ..services.image_service import image_service

router = APIRouter()


# Pydantic models
class ArticleCreateRequest(BaseModel):
    topic: str = Field(..., description="Article topic")
    title: Optional[str] = Field(None, description="Article title (optional, will be generated if not provided)")
    source: ArticleSource = Field(ArticleSource.MANUAL, description="Article source")
    style: str = Field("professional", description="Writing style")
    length: str = Field("medium", description="Article length")
    enable_research: bool = Field(False, description="Enable deep research")
    generate_cover: bool = Field(True, description="Generate cover image")
    ai_model: Optional[str] = Field(None, description="AI model to use")


class TitleGenerateRequest(BaseModel):
    topic: str = Field(..., description="Topic to generate titles for")
    count: int = Field(5, ge=1, le=10, description="Number of titles to generate")
    ai_model: Optional[str] = Field(None, description="AI model to use")


class ContentGenerateRequest(BaseModel):
    topic: str = Field(..., description="Article topic")
    title: str = Field(..., description="Article title")
    style: str = Field("professional", description="Writing style")
    length: str = Field("medium", description="Article length")
    enable_research: bool = Field(False, description="Enable deep research")
    ai_model: Optional[str] = Field(None, description="AI model to use")


class ContentOptimizeRequest(BaseModel):
    article_id: int = Field(..., description="Article ID")
    optimization_type: str = Field("enhance", description="Optimization type")
    ai_model: Optional[str] = Field(None, description="AI model to use")


class ArticleResponse(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    content: str
    status: ArticleStatus
    source: ArticleSource
    cover_image_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TitleResponse(BaseModel):
    title: str
    predicted_click_rate: float
    emotion: str


# Endpoints
@router.post("/titles/generate", response_model=List[TitleResponse])
async def generate_titles(request: TitleGenerateRequest):
    """Generate multiple article titles based on topic."""
    try:
        logger.info(f"Generating titles for topic: {request.topic}")

        titles = await ai_writer_service.generate_titles(
            topic=request.topic,
            count=request.count,
            model=request.ai_model
        )

        return titles

    except Exception as e:
        logger.error(f"Error generating titles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content/generate")
async def generate_content(request: ContentGenerateRequest):
    """Generate article content based on topic and title."""
    try:
        logger.info(f"Generating content for: {request.title}")

        content = await ai_writer_service.generate_content(
            topic=request.topic,
            title=request.title,
            style=request.style,
            length=request.length,
            enable_research=request.enable_research,
            model=request.ai_model
        )

        return content

    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize/{article_id}")
async def optimize_article_content(
    article_id: int,
    request: ContentOptimizeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Optimize article content."""
    try:
        # Get article
        result = await db.execute(select(Article).where(Article.id == article_id))
        article = result.scalar_one_or_none()

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        # Optimize content
        optimized_content = await ai_writer_service.optimize_content(
            content=article.content,
            optimization_type=request.optimization_type,
            model=request.ai_model
        )

        # Update article
        article.content = optimized_content
        article.updated_at = datetime.utcnow()
        await db.commit()

        return {
            "message": "Content optimized successfully",
            "content": optimized_content
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=ArticleResponse)
async def create_article(
    request: ArticleCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new article."""
    try:
        logger.info(f"Creating article for topic: {request.topic}")

        # Generate title if not provided
        if not request.title:
            titles = await ai_writer_service.generate_titles(
                topic=request.topic,
                count=1,
                model=request.ai_model
            )
            request.title = titles[0]["title"]

        # Generate content
        content_data = await ai_writer_service.generate_content(
            topic=request.topic,
            title=request.title,
            style=request.style,
            length=request.length,
            enable_research=request.enable_research,
            model=request.ai_model
        )

        # Generate cover image if requested
        cover_image_url = None
        if request.generate_cover:
            keywords = request.topic[:50]
            cover_image_url = await image_service.search_cover_image(keywords)

        # Create article record
        article = Article(
            title=request.title,
            summary=content_data.get("summary"),
            content=content_data.get("content"),
            html_content=content_data.get("content"),  # TODO: Convert to HTML
            source=request.source,
            source_topic=request.topic,
            status=ArticleStatus.READY,
            ai_model=request.ai_model or "default",
            cover_image_url=cover_image_url,
            tags=content_data.get("tags"),
            quality_score=content_data.get("quality_score")
        )

        db.add(article)
        await db.commit()
        await db.refresh(article)

        logger.info(f"Article created: {article.id}")
        return article

    except Exception as e:
        logger.error(f"Error creating article: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ArticleResponse])
async def list_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[ArticleStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    """List articles with pagination."""
    try:
        query = select(Article)

        if status:
            query = query.where(Article.status == status)

        query = query.order_by(Article.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        articles = result.scalars().all()

        return articles

    except Exception as e:
        logger.error(f"Error listing articles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get article by ID."""
    try:
        result = await db.execute(select(Article).where(Article.id == article_id))
        article = result.scalar_one_or_none()

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        return article

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete article by ID."""
    try:
        result = await db.execute(select(Article).where(Article.id == article_id))
        article = result.scalar_one_or_none()

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        await db.delete(article)
        await db.commit()

        return {"message": "Article deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from ..core.database import get_db
from ..core.logger import logger
from ..models.wechat import WeChatAccount, WeChatMedia
from ..models.article import Article
from ..services.wechat_service import wechat_service

router = APIRouter()


# Pydantic models
class WeChatAccountCreate(BaseModel):
    name: str = Field(..., description="Account name")
    app_id: str = Field(..., description="WeChat AppID")
    app_secret: str = Field(..., description="WeChat AppSecret")
    account_type: Optional[str] = Field(None, description="Account type")
    is_default: bool = Field(False, description="Set as default account")


class WeChatAccountResponse(BaseModel):
    id: int
    name: str
    app_id: str
    account_type: Optional[str]
    is_active: bool
    is_default: bool
    followers_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class DraftCreateRequest(BaseModel):
    article_id: int = Field(..., description="Article ID")
    account_id: int = Field(..., description="WeChat account ID")


class DraftPublishRequest(BaseModel):
    draft_id: str = Field(..., description="WeChat draft media_id")


class ArticlePublishRequest(BaseModel):
    article_id: int = Field(..., description="Article ID")
    account_id: int = Field(..., description="WeChat account ID")


# Endpoints
@router.post("/accounts", response_model=WeChatAccountResponse)
async def create_wechat_account(
    account: WeChatAccountCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new WeChat account."""
    try:
        logger.info(f"Creating WeChat account: {account.name}")

        # Check if AppID already exists
        result = await db.execute(
            select(WeChatAccount).where(WeChatAccount.app_id == account.app_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(status_code=400, detail="AppID already exists")

        # If setting as default, unset other defaults
        if account.is_default:
            await db.execute(
                select(WeChatAccount).where(WeChatAccount.is_default == True)
            )
            # TODO: Update all existing accounts to is_default=False

        # Create account
        wechat_account = WeChatAccount(
            name=account.name,
            app_id=account.app_id,
            app_secret=account.app_secret,
            account_type=account.account_type,
            is_default=account.is_default
        )

        db.add(wechat_account)
        await db.commit()
        await db.refresh(wechat_account)

        logger.info(f"WeChat account created: {wechat_account.id}")
        return wechat_account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating WeChat account: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts", response_model=List[WeChatAccountResponse])
async def list_wechat_accounts(db: AsyncSession = Depends(get_db)):
    """List all WeChat accounts."""
    try:
        result = await db.execute(
            select(WeChatAccount).order_by(WeChatAccount.created_at.desc())
        )
        accounts = result.scalars().all()

        return accounts

    except Exception as e:
        logger.error(f"Error listing WeChat accounts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts/{account_id}", response_model=WeChatAccountResponse)
async def get_wechat_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get WeChat account by ID."""
    try:
        result = await db.execute(
            select(WeChatAccount).where(WeChatAccount.id == account_id)
        )
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        return account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting WeChat account: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/media/upload")
async def upload_media(
    file: UploadFile = File(...),
    media_type: str = Form("image"),
    account_id: int = Form(None)
):
    """Upload media file to WeChat."""
    try:
        logger.info(f"Uploading media: {file.filename}")

        # Save uploaded file temporarily
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Upload to WeChat
            result = await wechat_service.upload_media(temp_file_path, media_type)

            return {
                "message": "Media uploaded successfully",
                "media_id": result.get("media_id"),
                "url": result.get("url")
            }

        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    except Exception as e:
        logger.error(f"Error uploading media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drafts/create")
async def create_draft(
    request: DraftCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create WeChat draft from article."""
    try:
        logger.info(f"Creating draft for article {request.article_id}")

        # Get article
        result = await db.execute(
            select(Article).where(Article.id == request.article_id)
        )
        article = result.scalar_one_or_none()

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        # Get WeChat account
        result = await db.execute(
            select(WeChatAccount).where(WeChatAccount.id == request.account_id)
        )
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(status_code=404, detail="WeChat account not found")

        # Initialize WeChat service with account credentials
        wechat = wechat_service.__class__(account.app_id, account.app_secret)

        # Prepare article data
        article_data = {
            "title": article.title,
            "content": article.content,
            "digest": article.summary,
            "author": "AI Writer",
            "thumb_media_id": article.cover_image_media_id
        }

        # Create draft
        result = await wechat.create_draft([article_data])

        # Update article with draft ID
        article.wechat_draft_id = result.get("media_id")
        await db.commit()

        return {
            "message": "Draft created successfully",
            "draft_id": result.get("media_id")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating draft: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drafts/publish")
async def publish_draft(request: DraftPublishRequest):
    """Publish WeChat draft."""
    try:
        logger.info(f"Publishing draft: {request.draft_id}")

        result = await wechat_service.publish_article(request.draft_id)

        return {
            "message": "Article published successfully",
            "publish_id": result.get("publish_id")
        }

    except Exception as e:
        logger.error(f"Error publishing draft: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/articles/publish")
async def publish_article(request: ArticlePublishRequest, db: AsyncSession = Depends(get_db)):
    """Publish article directly (create draft and publish)."""
    try:
        logger.info(f"Publishing article {request.article_id}")

        # Get article
        result = await db.execute(
            select(Article).where(Article.id == request.article_id)
        )
        article = result.scalar_one_or_none()

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        # Get WeChat account
        result = await db.execute(
            select(WeChatAccount).where(WeChatAccount.id == request.account_id)
        )
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(status_code=404, detail="WeChat account not found")

        # Initialize WeChat service
        wechat = wechat_service.__class__(account.app_id, account.app_secret)

        # Create article data
        article_data = {
            "title": article.title,
            "content": article.content,
            "digest": article.summary,
            "author": "AI Writer",
            "thumb_media_id": article.cover_image_media_id
        }

        # Create draft
        draft_result = await wechat.create_draft([article_data])
        draft_id = draft_result.get("media_id")

        # Publish draft
        publish_result = await wechat.publish_article(draft_id)

        # Update article
        article.wechat_draft_id = draft_id
        article.wechat_publish_time = datetime.utcnow()
        article.status = "published"
        await db.commit()

        return {
            "message": "Article published successfully",
            "draft_id": draft_id,
            "publish_id": publish_result.get("publish_id")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing article: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/account/info")
async def get_account_info():
    """Get WeChat account information."""
    try:
        result = await wechat_service.get_user_info()
        return result

    except Exception as e:
        logger.error(f"Error getting account info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
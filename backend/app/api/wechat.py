"""
微信集成API路由 - 简化版
支持配置管理、连接测试、发布草稿、图片上传
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path
import shutil
from ..services.wechat_service import wechat_service
from ..services.image_generation_service import image_generation_service
from ..core.config import settings
from ..core.logger import logger
from ..core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.config import AppConfig

router = APIRouter()


class WeChatConfig(BaseModel):
    """微信配置模型"""
    app_id: str = Field(..., description="公众号AppID")
    app_secret: str = Field(..., description="公众号AppSecret")


class PublishRequest(BaseModel):
    """发布请求模型"""
    title: str = Field(..., description="文章标题")
    content: str = Field(..., description="文章内容（HTML格式）")
    digest: str = Field(default="", description="摘要")
    cover_media_id: str = Field(default="", description="封面图media_id")
    author: str = Field(default="AI助手", description="作者")


@router.get("/config", response_model=dict)
async def get_wechat_config():
    """
    获取微信配置（隐藏密钥）
    
    Returns:
        微信配置信息（密钥已隐藏）
    """
    try:
        return {
            "app_id": settings.WECHAT_APP_ID,
            "app_secret": "***隐藏***" if settings.WECHAT_APP_SECRET else None,
            "configured": bool(settings.WECHAT_APP_ID and settings.WECHAT_APP_SECRET)
        }
    except Exception as e:
        logger.error(f"获取微信配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.post("/test", response_model=dict)
async def test_wechat_connection():
    """
    测试微信连接
    
    Returns:
        测试结果
    """
    try:
        if not settings.WECHAT_APP_ID or not settings.WECHAT_APP_SECRET:
            raise HTTPException(status_code=400, detail="未配置微信AppID和AppSecret")
        
        logger.info("测试微信连接")
        
        # 尝试获取access_token
        access_token = await wechat_service.get_access_token(
            app_id=settings.WECHAT_APP_ID,
            app_secret=settings.WECHAT_APP_SECRET
        )
        
        return {
            "success": True,
            "message": "微信连接测试成功",
            "access_token": access_token[:20] + "..."  # 只显示部分token
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"测试微信连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"连接测试失败: {str(e)}")


@router.post("/publish", response_model=dict)
async def publish_to_wechat(request: PublishRequest, db: AsyncSession = Depends(get_db)):
    """
    发布文章到微信草稿箱

    Args:
        request: 发布请求
        db: 数据库会话

    Returns:
        发布结果
    """
    try:
        # 从数据库读取微信配置
        result = await db.execute(select(AppConfig))
        config = result.scalar_one_or_none()
        
        if not config or not config.wechat_app_id or not config.wechat_app_secret:
            logger.warning("微信配置未设置")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "未配置微信公众号",
                    "message": "请先在系统设置中配置微信公众号的AppID和AppSecret",
                    "guide": "1. 访问 http://localhost:3000/settings\n2. 配置微信公众号的AppID和AppSecret\n3. 保存配置"
                }
            )
        
        wechat_app_id = config.wechat_app_id
        wechat_app_secret = config.wechat_app_secret

        logger.info(f"发布文章到微信，标题: {request.title}")

        # 获取access_token
        try:
            access_token = await wechat_service.get_access_token(
                app_id=wechat_app_id,
                app_secret=wechat_app_secret
            )
        except ValueError as ve:
            # 网络连接错误
            error_msg = str(ve)
            if "无法连接" in error_msg or "连接失败" in error_msg:
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "无法连接到微信API",
                        "message": "网络连接失败，请检查网络设置",
                        "guide": "可能的原因：\n1. 网络连接问题\n2. 需要配置代理\n3. 防火墙阻止了连接\n\n建议：\n- 检查网络连接\n- 如在国内，可能需要配置代理\n- 检查防火墙设置"
                    }
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "获取微信access_token失败",
                        "message": error_msg,
                        "guide": "请检查AppID和AppSecret是否正确"
                    }
                )

        # 创建草稿
        try:
            # 如果没有封面图，生成一个默认封面图
            cover_media_id = request.cover_media_id
            if not cover_media_id:
                logger.info("未提供封面图，生成默认封面图...")
                
                # 创建一个简单的默认封面图
                from PIL import Image, ImageDraw, ImageFont
                import io
                import uuid
                
                # 创建封面图
                img = Image.new('RGB', (900, 500), color='#4A90E2')
                draw = ImageDraw.Draw(img)
                
                # 尝试添加标题文字
                try:
                    # 使用默认字体
                    font = ImageFont.load_default()
                    title_text = request.title[:20] if request.title else "文章封面"
                    # 简单的文字居中
                    text_width = draw.textlength(title_text, font=font)
                    x = (900 - text_width) / 2
                    y = 250
                    draw.text((x, y), title_text, fill='white', font=font)
                except:
                    pass  # 如果字体加载失败，就使用纯色背景
                
                # 保存临时图片
                temp_image_path = f"G:/db/guwen/gzh/backend/uploads/temp_cover_{uuid.uuid4().hex[:8]}.jpg"
                img.save(temp_image_path, 'JPEG')
                
                # 上传到微信
                cover_media_id = await wechat_service.upload_permanent_material(
                    access_token=access_token,
                    media_type="image",
                    file_path=temp_image_path,
                    description={"introduction": request.digest or request.title}
                )
                
                logger.info(f"默认封面图上传成功: {cover_media_id}")
            
            draft_id = await wechat_service.create_draft(
                access_token=access_token,
                title=request.title,
                author=request.author,
                digest=request.digest,
                content=request.content,
                cover_media_id=cover_media_id
            )
        except ValueError as ve:
            error_msg = str(ve)
            if "无法连接" in error_msg or "连接失败" in error_msg:
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "无法连接到微信API",
                        "message": "创建草稿时网络连接失败",
                        "guide": "请检查网络连接和代理设置"
                    }
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "创建草稿失败",
                        "message": error_msg,
                        "guide": "请检查文章内容是否符合微信公众号规范"
                    }
                )

        logger.info(f"草稿创建成功: {draft_id}")

        return {
            "success": True,
            "message": "草稿创建成功",
            "draft_id": draft_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发布到微信失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "发布失败",
                "message": str(e),
                "guide": "请稍后重试，如问题持续请联系技术支持"
            }
        )


@router.post("/upload-image", response_model=dict)
async def upload_wechat_image(file: UploadFile = File(...)):
    """
    上传图片到微信并返回media_id
    
    Args:
        file: 图片文件
    
    Returns:
        上传结果，包含media_id和图片URL
    """
    try:
        if not settings.WECHAT_APP_ID or not settings.WECHAT_APP_SECRET:
            raise HTTPException(status_code=400, detail="未配置微信AppID和AppSecret")
        
        logger.info(f"上传图片到微信，文件名: {file.filename}")
        
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="只支持图片文件")
        
        # 保存到临时目录
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        
        # 裁剪图片到微信封面尺寸
        cropped_path = await image_generation_service.crop_image(str(file_path))
        
        # 上传到微信
        access_token = await wechat_service.get_access_token(
            app_id=settings.WECHAT_APP_ID,
            app_secret=settings.WECHAT_APP_SECRET
        )
        
        media_id = await wechat_service.upload_media(
            access_token=access_token,
            media_type="image",
            file_path=cropped_path
        )
        
        logger.info(f"图片上传成功，media_id: {media_id}")
        
        return {
            "success": True,
            "message": "图片上传成功",
            "media_id": media_id,
            "image_path": cropped_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传图片失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@router.post("/publish-draft/{article_id}", response_model=dict)
async def publish_article_to_wechat_draft(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    根据文章ID发布到微信草稿箱

    Args:
        article_id: 文章ID
        db: 数据库会话

    Returns:
        发布结果
    """
    try:
        logger.info(f"发布文章到微信草稿箱，文章ID: {article_id}")

        # 1. 从数据库查询文章
        from ..models.article import Article
        query = select(Article).where(Article.id == article_id)
        result = await db.execute(query)
        article = result.scalar_one_or_none()

        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")

        # 2. 从数据库读取微信配置
        query_config = select(AppConfig).order_by(AppConfig.id.desc())
        result_config = await db.execute(query_config)
        config = result_config.scalar_one_or_none()

        if not config or not config.wechat_app_id or not config.wechat_app_secret:
            logger.warning("微信配置未设置")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "未配置微信公众号",
                    "message": "请先在系统设置中配置微信公众号的AppID和AppSecret",
                    "guide": "1. 访问 http://localhost:3000/settings\n2. 配置微信公众号的AppID和AppSecret\n3. 保存配置"
                }
            )

        wechat_app_id = config.wechat_app_id
        wechat_app_secret = config.wechat_app_secret

        # 3. 获取access_token
        try:
            access_token = await wechat_service.get_access_token(
                app_id=wechat_app_id,
                app_secret=wechat_app_secret
            )
        except ValueError as ve:
            error_msg = str(ve)
            if "无法连接" in error_msg or "连接失败" in error_msg:
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "无法连接到微信API",
                        "message": "网络连接失败，请检查网络设置",
                        "guide": "可能的原因：\n1. 网络连接问题\n2. 需要配置代理\n3. 防火墙阻止了连接"
                    }
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "获取微信access_token失败",
                        "message": error_msg,
                        "guide": "请检查AppID和AppSecret是否正确"
                    }
                )

        # 4. 处理封面图
        cover_media_id = ""
        if article.cover_image_url:
            # 如果文章有封面图，上传到微信
            try:
                # 检查封面图路径
                cover_path = article.cover_image_url
                if cover_path.startswith('http://') or cover_path.startswith('https://'):
                    # 如果是URL，需要先下载
                    logger.info(f"封面图是URL，暂不支持自动下载: {cover_path}")
                else:
                    # 本地文件路径
                    if not Path(cover_path).is_absolute():
                        # 相对路径，转换为绝对路径
                        cover_path = str(Path(settings.UPLOAD_DIR) / cover_path)

                    if Path(cover_path).exists():
                        cover_media_id = await wechat_service.upload_permanent_material(
                            access_token=access_token,
                            media_type="image",
                            file_path=cover_path,
                            description={"introduction": article.summary or article.title}
                        )
                        logger.info(f"封面图上传成功: {cover_media_id}")
            except Exception as img_error:
                logger.warning(f"上传封面图失败: {str(img_error)}，将生成默认封面")

        # 如果没有封面图或上传失败，生成默认封面
        if not cover_media_id:
            logger.info("生成默认封面图...")
            try:
                from PIL import Image, ImageDraw, ImageFont
                import uuid

                # 创建封面图
                img = Image.new('RGB', (900, 500), color='#4A90E2')
                draw = ImageDraw.Draw(img)

                # 添加标题文字
                try:
                    font = ImageFont.load_default()
                    title_text = article.title[:20] if article.title else "文章封面"
                    text_bbox = draw.textbbox((0, 0), title_text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    x = (900 - text_width) / 2
                    y = 250
                    draw.text((x, y), title_text, fill='white', font=font)
                except:
                    pass

                # 保存临时图片
                temp_image_path = str(Path(settings.UPLOAD_DIR) / f"temp_cover_{uuid.uuid4().hex[:8]}.jpg")
                img.save(temp_image_path, 'JPEG')

                # 上传到微信
                cover_media_id = await wechat_service.upload_permanent_material(
                    access_token=access_token,
                    media_type="image",
                    file_path=temp_image_path,
                    description={"introduction": article.summary or article.title}
                )
                logger.info(f"默认封面图上传成功: {cover_media_id}")
            except Exception as default_img_error:
                logger.error(f"生成默认封面图失败: {str(default_img_error)}")
                # 继续执行，不阻塞发布流程

        # 5. 创建草稿
        try:
            draft_id = await wechat_service.create_draft(
                access_token=access_token,
                title=article.title,
                author="AI助手",
                digest=article.summary or "",
                content=article.content,
                cover_media_id=cover_media_id
            )
        except ValueError as ve:
            error_msg = str(ve)
            if "无法连接" in error_msg or "连接失败" in error_msg:
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "无法连接到微信API",
                        "message": "创建草稿时网络连接失败",
                        "guide": "请检查网络连接和代理设置"
                    }
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "创建草稿失败",
                        "message": error_msg,
                        "guide": "请检查文章内容是否符合微信公众号规范"
                    }
                )

        # 6. 更新文章状态
        from ..models.article import ArticleStatus
        article.wechat_draft_id = draft_id
        article.status = ArticleStatus.PUBLISHED
        await db.commit()

        logger.info(f"文章发布成功，草稿ID: {draft_id}")

        return {
            "success": True,
            "message": "发布到微信草稿箱成功",
            "draft_id": draft_id,
            "article_id": article_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发布到微信失败: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "发布失败",
                "message": str(e),
                "guide": "请稍后重试，如问题持续请联系技术支持"
            }
        )

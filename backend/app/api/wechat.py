"""
微信集成API路由 - 简化版
支持配置管理、连接测试、发布草稿、图片上传
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path
import shutil
import re
import socket
import uuid
import tempfile
import os
import httpx
from ..services.wechat_service import wechat_service
from ..services.image_generation_service import image_generation_service
from ..services.markdown_converter import markdown_converter
from ..core.config import settings
from ..core.logger import logger
from ..core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.config import AppConfig

router = APIRouter()


def _build_access_token_error_detail(error_msg: str) -> tuple[int, dict]:
    """统一解析 access_token 获取失败错误，返回 (status_code, detail)。"""
    if "无法连接" in error_msg or "连接失败" in error_msg:
        return 503, {
            "error": "无法连接到微信API",
            "message": "网络连接失败，请检查网络设置",
            "guide": "可能的原因：\n1. 网络连接问题\n2. 需要配置代理\n3. 防火墙阻止了连接\n\n建议：\n- 检查网络连接\n- 如在国内，可能需要配置代理\n- 检查防火墙设置",
        }

    if "40164" in error_msg or "invalid ip" in error_msg.lower():
        ip_match = re.search(r"invalid ip\s+([0-9\.]+)", error_msg, re.IGNORECASE)
        detected_ip = ip_match.group(1) if ip_match else "未知"
        return 400, {
            "error": "微信IP白名单校验失败（errcode: 40164）",
            "message": f"当前服务出口IP {detected_ip} 不在微信公众号后台IP白名单中",
            "guide": "请登录 mp.weixin.qq.com → 开发 → 基本配置 → IP白名单，添加该出口IP后重试。\n若本地公网IP经常变化，建议使用固定出口IP的云服务器或代理。",
            "detected_ip": detected_ip,
            "errcode": 40164,
        }

    return 400, {
        "error": "获取微信access_token失败",
        "message": error_msg,
        "guide": "请检查AppID和AppSecret是否正确",
    }


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
    author: str = Field(default="拾贝猫", description="作者")


def _mask_app_id(app_id: str) -> str:
    if not app_id:
        return ""
    if len(app_id) <= 8:
        return app_id[:2] + "***"
    return f"{app_id[:4]}***{app_id[-4:]}"


async def _get_wechat_credentials(db: AsyncSession) -> tuple[str, str, str]:
    """返回 (app_id, app_secret, source)。"""
    result = await db.execute(select(AppConfig).order_by(AppConfig.id.desc()))
    config = result.scalar_one_or_none()
    if config and config.wechat_app_id and config.wechat_app_secret:
        return config.wechat_app_id, config.wechat_app_secret, "database"
    return settings.WECHAT_APP_ID or "", settings.WECHAT_APP_SECRET or "", "env"


def _detect_local_ip() -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except Exception:
        return "unknown"


async def _convert_markdown_to_wechat_html(markdown_text: str) -> tuple[str, str]:
    """优先使用高级转换器，失败时回退简单转换。返回 (html, engine)。"""
    try:
        html = await markdown_converter.convert_to_wechat_html(markdown_text, inline_css=True)
        return html, "advanced"
    except Exception as e:
        logger.warning(f"高级转换器失败，回退简单转换: {e}")
        return wechat_service._simple_markdown_to_html(markdown_text), "simple"


async def _rewrite_html_images_for_wechat(
    html_content: str,
    access_token: str,
    trace_id: str,
) -> tuple[str, dict]:
    """将正文中的图片上传到微信并替换为微信URL。"""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, "html.parser")
    images = soup.find_all("img")
    stats = {
        "total": len(images),
        "replaced": 0,
        "failed": 0,
        "skipped": 0,
        "details": [],
    }

    logger.info(f"[{trace_id}] 开始重写正文图片: total={len(images)}")

    for index, img in enumerate(images, start=1):
        src = (img.get("src") or "").strip()
        if not src:
            stats["skipped"] += 1
            stats["details"].append({"index": index, "status": "skipped", "reason": "empty_src"})
            logger.info(f"[{trace_id}] 正文图片跳过(index={index}): src 为空")
            continue

        if src.startswith("data:"):
            stats["skipped"] += 1
            stats["details"].append({"index": index, "status": "skipped", "src": src[:32], "reason": "data_uri"})
            logger.info(f"[{trace_id}] 正文图片跳过(index={index}): data URI 不支持上传")
            continue

        logger.info(f"[{trace_id}] 正文图片处理(index={index}): src={src}")

        temp_path = None
        try:
            # 1) 准备本地文件
            if src.startswith("http://") or src.startswith("https://"):
                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                    response = await client.get(src)
                    response.raise_for_status()
                    suffix = ".jpg"
                    content_type = response.headers.get("content-type", "")
                    if "png" in content_type:
                        suffix = ".png"
                    elif "gif" in content_type:
                        suffix = ".gif"

                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                        tmp_file.write(response.content)
                        temp_path = tmp_file.name
            else:
                normalized = src.replace("\\", "/")
                if normalized.startswith("/uploads/"):
                    temp_path = str(Path(settings.UPLOAD_DIR) / normalized.replace("/uploads/", "", 1))
                elif normalized.startswith("uploads/"):
                    temp_path = str(Path(settings.UPLOAD_DIR) / normalized.replace("uploads/", "", 1))
                else:
                    path_obj = Path(normalized)
                    temp_path = str(path_obj if path_obj.is_absolute() else (Path(settings.UPLOAD_DIR) / normalized))

            logger.info(f"[{trace_id}] 正文图片解析(index={index}): resolved_path={temp_path}")

            if not temp_path or not Path(temp_path).exists():
                raise ValueError(f"图片文件不存在: {src}")

            file_size = Path(temp_path).stat().st_size
            logger.info(f"[{trace_id}] 正文图片上传(index={index}): size={file_size} bytes")

            # 2) 上传到微信正文图片接口
            wechat_url = await wechat_service.upload_article_image(access_token=access_token, file_path=temp_path)
            img["src"] = wechat_url
            stats["replaced"] += 1
            stats["details"].append({
                "index": index,
                "status": "replaced",
                "src": src,
                "wechat_url": wechat_url,
            })
            logger.info(f"[{trace_id}] 正文图片已替换(index={index}): {src} -> {wechat_url}")
        except Exception as image_error:
            stats["failed"] += 1
            stats["details"].append({
                "index": index,
                "status": "failed",
                "src": src,
                "error": str(image_error),
            })
            logger.warning(f"[{trace_id}] 正文图片替换失败(index={index}): src={src}, error={image_error}")
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    # 仅清理临时下载文件
                    if src.startswith("http://") or src.startswith("https://"):
                        os.remove(temp_path)
                except Exception:
                    pass

    logger.info(
        f"[{trace_id}] 正文图片重写结束: total={stats['total']}, replaced={stats['replaced']}, "
        f"failed={stats['failed']}, skipped={stats['skipped']}"
    )

    return str(soup), stats


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
        
    except ValueError as ve:
        error_msg = str(ve)
        status_code, detail = _build_access_token_error_detail(error_msg)
        raise HTTPException(status_code=status_code, detail=detail)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"测试微信连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"连接测试失败: {str(e)}")


@router.get("/diagnose", response_model=dict)
async def diagnose_wechat_connection(db: AsyncSession = Depends(get_db)):
    """微信诊断：配置、连通性、白名单错误识别。"""
    app_id, app_secret, source = await _get_wechat_credentials(db)

    diagnose_result = {
        "configured": bool(app_id and app_secret),
        "config_source": source,
        "app_id_masked": _mask_app_id(app_id),
        "local_ip": _detect_local_ip(),
        "access_token": {
            "ok": False,
            "detail": None,
        },
    }

    if not app_id or not app_secret:
        diagnose_result["access_token"]["detail"] = {
            "error": "未配置微信公众号",
            "message": "缺少 AppID 或 AppSecret",
            "guide": "请先在系统设置中配置微信公众号参数。",
        }
        return diagnose_result

    try:
        token = await wechat_service.get_access_token(app_id=app_id, app_secret=app_secret)
        diagnose_result["access_token"] = {
            "ok": True,
            "token_preview": token[:20] + "...",
            "detail": {
                "message": "获取 access_token 成功",
            },
        }
        return diagnose_result
    except ValueError as ve:
        error_msg = str(ve)
        status_code, detail = _build_access_token_error_detail(error_msg)
        diagnose_result["access_token"] = {
            "ok": False,
            "status_code": status_code,
            "detail": detail,
        }
        return diagnose_result
    except Exception as e:
        diagnose_result["access_token"] = {
            "ok": False,
            "status_code": 500,
            "detail": {
                "error": "诊断异常",
                "message": str(e),
            },
        }
        return diagnose_result


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
        trace_id = f"wxapi-{uuid.uuid4().hex[:8]}"
        # 从数据库读取微信配置
        result = await db.execute(select(AppConfig))
        config = result.scalar_one_or_none()
        
        if config and config.wechat_app_id and config.wechat_app_secret:
            wechat_app_id = config.wechat_app_id
            wechat_app_secret = config.wechat_app_secret
        else:
            logger.warning("数据库未找到微信配置，回退到环境变量")
            wechat_app_id = settings.WECHAT_APP_ID or ""
            wechat_app_secret = settings.WECHAT_APP_SECRET or ""

        logger.info(f"发布文章到微信，标题: {request.title}")

        # 获取access_token
        try:
            access_token = await wechat_service.get_access_token(
                app_id=wechat_app_id,
                app_secret=wechat_app_secret
            )
        except ValueError as ve:
            error_msg = str(ve)
            status_code, detail = _build_access_token_error_detail(error_msg)
            raise HTTPException(status_code=status_code, detail=detail)

        # 创建草稿
        try:
            # 未提供封面图时直接继续，避免封面上传失败阻断主流程
            cover_media_id = request.cover_media_id or ""
            
            # 转换 Markdown 为 HTML（优先高级转换）
            html_content, format_engine = await _convert_markdown_to_wechat_html(request.content)
            logger.info(f"[{trace_id}] 内容已转换为 HTML，转换器: {format_engine}，长度: {len(html_content)} 字符")

            html_content, image_stats = await _rewrite_html_images_for_wechat(
                html_content=html_content,
                access_token=access_token,
                trace_id=trace_id,
            )
            logger.info(f"[{trace_id}] 正文图片重写完成: total={image_stats['total']}, replaced={image_stats['replaced']}, failed={image_stats['failed']}")
            
            # 微信标题限制64字符
            title = request.title[:64] if len(request.title) > 64 else request.title
            
            draft_id = await wechat_service.create_draft(
                access_token=access_token,
                title=title,
                author=request.author,
                digest=request.digest,
                content=html_content,
                cover_media_id=cover_media_id
            )
        except ValueError as ve:
            error_msg = str(ve)
            logger.error(f"创建草稿时发生错误: {error_msg}")
            
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
                    status_code=400,
                    detail={
                        "error": "创建草稿失败",
                        "message": error_msg,
                        "guide": "请检查：\n1. 封面图是否上传成功\n2. 文章标题、摘要长度是否符合规范\n3. 文章内容格式是否正确"
                    }
                )

        logger.info(f"草稿创建成功: {draft_id}")

        return {
            "success": True,
            "message": "草稿创建成功",
            "draft_id": draft_id,
            "format_engine": format_engine,
            "image_rewrite": image_stats,
            "trace_id": trace_id,
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
        trace_id = f"wxpub-{uuid.uuid4().hex[:8]}"
        stage = "init"
        logger.info(f"[{trace_id}] 发布文章到微信草稿箱，文章ID: {article_id}")

        # 1. 从数据库查询文章
        stage = "load_article"
        from ..models.article import Article
        query = select(Article).where(Article.id == article_id)
        result = await db.execute(query)
        article = result.scalar_one_or_none()

        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")

        # 2. 从数据库读取微信配置
        stage = "load_wechat_config"
        query_config = select(AppConfig).order_by(AppConfig.id.desc())
        result_config = await db.execute(query_config)
        config = result_config.scalar_one_or_none()

        if not config or not config.wechat_app_id or not config.wechat_app_secret:
            logger.warning(f"[{trace_id}] 微信配置未设置")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "未配置微信公众号",
                    "message": "请先在系统设置中配置微信公众号的AppID和AppSecret",
                    "guide": "1. 访问 http://localhost:3000/settings\n2. 配置微信公众号的AppID和AppSecret\n3. 保存配置",
                    "trace_id": trace_id,
                }
            )

        wechat_app_id = config.wechat_app_id
        wechat_app_secret = config.wechat_app_secret

        # 3. 获取access_token
        stage = "get_access_token"
        try:
            access_token = await wechat_service.get_access_token(
                app_id=wechat_app_id,
                app_secret=wechat_app_secret
            )
        except ValueError as ve:
            error_msg = str(ve)
            status_code, detail = _build_access_token_error_detail(error_msg)
            if isinstance(detail, dict):
                detail["trace_id"] = trace_id
            raise HTTPException(status_code=status_code, detail=detail)

        # 4. 处理封面图（优先使用文章原封面，避免发布后封面不一致）
        stage = "upload_cover"
        cover_media_id = ""
        cover_source = "none"
        if not article.cover_image_url:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "缺少封面图",
                    "message": "该文章未设置封面图，无法保证微信草稿封面一致性",
                    "guide": "请先在文章编辑页设置封面图后再发布到微信公众号草稿箱。",
                    "trace_id": trace_id,
                    "stage": stage,
                }
            )

        if article.cover_image_url:
            # 如果文章有封面图，上传到微信
            try:
                # 检查封面图路径
                cover_path = article.cover_image_url
                logger.info(f"[{trace_id}] 文章封面图路径: {cover_path}")
                
                if cover_path.startswith('http://') or cover_path.startswith('https://'):
                    # 如果是URL，需要先下载
                    logger.info(f"封面图是URL，开始下载: {cover_path}")
                    try:
                        import httpx
                        import hashlib
                        from pathlib import Path
                        
                        # 下载图片
                        async with httpx.AsyncClient() as client:
                            response = await client.get(cover_path, timeout=30.0)
                            response.raise_for_status()
                            
                            # 生成文件名
                            filename = f"cover_downloaded_{hashlib.md5(cover_path.encode()).hexdigest()[:8]}.jpg"
                            download_dir = Path(settings.UPLOAD_DIR)
                            download_dir.mkdir(parents=True, exist_ok=True)
                            cover_path = str(download_dir / filename)
                            
                            # 保存图片
                            with open(cover_path, 'wb') as f:
                                f.write(response.content)
                            
                            logger.info(f"封面图下载成功: {cover_path}")
                    except Exception as download_error:
                        logger.error(f"下载封面图失败: {download_error}")
                        cover_path = None
                else:
                    # 本地文件路径处理
                    if not Path(cover_path).is_absolute():
                        # 相对路径，需要转换为绝对路径
                        # 如果路径已经包含 uploads/ 前缀，直接使用项目根目录作为基准
                        if cover_path.startswith('uploads/'):
                            # 从项目根目录开始
                            project_root = Path(__file__).parent.parent.parent.parent  # backend/app/api -> backend
                            cover_path = str(project_root / cover_path)
                        else:
                            # 其他相对路径，使用 UPLOAD_DIR 作为基准
                            cover_path = str(Path(settings.UPLOAD_DIR) / cover_path)
                    
                    logger.info(f"转换后的封面图绝对路径: {cover_path}")

                # 检查文件是否存在
                if cover_path and Path(cover_path).exists():
                    cover_media_id = await wechat_service.upload_permanent_material(
                        access_token=access_token,
                        media_type="thumb",
                        file_path=cover_path,
                        description={"introduction": article.summary or article.title}
                    )
                    logger.info(f"封面图上传成功: {cover_media_id}")
                    cover_source = "article_cover"
                else:
                    logger.warning(f"[{trace_id}] 封面图文件不存在: {cover_path}")
            except Exception as img_error:
                logger.warning(f"[{trace_id}] 上传文章封面图失败: {str(img_error)}")

        if not cover_media_id:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "封面图上传失败",
                    "message": "微信草稿封面上传失败，已阻止使用默认蓝底封面以避免与文章封面不一致。",
                    "guide": "请检查文章封面图路径/格式（建议 JPG/PNG）并重新发布。",
                    "trace_id": trace_id,
                }
            )

        # 5. 创建草稿
        stage = "create_draft"
        try:
            # 转换 Markdown 为 HTML（优先高级转换）
            html_content, format_engine = await _convert_markdown_to_wechat_html(article.content)
            logger.info(f"[{trace_id}] 文章内容已转换为 HTML，转换器: {format_engine}，长度: {len(html_content)} 字符")

            # 重写正文图片为微信可访问URL
            stage = "rewrite_content_images"
            html_content, image_stats = await _rewrite_html_images_for_wechat(
                html_content=html_content,
                access_token=access_token,
                trace_id=trace_id,
            )
            logger.info(f"[{trace_id}] 正文图片重写完成: total={image_stats['total']}, replaced={image_stats['replaced']}, failed={image_stats['failed']}")

            stage = "create_draft"
            
            # 微信标题限制64字符
            title = article.title[:64] if len(article.title) > 64 else article.title
            
            draft_id = await wechat_service.create_draft(
                access_token=access_token,
                title=title,
                author="拾贝猫",
                digest=article.summary or "",
                content=html_content,
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
                        "guide": "请检查网络连接和代理设置",
                        "trace_id": trace_id,
                        "stage": stage,
                    }
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "创建草稿失败",
                        "message": error_msg,
                        "guide": "请检查文章内容是否符合微信公众号规范",
                        "trace_id": trace_id,
                        "stage": stage,
                    }
                )

        # 6. 更新文章状态
        stage = "update_article_status"
        from ..models.article import ArticleStatus
        article.wechat_draft_id = draft_id
        article.status = ArticleStatus.PUBLISHED
        await db.commit()

        logger.info(f"[{trace_id}] 文章发布成功，草稿ID: {draft_id}")

        return {
            "success": True,
            "message": "发布到微信草稿箱成功",
            "draft_id": draft_id,
            "article_id": article_id,
            "cover_source": cover_source,
            "format_engine": format_engine,
            "image_rewrite": image_stats,
            "trace_id": trace_id,
            "stage": "done",
        }

    except HTTPException as he:
        detail = he.detail
        if isinstance(detail, dict):
            detail.setdefault("trace_id", trace_id)
            detail.setdefault("stage", stage)
            raise HTTPException(status_code=he.status_code, detail=detail)
        raise HTTPException(
            status_code=he.status_code,
            detail={
                "error": "发布失败",
                "message": str(detail),
                "trace_id": trace_id,
                "stage": stage,
            },
        )
    except Exception as e:
        logger.error(f"[{trace_id}] 发布到微信失败: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "发布失败",
                "message": str(e),
                "guide": "请稍后重试，如问题持续请联系技术支持",
                "trace_id": trace_id,
                "stage": stage,
            }
        )

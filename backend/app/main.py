from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import Any
import time
from pathlib import Path
import json

from .core.config import settings
from .core.logger import logger
from .core.database import init_db, close_db
from .models import *  # 导入所有模型以注册到 Base.metadata
from .api import articles, news, unified_ai, wechat, config, health, hotspots, templates, charts, creator, ai_streaming, publish, multiplatform, unified_ai_advanced
from .api.unified_ai import providers_alias_router
from .services.unified_ai_service import (
    unified_ai_service,
    AIProviderError,
    NoAvailableProviderError
)
from .services.memory_cache import initialize_caches, close_caches
from .services.async_task_queue import initialize_task_queue, close_task_queue
from .services.stats_sync_service import initialize_stats_sync, close_stats_sync


class CustomJSONResponse(JSONResponse):
    """自定义JSON响应，支持中文显示"""
    
    def render(self, content: Any) -> bytes:
        # 使用标准json，确保中文不被转义
        # orjson虽然更快但不支持ensure_ascii参数
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理器"""
    # 启动
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()
    logger.info("数据库初始化完成")

    # 初始化AI服务
    await unified_ai_service.initialize()
    logger.info("AI服务初始化完成")

    # 初始化缓存服务
    await initialize_caches()
    logger.info("缓存服务初始化完成")

    # 初始化任务队列
    await initialize_task_queue()
    logger.info("任务队列初始化完成")

    # 初始化统计同步服务（1小时同步一次）
    await initialize_stats_sync()
    logger.info("统计同步服务初始化完成")

    yield

    # 关闭
    logger.info("关闭应用...")
    await unified_ai_service.close()
    await close_task_queue()
    await close_stats_sync()
    await close_caches()
    await close_db()
    logger.info("所有服务已关闭")


# 自定义JSON编码器
def custom_json_encoder(obj):
    """自定义JSON编码器"""
    return jsonable_encoder(obj)


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI驱动的微信公众号内容生成与发布系统 - 个人商用版",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    default_response_class=CustomJSONResponse  # 使用自定义JSON响应类
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有请求和响应时间"""
    start_time = time.time()

    # 记录请求
    logger.info(f"{request.method} {request.url.path}")

    # 处理请求
    response = await call_next(request)

    # 记录响应
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - 状态: {response.status_code} - 耗时: {process_time:.3f}s")

    # 添加处理时间到响应头
    response.headers["X-Process-Time"] = str(process_time)

    return response


# AI服务异常处理器
@app.exception_handler(NoAvailableProviderError)
async def no_provider_handler(request: Request, exc: NoAvailableProviderError):
    """处理无可用提供商异常"""
    logger.error(f"无可用AI提供商: {str(exc)}")
    return CustomJSONResponse(
        status_code=503,
        content={
            "detail": "AI服务暂时不可用",
            "error": "没有配置可用的AI提供商，请检查配置",
            "type": "no_available_provider"
        }
    )


@app.exception_handler(AIProviderError)
async def ai_provider_error_handler(request: Request, exc: AIProviderError):
    """处理AI提供商错误"""
    logger.error(f"AI提供商错误: {str(exc)}")
    return CustomJSONResponse(
        status_code=503,
        content={
            "detail": "AI服务调用失败",
            "error": str(exc) if settings.DEBUG else "AI服务暂时不可用，请稍后重试",
            "type": "ai_provider_error"
        }
    )


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)

    return CustomJSONResponse(
        status_code=500,
        content={
            "detail": "内部服务器错误",
            "error": str(exc) if settings.DEBUG else "发生错误，请稍后重试"
        }
    )


# 注册路由
app.include_router(health.router, prefix="/api/health", tags=["健康检查"])
app.include_router(articles.router, prefix="/api/articles", tags=["文章管理"])
app.include_router(news.router, prefix="/api/news", tags=["新闻热点"])
app.include_router(wechat.router, prefix="/api/wechat", tags=["微信集成"])
app.include_router(unified_ai.router, prefix="/api/ai", tags=["AI服务"])
app.include_router(unified_ai_advanced.router, prefix="/api/ai/advanced", tags=["AI服务-进阶"])
app.include_router(ai_streaming.router, prefix="/api/ai-stream", tags=["AI流式服务"])
app.include_router(providers_alias_router, prefix="/api/unified-ai", tags=["AI服务-兼容"])
app.include_router(config.router, prefix="/api/config", tags=["配置管理"])
app.include_router(hotspots.router, prefix="/api/hotspots", tags=["热门话题"])
app.include_router(templates.router, prefix="/api/templates", tags=["模板管理"])
app.include_router(charts.router, prefix="/api/charts", tags=["数据图表"])
app.include_router(creator.router, prefix="/api/creator", tags=["自媒体工具"])
app.include_router(publish.router, prefix="/api/publish", tags=["多平台发布"])
app.include_router(multiplatform.router, prefix="/api/multiplatform", tags=["多平台发布-Mixpost"])

# 挂载静态文件服务（用于提供上传的图片）
uploads_dir = Path(settings.UPLOAD_DIR)
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
logger.info(f"静态文件服务已挂载: /uploads -> {uploads_dir.absolute()}")


# 根端点
@app.get("/")
async def root():
    """根端点"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }
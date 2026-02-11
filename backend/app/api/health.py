from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..core.database import get_db
from ..core.logger import logger
from ..core.config import settings

router = APIRouter()


@router.get("/")
async def health_check():
    """基础健康检查"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@router.get("/database")
async def database_health(db: AsyncSession = Depends(get_db)):
    """检查数据库连接"""
    try:
        # 测试数据库连接
        await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"数据库健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@router.get("/services")
async def services_health():
    """检查所有外部服务"""
    services = {
        "database": False,
        "openai": bool(settings.OPENAI_API_KEY),
        "deepseek": bool(settings.DEEPSEEK_API_KEY),
        "wechat": bool(settings.WECHAT_APP_ID and settings.WECHAT_APP_SECRET)
    }

    # 检查数据库
    try:
        from ..core.database import engine
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        services["database"] = True
    except:
        pass

    return {
        "status": "ok",
        "services": services
    }
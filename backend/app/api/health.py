from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from ..core.logger import logger
from ..core.config import settings

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@router.get("/database")
async def database_health(db: AsyncSession = Depends(get_db)):
    """Check database connection."""
    try:
        # Test database connection
        await db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@router.get("/services")
async def services_health():
    """Check all external services."""
    services = {
        "database": False,
        "redis": False,
        "openai": bool(settings.OPENAI_API_KEY),
        "deepseek": bool(settings.DEEPSEEK_API_KEY),
        "claude": bool(settings.CLAUDE_API_KEY),
        "gemini": bool(settings.GEMINI_API_KEY),
        "wechat": bool(settings.WECHAT_APP_ID and settings.WECHAT_APP_SECRET)
    }

    # Try to check database
    try:
        from ..core.database import engine
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        services["database"] = True
    except:
        pass

    # Try to check Redis
    try:
        import redis.asyncio as redis
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()
        services["redis"] = True
    except:
        pass

    return {
        "status": "ok",
        "services": services
    }
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from .config import settings
import os

# 确保 SQLite 数据库目录存在
# 处理不同格式的SQLite URL: sqlite:/// 或 sqlite+aiosqlite:///
db_url = settings.DATABASE_URL
if ":///" in db_url:
    db_path = db_url.split(":///")[1]
else:
    db_path = db_url
if db_path:
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

# 创建 SQLite 异步引擎
# 注意：SQLite不支持pool_size和max_overflow参数
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_recycle=settings.DB_POOL_RECYCLE if hasattr(settings, 'DB_POOL_RECYCLE') else 3600,
    pool_pre_ping=True,
)

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 创建模型基类
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖函数
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncSession:
    """
    获取数据库会话（用于非依赖注入场景）
    """
    async with async_session_maker() as session:
        yield session


async def init_db() -> None:
    """
    初始化数据库表
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    关闭数据库连接
    """
    await engine.dispose()
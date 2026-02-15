"""
数据库初始化脚本
创建所有数据库表
"""
import asyncio
from app.core.database import init_db, close_db
from app.core.logger import logger

# 导入所有模型以确保 Base.metadata 包含所有表定义
from app.models import (
    Article, ArticleStatus,
    NewsItem, NewsSource,
    WeChatConfig,
    AppConfig,
    Template,
    Hotspot,
    Task, TaskType, TaskStatus,
    BatchJob, BatchJobType, BatchJobStatus,
    AIProviderConfig,
    ImageProviderConfig
)


async def main():
    """主函数"""
    logger.info("开始初始化数据库...")

    try:
        # 初始化数据库表
        await init_db()
        logger.info("数据库表创建成功！")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise
    finally:
        # 关闭数据库连接
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
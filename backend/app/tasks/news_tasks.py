from celery import Task
from datetime import datetime, timedelta
from ..celery_app import celery_app
from ..services.news_fetcher import news_fetcher_service
from ..services.logging_service import logging_service
from ..core.database import get_db
from ..core.logger import logger


class DatabaseTask(Task):
    """Base task with database session."""
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_db().__anext__()
        return self._db


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.news_tasks.fetch_all_news")
def fetch_all_news(self):
    """Fetch news from all sources."""
    logger.info("Starting fetch_all_news task")

    try:
        # Create task
        task = logging_service.create_task(
            task_type="news_fetch",
            task_name="Fetch all news from all sources",
            db=self.db
        )

        # Update status to running
        logging_service.update_task_status(
            task.id,
            "running",
            progress=10,
            db=self.db
        )

        # Fetch news
        news_items = news_fetcher_service.fetch_all_news(limit_per_source=50)

        # Update progress
        logging_service.update_task_status(
            task.id,
            "running",
            progress=80,
            db=self.db
        )

        # Log result
        logging_service.add_task_log(
            task.id,
            "info",
            f"Successfully fetched {len(news_items)} news items",
            {"count": len(news_items)},
            db=self.db
        )

        # Mark as complete
        logging_service.update_task_status(
            task.id,
            "success",
            progress=100,
            result={"count": len(news_items)},
            db=self.db
        )

        logger.info(f"fetch_all_news task completed: {len(news_items)} items")
        return {"count": len(news_items)}

    except Exception as e:
        logger.error(f"Error in fetch_all_news task: {str(e)}")
        logging_service.update_task_status(
            task.id,
            "failed",
            error_message=str(e),
            db=self.db
        )
        raise


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.news_tasks.fetch_hot_topics")
def fetch_hot_topics(self):
    """Fetch hot topics from all sources."""
    logger.info("Starting fetch_hot_topics task")

    try:
        # Create task
        task = logging_service.create_task(
            task_type="hot_topics_fetch",
            task_name="Fetch hot topics",
            db=self.db
        )

        # Update status
        logging_service.update_task_status(
            task.id,
            "running",
            progress=10,
            db=self.db
        )

        # Fetch hot news
        hot_news = news_fetcher_service.fetch_all_news(limit_per_source=20)

        # Filter top hot topics
        top_topics = sorted(hot_news, key=lambda x: x.hot_score, reverse=True)[:50]

        # Update progress
        logging_service.update_task_status(
            task.id,
            "running",
            progress=80,
            db=self.db
        )

        # Log result
        logging_service.add_task_log(
            task.id,
            "info",
            f"Successfully fetched {len(top_topics)} hot topics",
            {"count": len(top_topics)},
            db=self.db
        )

        # Mark as complete
        logging_service.update_task_status(
            task.id,
            "success",
            progress=100,
            result={"count": len(top_topics)},
            db=self.db
        )

        logger.info(f"fetch_hot_topics task completed: {len(top_topics)} topics")
        return {"count": len(top_topics)}

    except Exception as e:
        logger.error(f"Error in fetch_hot_topics task: {str(e)}")
        logging_service.update_task_status(
            task.id,
            "failed",
            error_message=str(e),
            db=self.db
        )
        raise
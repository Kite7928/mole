from celery import Task
from datetime import datetime, timedelta
from ..celery_app import celery_app
from ..services.wechat_service import wechat_service
from ..services.logging_service import logging_service
from ..core.database import get_db
from ..core.logger import logger
from sqlalchemy import select, desc
from ..models.article import Article, ArticleStatus


class DatabaseTask(Task):
    """Base task with database session."""
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_db().__anext__()
        return self._db


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.wechat_tasks.publish_scheduled_articles")
def publish_scheduled_articles(self):
    """Publish scheduled articles to WeChat."""
    logger.info("Starting publish_scheduled_articles task")

    try:
        # Create task
        task = logging_service.create_task(
            task_type="wechat_publish",
            task_name="Publish scheduled articles",
            db=self.db
        )

        # Get articles ready to publish
        result = await self.db.execute(
            select(Article)
            .where(Article.status == ArticleStatus.READY)
            .where(Article.scheduled_publish_at <= datetime.utcnow())
            .order_by(Article.scheduled_publish_at.asc())
            .limit(10)
        )

        articles = result.scalars().all()

        if not articles:
            logging_service.add_task_log(
                task.id,
                "info",
                "No articles to publish",
                db=self.db
            )
            logging_service.update_task_status(
                task.id,
                "success",
                progress=100,
                result={"published": 0},
                db=self.db
            )
            return {"published": 0}

        published_count = 0

        for article in articles:
            try:
                # Publish article
                publish_result = await wechat_service.publish_article(article.wechat_draft_id)

                # Update article status
                article.status = ArticleStatus.PUBLISHED
                article.published_at = datetime.utcnow()
                article.wechat_article_id = publish_result.get("article_id")

                published_count += 1

                logging_service.add_task_log(
                    task.id,
                    "info",
                    f"Published article: {article.title}",
                    {"article_id": article.id},
                    db=self.db
                )

            except Exception as e:
                logger.error(f"Error publishing article {article.id}: {str(e)}")
                logging_service.add_task_log(
                    task.id,
                    "error",
                    f"Failed to publish article {article.id}: {str(e)}",
                    {"article_id": article.id},
                    db=self.db
                )

        # Mark task as complete
        logging_service.update_task_status(
            task.id,
            "success",
            progress=100,
            result={"published": published_count},
            db=self.db
        )

        logger.info(f"publish_scheduled_articles task completed: {published_count} articles")
        return {"published": published_count}

    except Exception as e:
        logger.error(f"Error in publish_scheduled_articles task: {str(e)}")
        logging_service.update_task_status(
            task.id,
            "failed",
            error_message=str(e),
            db=self.db
        )
        raise
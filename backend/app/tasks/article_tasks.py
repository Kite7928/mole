from celery import Task
from datetime import datetime, timedelta
from ..celery_app import celery_app
from ..services.ai_writer import ai_writer_service
from ..services.image_service import image_service
from ..services.wechat_service import wechat_service
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


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.article_tasks.auto_generate_article")
def auto_generate_article(self, topic: str, source: str = "auto"):
    """Automatically generate an article."""
    logger.info(f"Starting auto_generate_article task for topic: {topic}")

    try:
        # Create task
        task = logging_service.create_task(
            task_type="article_generation",
            task_name=f"Auto generate article: {topic}",
            config={"topic": topic, "source": source},
            db=self.db
        )

        # Step 1: Generate titles (10%)
        logging_service.update_task_status(
            task.id,
            "running",
            progress=10,
            db=self.db
        )
        titles = await ai_writer_service.generate_titles(topic, count=5)
        selected_title = titles[0]["title"]

        # Step 2: Generate content (30%)
        logging_service.update_task_status(
            task.id,
            "running",
            progress=30,
            db=self.db
        )
        content = await ai_writer_service.generate_content(
            topic=topic,
            title=selected_title,
            style="professional",
            length="medium",
            enable_research=True
        )

        # Step 3: Generate cover image (50%)
        logging_service.update_task_status(
            task.id,
            "running",
            progress=50,
            db=self.db
        )
        cover_image_url = await image_service.search_cover_image(topic)

        # Step 4: Create WeChat draft (80%)
        logging_service.update_task_status(
            task.id,
            "running",
            progress=80,
            db=self.db
        )
        draft_result = await wechat_service.create_draft([{
            "title": selected_title,
            "author": "AI Writer",
            "digest": content.get("summary"),
            "content": content.get("content"),
            "thumb_media_id": cover_image_url,
        }])

        # Step 5: Complete (100%)
        logging_service.update_task_status(
            task.id,
            "success",
            progress=100,
            result={
                "title": selected_title,
                "draft_id": draft_result.get("media_id"),
                "cover_image": cover_image_url
            },
            db=self.db
        )

        logger.info(f"auto_generate_article task completed: {selected_title}")
        return {
            "title": selected_title,
            "draft_id": draft_result.get("media_id")
        }

    except Exception as e:
        logger.error(f"Error in auto_generate_article task: {str(e)}")
        logging_service.update_task_status(
            task.id,
            "failed",
            error_message=str(e),
            db=self.db
        )
        raise
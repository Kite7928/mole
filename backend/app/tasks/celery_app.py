from celery import Celery
from celery.schedules import crontab
from ..core.config import settings
from ..core.logger import logger

# Create Celery app
celery_app = Celery(
    "wechat_ai_writer",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.news_tasks",
        "app.tasks.article_tasks",
        "app.tasks.wechat_tasks",
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    # Fetch news every 4 hours
    "fetch-news-every-4-hours": {
        "task": "app.tasks.news_tasks.fetch_all_news",
        "schedule": crontab(hour="*/4"),
    },

    # Fetch hot topics every hour
    "fetch-hot-topics-hourly": {
        "task": "app.tasks.news_tasks.fetch_hot_topics",
        "schedule": crontab(minute=0),
    },

    # Publish scheduled articles at 9 AM
    "publish-scheduled-articles": {
        "task": "app.tasks.wechat_tasks.publish_scheduled_articles",
        "schedule": crontab(hour=9, minute=0),
    },

    # Clean up old logs daily at 2 AM
    "cleanup-old-logs": {
        "task": "app.tasks.maintenance_tasks.cleanup_old_logs",
        "schedule": crontab(hour=2, minute=0),
    },
}

logger.info("Celery app configured successfully")
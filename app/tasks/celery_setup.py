from celery import Celery

from app.config import settings

celery = Celery(
    "tasks",
    broker=settings.redis_url,
    include=["app.tasks.tasks"]
)

from celery import Celery

from app.config import settings

# Configuring the Celery, using redis as a broker
celery = Celery("tasks", broker=settings.redis_url, include=["app.tasks.tasks"])

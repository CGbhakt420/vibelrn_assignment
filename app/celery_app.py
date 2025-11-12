import platform
from celery import Celery
from app.database.config import settings

celery_app = Celery(
    "reviews_app",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Automatically switch to solo pool on Windows
if platform.system() == "Windows":
    celery_app.conf.worker_pool = "solo"

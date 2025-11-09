# app/core/celery_app.py
import platform

from celery import Celery

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger("Celery")

celery_app = Celery(
    "skillstack",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    broker_url=settings.REDIS_URL,
    result_backend=settings.REDIS_URL,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_time_limit=600,
)

# 👇 Automatically adjust for Windows
if platform.system().lower() == "windows":
    celery_app.conf.worker_pool = "solo"
    logger.warning("⚠️ Running Celery in 'solo' mode (Windows detected).")

logger.info("✅ Celery initialized successfully.")

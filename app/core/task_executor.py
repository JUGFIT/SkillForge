# app/core/task_executor.py
import threading
import logging
from fastapi import BackgroundTasks
from app.core.config import settings

logger = logging.getLogger(__name__)

USE_CELERY = getattr(settings, "USE_CELERY", False)

try:
    from app.core.celery_app import celery_app
except ImportError:
    celery_app = None


def enqueue(task_fn, *args, bg: BackgroundTasks = None, **kwargs):
    """
    Unified background task enqueuer — Celery if available, else FastAPI/Thread.
    """
    task_name = getattr(task_fn, "__name__", str(task_fn))

    if USE_CELERY and celery_app:
        try:
            celery_app.send_task(task_fn.__name__, args=args, kwargs=kwargs)
            logger.info(f"📦 Celery task queued: {task_name}")
            return
        except Exception as e:
            logger.warning(f"⚠️ Celery unavailable, falling back: {e}")

    # Fallback: FastAPI BackgroundTasks or Thread
    if bg:
        bg.add_task(task_fn, *args, **kwargs)
        logger.debug(f"🌀 BackgroundTasks scheduled: {task_name}")
    else:
        threading.Thread(
            target=task_fn, args=args, kwargs=kwargs, daemon=True
        ).start()
        logger.debug(f"🧵 Threaded background job launched: {task_name}")


def background_task(func):
    """
    Decorator to mark a function as enqueueable task.
    """
    def wrapper(*args, **kwargs):
        enqueue(func, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

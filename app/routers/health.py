# app/routers/health.py
from fastapi import APIRouter
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import time

from app.core.database import SessionLocal
from app.core.cache import redis_health
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["System"])


@router.get("/")
def health_check():
    """
    Comprehensive system health check.
    Verifies database, Redis, and Celery (if enabled).
    Returns uptime-friendly JSON status with latency metrics.
    """

    start_time = time.time()
    db_status = "unknown"
    redis_status = "unknown"
    celery_status = "disabled" if not settings.USE_CELERY else "unknown"

    # --- Check Database ---
    db = SessionLocal()
    try:
        db.execute("SELECT 1")
        db_status = "ok"
    except SQLAlchemyError:
        db_status = "error"
    finally:
        db.close()

    # --- Check Redis ---
    try:
        redis_ok = redis_health()
        redis_status = "ok" if redis_ok else "error"
    except Exception:
        redis_status = "error"

    # --- Check Celery (if enabled) ---
    if settings.USE_CELERY:
        try:
            from app.core.task_executor import celery_app

            result = celery_app.control.ping(timeout=1)
            celery_status = "ok" if result else "error"
        except Exception:
            celery_status = "error"

    # --- Compute total response time ---
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    # --- Response ---
    return {
        "status": (
            "ok"
            if all(
                s == "ok" or s == "disabled"
                for s in [db_status, redis_status, celery_status]
            )
            else "degraded"
        ),
        "services": {
            "database": db_status,
            "redis": redis_status,
            "celery": celery_status,
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "elapsed_ms": elapsed_ms,
            "environment": settings.APP_ENV,
            "service": "SkillStack 2.0 API",
        },
    }

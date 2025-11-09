# app/tasks/background_tasks.py
from app.core.celery_app import celery_app
from app.core.logging_config import get_logger
from app.utils.roadmap_utils import normalize_positions
from app.core.database import SessionLocal

logger = get_logger("BackgroundTasks")


@celery_app.task(name="normalize_roadmap_steps")
def normalize_roadmap_steps_task(roadmap_id: str):
    """
    Asynchronous normalization for roadmap steps.
    Useful after deletions, reorders, or bulk updates.
    """
    logger.info(f"🌀 Starting roadmap normalization for roadmap {roadmap_id}")
    db = SessionLocal()
    try:
        normalize_positions(db, roadmap_id)
        logger.info(f"✅ Normalized roadmap {roadmap_id} successfully.")
    except Exception as e:
        logger.error(f"❌ Error during normalization for {roadmap_id}: {e}")
    finally:
        db.close()

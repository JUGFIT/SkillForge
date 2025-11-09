# app/tasks/normalize_tasks.py
import logging
from app.core.database import SessionLocal
from app.utils.roadmap_utils import normalize_positions
from app.core.cache import redis_lock

logger = logging.getLogger(__name__)

def normalize_roadmap_task(roadmap_id: str):
    """Safe roadmap normalization job — isolated session + lock."""
    lock_key = f"lock:roadmap:{roadmap_id}"
    with redis_lock(lock_key, ttl=15):
        try:
            with SessionLocal() as db:
                normalize_positions(db, roadmap_id)
                db.commit()
            logger.info(f"✅ Normalized roadmap {roadmap_id}")
        except Exception as e:
            logger.exception(f"❌ Normalization failed for {roadmap_id}: {e}")

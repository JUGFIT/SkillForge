# app/utils/crud_helpers.py
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.schemas import TaskAnalyticsResponse
from app.utils.cache import cache_set


def clear_user_cache(user_id: UUID):
    """Invalidate cached analytics overview for a user."""
    try:
        cache_set(f"analytics:overview:{user_id}", None, expire_seconds=0)
    except Exception as e:
        print(f"[Cache Warning] Could not clear cache for {user_id}: {e}")


def mark_duplicate(db: Session, original_id: UUID, duplicate_id: UUID):
    """Mark one task as a duplicate of another."""
    if original_id == duplicate_id:
        raise HTTPException(status_code=400, detail="A task cannot duplicate itself.")

    original = db.query(models.Task).filter(models.Task.id == original_id).first()
    duplicate = db.query(models.Task).filter(models.Task.id == duplicate_id).first()

    if not original or not duplicate:
        raise HTTPException(status_code=404, detail="One or both tasks not found.")

    existing = (
        db.query(models.TaskDuplicate)
        .filter_by(original_id=original_id, duplicate_id=duplicate_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already marked duplicate.")

    link = models.TaskDuplicate(original_id=original_id, duplicate_id=duplicate_id)
    db.add(link)
    db.commit()

    log_activity(
        db,
        user_id=None,
        task_id=duplicate_id,
        action=f"Marked duplicate of {original.task_key}",
    )
    clear_user_cache(original.project.owner_id if original.project else None)
    return {
        "detail": f"Task {duplicate.task_key} marked as duplicate of {original.task_key}"
    }


def log_activity(db: Session, user_id: UUID, task_id: UUID, action: str):
    """Creates an audit log entry for a given task and user action."""
    log = models.ActivityLog(
        user_id=user_id, task_id=task_id, action=action, timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    if user_id:
        clear_user_cache(user_id)
    return log


# ==============================================================
# 🧠 SMART DUPLICATE DETECTION
# ==============================================================


def detect_possible_duplicates(
    db: Session, project_id: UUID, new_title: str, threshold: int = 80
):
    """
    Uses fuzzy string matching to find similar tasks within the same project.
    Requires: pip install rapidfuzz
    """
    try:
        from rapidfuzz import fuzz
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="RapidFuzz not installed. Run: pip install rapidfuzz",
        )

    existing_tasks = (
        db.query(models.Task).filter(models.Task.project_id == project_id).all()
    )
    if not existing_tasks:
        return []

    results = []
    for t in existing_tasks:
        similarity = fuzz.token_sort_ratio(t.title, new_title)
        if similarity >= threshold:
            results.append(
                {
                    "task_key": t.task_key,
                    "title": t.title,
                    "similarity": similarity,
                }
            )
    return results


def generate_task_key(db: Session, project: models.Project) -> str:
    """Generate sequential task key for a project (e.g. PROJ-001)."""
    prefix = project.name[:4].upper()
    count = db.query(models.Task).filter(models.Task.project_id == project.id).count()
    return f"{prefix}-{count + 1:03d}"

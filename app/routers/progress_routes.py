from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import database
from app.models.activity_log import ActivityLog
from app.models.user_progress import UserProgress
from app.schemas.progress import (UserProgressCreate, UserProgressResponse,
                                  UserProgressUpdate)
from app.services.notifications import create_notification
from app.services.progress_engine import update_user_progress
from app.utils.auth import get_current_user

router = APIRouter(prefix="/progress", tags=["Progress Tracking"])


def log_activity(db, user_id: UUID, action: str, details: str):
    entry = ActivityLog(user_id=user_id, action=action, details=details)
    db.add(entry)
    db.commit()


# ------------------------------------------------------
# 1️⃣ Start Progress Tracking
# ------------------------------------------------------
@router.post(
    "/start", response_model=UserProgressResponse, status_code=status.HTTP_201_CREATED
)
def start_progress(
    payload: UserProgressCreate,
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user),
):
    existing = (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == current_user.id,
            UserProgress.roadmap_id == payload.roadmap_id,
            UserProgress.concept_id == payload.concept_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Progress already exists for this roadmap/concept."
        )

    progress = UserProgress(
        user_id=current_user.id,
        roadmap_id=payload.roadmap_id,
        concept_id=payload.concept_id,
        progress_percent=payload.progress_percent or 0.0,
        notes=payload.notes or {},
    )
    db.add(progress)
    db.commit()
    db.refresh(progress)

    log_activity(
        db,
        current_user.id,
        "progress_started",
        f"Started tracking progress for roadmap {payload.roadmap_id}",
    )
    return progress


# ------------------------------------------------------
# 2️⃣ Update Progress (with progress_engine integration)
# ------------------------------------------------------
@router.post("/update", response_model=UserProgressResponse)
def update_progress(
    concept_id: UUID,
    duration_minutes: int,
    understanding_score: float,
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user),
):
    """
    Updates user's progress on a concept using the adaptive engine.
    """
    try:
        result = update_user_progress(
            db, current_user.id, concept_id, duration_minutes, understanding_score
        )
        progress = (
            db.query(UserProgress)
            .filter(
                UserProgress.user_id == current_user.id,
                UserProgress.concept_id == concept_id,
            )
            .first()
        )

        if not progress:
            raise HTTPException(
                status_code=404, detail="No progress record found for this concept"
            )

        progress.progress_percent = result.get(
            "progress_percent", progress.progress_percent
        )
        progress.completed = result.get("completed", progress.completed)
        db.commit()
        db.refresh(progress)

        # Log + notify
        log_activity(
            db,
            current_user.id,
            "progress_updated",
            f"Progress updated to {progress.progress_percent}%",
        )
        if progress.completed:
            create_notification(
                db,
                current_user.id,
                title="🎯 Concept Completed",
                message=f"You completed a concept under roadmap {progress.roadmap_id}!",
            )

        return progress

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------------------------------
# 3️⃣ Get All Progress for Current User
# ------------------------------------------------------
@router.get("/me", response_model=list[UserProgressResponse])
def get_my_progress(
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user),
):
    progress_entries = (
        db.query(UserProgress).filter(UserProgress.user_id == current_user.id).all()
    )
    return progress_entries


# ------------------------------------------------------
# 4️⃣ Get Progress for a Specific Roadmap
# ------------------------------------------------------
@router.get("/{roadmap_id}", response_model=list[UserProgressResponse])
def get_roadmap_progress(
    roadmap_id: UUID,
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user),
):
    progress_entries = (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == current_user.id,
            UserProgress.roadmap_id == roadmap_id,
        )
        .all()
    )
    if not progress_entries:
        raise HTTPException(
            status_code=404, detail="No progress found for this roadmap"
        )

    return progress_entries

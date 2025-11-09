from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import UserProgress, StudySession

XP_PER_MINUTE = 2
STREAK_INTERVAL_HOURS = 36  # 1.5 days


def calculate_xp(duration_minutes: int, understanding_score: float):
    """XP = time * score weight."""
    base_xp = duration_minutes * XP_PER_MINUTE
    multiplier = 1 + (understanding_score / 2)
    return round(base_xp * multiplier, 2)


def update_user_progress(
    db: Session,
    user_id: str,
    concept_id: str,
    duration_minutes: int,
    understanding_score: float,
):
    """Update progress and calculate XP/streak."""
    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id, UserProgress.concept_id == concept_id)
        .first()
    )

    if not progress:
        progress = UserProgress(
            user_id=user_id, concept_id=concept_id, progress=0.0, completed=False
        )
        db.add(progress)

    # Increase progress
    gain = min(0.3 * understanding_score, 1.0 - progress.progress)
    progress.progress += gain
    if progress.progress >= 1.0:
        progress.completed = True

    # Compute XP and streaks
    xp_gained = calculate_xp(duration_minutes, understanding_score)
    now = datetime.utcnow()
    last_session = (
        db.query(StudySession)
        .filter(StudySession.user_id == user_id)
        .order_by(StudySession.created_at.desc())
        .first()
    )
    streak = 1
    if last_session:
        delta = now - last_session.created_at
        if delta < timedelta(hours=STREAK_INTERVAL_HOURS):
            streak += 1

    # Save updated study session
    new_session = StudySession(
        user_id=user_id,
        concept_id=concept_id,
        duration_minutes=duration_minutes,
        understanding_score=understanding_score,
        reflection_notes=f"XP gained: {xp_gained}, streak: {streak}",
    )
    db.add(new_session)
    db.commit()
    db.refresh(progress)

    return {
        "progress": round(progress.progress, 2),
        "completed": progress.completed,
        "xp_gained": xp_gained,
        "streak": streak,
    }

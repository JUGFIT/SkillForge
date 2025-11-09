from datetime import datetime, timedelta

import google.generativeai as genai
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.notification import Notification
from app.models.study_session import StudySession

genai.configure(api_key=settings.GEMINI_API_KEY)


def create_notification(db: Session, user_id: str, title: str, message: str):
    """Store a new notification in the DB."""
    notif = Notification(user_id=user_id, title=title, message=message, is_read=False)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def generate_ai_reflection(user_id: str, recent_sessions: list):
    """Use Gemini 2.5 Flash to analyze recent study sessions."""
    prompt = f"""
    You are a learning coach analyzing this user's last few study sessions:
    {recent_sessions}

    Write a short motivational reflection summary (under 80 words).
    Include:
    - Key improvement area
    - One strength
    - A positive next-step suggestion
    """

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()


def send_study_summary(db: Session, user_id: str):
    """AI-generated reflection and milestone notification."""
    one_day_ago = datetime.utcnow() - timedelta(hours=24)
    recent_sessions = (
        db.query(StudySession)
        .filter(StudySession.user_id == user_id, StudySession.created_at >= one_day_ago)
        .order_by(StudySession.created_at.desc())
        .limit(5)
        .all()
    )

    if not recent_sessions:
        return None

    # Format for AI input
    session_data = [
        {
            "concept_id": str(s.concept_id),
            "duration": s.duration_minutes,
            "score": s.understanding_score,
            "notes": s.reflection_notes,
        }
        for s in recent_sessions
    ]

    ai_message = generate_ai_reflection(user_id, session_data)
    return create_notification(db, user_id, "Daily Learning Reflection", ai_message)

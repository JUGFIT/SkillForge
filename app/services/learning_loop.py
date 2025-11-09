from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.services.progress_engine import update_user_progress
from app.services.notifications import create_notification, generate_ai_reflection
from app.models import StudySession
from app.core.config import settings
import google.generativeai as genai

genai.configure(api_key=settings.GEMINI_API_KEY)

def ai_suggest_next_concept(user_id: str, recent_sessions: list):
    """Use Gemini 2.5 Flash to suggest what the learner should study next."""
    prompt = f"""
    You are a personalized study planner.
    The user recently worked on these concepts: {recent_sessions}.
    Suggest ONE specific next concept or topic to study, and why.
    Keep it concise (<50 words).
    """
    model = genai.GenerativeModel("gemini-2.5-flash")
    res = model.generate_content(prompt)
    return res.text.strip()


def run_learning_loop(db: Session, user_id: str, concept_id: str,
                      duration_minutes: int, understanding_score: float):
    """Main orchestrator: updates progress, reflection, and next-step suggestion."""
    # 1️⃣  Update progress + XP
    result = update_user_progress(db, user_id, concept_id, duration_minutes, understanding_score)

    # 2️⃣  Collect recent sessions
    recent_sessions = (
        db.query(StudySession)
        .filter(StudySession.user_id == user_id)
        .order_by(StudySession.created_at.desc())
        .limit(3)
        .all()
    )
    session_data = [
        {"concept_id": str(s.concept_id), "score": s.understanding_score, "notes": s.reflection_notes}
        for s in recent_sessions
    ]

    # 3️⃣  AI reflection
    reflection = generate_ai_reflection(user_id, session_data)

    # 4️⃣  AI next suggestion
    next_concept = ai_suggest_next_concept(user_id, session_data)

    # 5️⃣  Save as notifications
    create_notification(db, user_id, "Study Reflection", reflection)
    create_notification(db, user_id, "Next Recommended Step", next_concept)

    return {
        "progress": result["progress"],
        "xp_gained": result["xp_gained"],
        "streak": result["streak"],
        "reflection": reflection,
        "next_suggestion": next_concept
    }

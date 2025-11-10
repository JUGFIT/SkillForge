import json

import google.generativeai as genai
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import RoadmapStep, UserProgress

# --- Configure Gemini ---
genai.configure(api_key=settings.GEMINI_API_KEY)


def get_user_learning_context(db: Session, user_id: str):
    """Collect user progress and concept context for AI prompt."""
    progress_data = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()
    roadmap_steps = (
        db.query(RoadmapStep)
        .join(UserProgress, RoadmapStep.roadmap_id == UserProgress.roadmap_id)
        .filter(UserProgress.user_id == user_id)
        .all()
    )

    # Format context summary
    context = {
        "progress_summary": [
            {
                "concept_id": str(p.concept_id),
                "progress": p.progress,
                "completed": p.completed,
            }
            for p in progress_data
        ],
        "roadmap_steps": [
            {
                "concept_id": str(r.concept_id),
                "completed": r.completed,
                "order": r.order_index,
            }
            for r in roadmap_steps
        ],
    }
    return context


def suggest_next_concept(db: Session, user_id: str):
    """Use Gemini to suggest the next concept based on progress."""
    context = get_user_learning_context(db, user_id)
    prompt = f"""
    You are a learning coach.
    Based on this user's current progress data:
    {json.dumps(context, indent=2)}
    Suggest 3 next learning concepts to focus on.
    Respond with JSON like:
    [
      {{ "title": "Next Concept", "reason": "Why relevant" }},
      ...
    ]
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    try:
        # Extract valid JSON
        text = response.text.strip()
        suggestions = json.loads(text)
        return suggestions
    except Exception:
        return [{"title": "Error parsing AI response", "reason": response.text}]

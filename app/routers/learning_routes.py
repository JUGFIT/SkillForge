from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core import database
from app.utils.auth import get_current_user
from app.services.learning_loop import run_learning_loop

router = APIRouter(prefix="/learning", tags=["Learning Intelligence"])

@router.post("/loop")
def execute_learning_loop(
    concept_id: str,
    duration_minutes: int,
    understanding_score: float,
    db: Session = Depends(database.get_db),
    user=Depends(get_current_user),
):
    """Full AI-powered learning loop (progress → reflection → next suggestion)."""
    try:
        data = run_learning_loop(db, user.id, concept_id, duration_minutes, understanding_score)
        return {"user": user.username, **data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

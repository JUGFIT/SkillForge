from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core import database
from app.services.ai_recommendation import suggest_next_concept
from app.utils.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Recommendations"])

@router.get("/recommend")
def recommend_next(user=Depends(get_current_user), db: Session = Depends(database.get_db)):
    try:
        suggestions = suggest_next_concept(db, user.id)
        return {"user": user.username, "recommendations": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

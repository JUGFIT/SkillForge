from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core import database
from app.utils.auth import get_current_user
from app.services.notifications import send_study_summary

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/summary")
def daily_reflection(
    user=Depends(get_current_user), db: Session = Depends(database.get_db)
):
    """Generate and store an AI-based reflection summary."""
    try:
        result = send_study_summary(db, user.id)
        if not result:
            return {"message": "No recent study sessions found."}
        return {"status": "success", "notification": result.message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

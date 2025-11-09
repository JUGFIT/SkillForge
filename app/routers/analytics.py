from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/ping")
def ping_analytics():
    return {"message": "Analytics router active ✅"}

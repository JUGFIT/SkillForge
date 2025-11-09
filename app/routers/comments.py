from fastapi import APIRouter

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.get("/ping")
def ping_comments():
    return {"message": "Comments router active ✅"}

from fastapi import APIRouter

router = APIRouter(prefix="/exports", tags=["Exports"])

@router.get("/ping")
def ping_exports():
    return {"message": "Exports router active ✅"}

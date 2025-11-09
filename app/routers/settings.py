from fastapi import APIRouter

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/")
def get_settings_status():
    return {"message": "Settings route active (placeholder)"}

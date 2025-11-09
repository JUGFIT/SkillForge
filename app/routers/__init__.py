from fastapi import APIRouter

router = APIRouter()

# Import routers one by one *after* router creation to prevent circular imports
from app.routers import (
    analytics,
    auth,
    comments,
    exports,
    projects,
    settings,
    tasks,
    health,
)

# Notifications imported last (to break circular dependency)
from app.routers import notifications

# Include all routers
router.include_router(auth.router)
router.include_router(projects.router)
router.include_router(tasks.router)
router.include_router(comments.router)
router.include_router(analytics.router)
router.include_router(exports.router)
router.include_router(settings.router)
router.include_router(notifications.router)

from fastapi import APIRouter

from app.routers import (
    ai,
    ai_routes,
    analytics,
    auth,
    comments,
    concepts,
    exports,
    health,
    invites,
    learning_routes,
    members,
    notifications,
    progress_routes,
    projects,
    roadmap_steps,
    roadmaps,
    settings,
    tasks,
)

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(tasks.router)
api_router.include_router(roadmaps.router)
api_router.include_router(roadmap_steps.router)
api_router.include_router(concepts.router)
api_router.include_router(progress_routes.router)
api_router.include_router(ai.router)
api_router.include_router(ai_routes.router)
api_router.include_router(learning_routes.router)
api_router.include_router(analytics.router)
api_router.include_router(comments.router)
api_router.include_router(members.router)
api_router.include_router(invites.router)
api_router.include_router(notifications.router)
api_router.include_router(exports.router)
api_router.include_router(settings.router)
api_router.include_router(health.router)

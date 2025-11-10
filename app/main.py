# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.rate_limiter import init_rate_limiter  # ✅ import limiter early
from app.core.startup import on_startup

# Routers
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
    tasks,
)

# -----------------------------------------------------------
# ⚙️ Initialize FastAPI first
# -----------------------------------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

# ✅ Attach rate limiter middleware BEFORE startup
init_rate_limiter(app)


# -----------------------------------------------------------
# 🔄 Lifespan: Startup & Shutdown Hooks
# -----------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles app startup & graceful shutdown events."""
    setup_logging()
    print("🚀 Starting SkillStack 2.0 API...")

    # Initialize any core services or bootstrap data
    on_startup()

    yield  # 🔥 App is running

    print("🧹 SkillStack shutting down gracefully...")


# -----------------------------------------------------------
# 🔌 Include All Routers
# -----------------------------------------------------------
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(comments.router)
app.include_router(notifications.router)
app.include_router(members.router)
app.include_router(invites.router)
app.include_router(ai.router)
app.include_router(ai_routes.router)
app.include_router(progress_routes.router)
app.include_router(learning_routes.router)
app.include_router(analytics.router)
app.include_router(exports.router)
app.include_router(health.router)
app.include_router(roadmaps.router)
app.include_router(roadmap_steps.router)
app.include_router(concepts.router)


# -----------------------------------------------------------
# ✅ Root Endpoint (Health / Welcome)
# -----------------------------------------------------------
@app.get("/", tags=["Health"])
def root():
    """Simple API heartbeat route."""
    return {
        "message": "SkillStack 2.0 API is up and running 🚀",
        "docs_url": "/docs",
        "version": settings.VERSION,
    }


# source .venv/Scripts/activate

# app/core/startup.py
import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal

logger = logging.getLogger("skillstack.startup")


def init_database():
    """
    Runs at FastAPI startup — verifies database connectivity
    and prepares any required preflight checks.
    """
    db = SessionLocal()
    try:
        # ✅ SQLAlchemy 2.0+ requires explicit text() for raw SQL
        db.execute(text("SELECT 1"))
        logger.info("✅ Database connection verified.")
    except SQLAlchemyError as e:
        logger.error(f"❌ Database connection failed: {e}")
    finally:
        db.close()


def on_startup():
    """
    Called by FastAPI on startup.
    Initializes essential subsystems (DB, scheduler, etc.).
    """
    logger.info("🚀 Starting SkillStack 2.0 API...")
    init_database()
    logger.info("✅ Application initialized successfully (no bootstrap admin).")

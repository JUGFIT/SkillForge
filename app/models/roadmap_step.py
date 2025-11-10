# app/models/roadmap_step.py
import logging
import threading
import uuid

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    event,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Session, relationship

from app.core.config import settings
from app.core.database import Base

logger = logging.getLogger(__name__)


class RoadmapStep(Base):
    __tablename__ = "roadmap_steps"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    roadmap_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        nullable=False,
    )
    concept_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("concepts.id", ondelete="SET NULL"),
        nullable=True,
    )

    title = Column(String(200), nullable=False, default="Untitled Step")
    description = Column(Text, nullable=True)
    position = Column(Integer, nullable=False, index=True, default=0)
    estimated_hours = Column(Float, nullable=True)
    resources = Column(Text, nullable=True)

    note = Column(Text, nullable=True)
    completed = Column(Boolean, default=False)

    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    # Relationships
    roadmap = relationship("Roadmap", back_populates="steps", lazy="joined")
    concept = relationship("Concept", back_populates="roadmap_steps", lazy="selectin")

    def __repr__(self):
        return f"<RoadmapStep(title='{self.title}', position={self.position})>"


# ---------------------------------------------------------
# 🧠 Background Normalizer (Thread + Celery)
# ---------------------------------------------------------
def _normalize_background(roadmap_id: str):
    """
    Run normalization in a detached background thread.
    Keeps main thread (API request) non-blocking.
    """
    from app.core.database import SessionLocal
    from app.utils.roadmap_utils import normalize_positions

    try:
        with SessionLocal() as session:
            normalize_positions(session, roadmap_id)
            session.close()
        logger.info(f"✅ Background normalized roadmap {roadmap_id}")
    except Exception as e:
        logger.warning(
            f"⚠️ Background normalization failed for roadmap {roadmap_id}: {e}"
        )


def schedule_background_normalization(roadmap_id: str):
    """
    Fire-and-forget thread OR Celery task depending on configuration.
    Uses Celery when USE_CELERY=true, otherwise fallback to thread.
    """
    if settings.USE_CELERY:
        try:
            from app.tasks.background_tasks import normalize_roadmap_steps_task

            normalize_roadmap_steps_task.delay(str(roadmap_id))
            logger.info(f"📦 Celery normalization task queued for roadmap {roadmap_id}")
        except Exception as e:
            logger.error(
                f"❌ Celery task queue failed for {roadmap_id}, falling back to thread: {e}"
            )
            threading.Thread(
                target=_normalize_background, args=(roadmap_id,), daemon=True
            ).start()
    else:
        threading.Thread(
            target=_normalize_background, args=(roadmap_id,), daemon=True
        ).start()
        logger.debug(
            f"🧵 Thread-based normalization scheduled for roadmap {roadmap_id}"
        )


# ---------------------------------------------------------
# 🧩 Event Hook: defer normalization until flush completes
# ---------------------------------------------------------
@event.listens_for(Session, "after_flush_postexec")
def after_flush_normalize(session, flush_context):
    """Schedule normalization for affected roadmaps asynchronously."""
    from app.models.roadmap_step import RoadmapStep

    affected_roadmap_ids = set()

    # Collect all roadmaps affected by insert/update/delete
    for obj in session.new.union(session.dirty).union(session.deleted):
        if isinstance(obj, RoadmapStep) and obj.roadmap_id:
            affected_roadmap_ids.add(obj.roadmap_id)

    if not affected_roadmap_ids:
        return

    # Schedule async normalization safely
    for rid in affected_roadmap_ids:
        schedule_background_normalization(rid)
        logger.debug(f"🌀 Scheduled normalization for roadmap {rid}")

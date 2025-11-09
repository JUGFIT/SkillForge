import uuid

from sqlalchemy import (TIMESTAMP, Column, Float, ForeignKey, Integer, String,
                        func)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    concept_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("learning_concepts.id", ondelete="CASCADE"),
        nullable=False,
    )
    duration_minutes = Column(Integer, default=0)
    understanding_score = Column(Float, default=0.0)
    reflection_notes = Column(String(500), nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    concept = relationship("LearningConcept", back_populates="study_sessions")
    user = relationship("User", back_populates="study_sessions")

    def __repr__(self):
        return f"<StudySession(user={self.user_id}, concept={self.concept_id}, duration={self.duration_minutes}m)>"

import uuid
from sqlalchemy import Column, ForeignKey, Boolean, Float, TIMESTAMP, func, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    roadmap_id = Column(PG_UUID(as_uuid=True), ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False)
    concept_id = Column(PG_UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True)

    progress_percent = Column(Float, default=0.0)       # 0.0 to 100.0
    completed = Column(Boolean, default=False)
    notes = Column(JSON, default={})
    last_updated = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="progress_entries")
    roadmap = relationship("Roadmap", back_populates="progress_entries")
    concept = relationship("Concept", back_populates="progress_entries")

    def __repr__(self):
        return f"<UserProgress user={self.user_id} concept={self.concept_id} progress={self.progress_percent}%>"

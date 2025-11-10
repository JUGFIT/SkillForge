import uuid

from sqlalchemy import JSON, TIMESTAMP, Column, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class LearningConcept(Base):
    __tablename__ = "learning_concepts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    tags = Column(JSON, default=list)
    difficulty_level = Column(Float, default=1.0)
    prerequisites = Column(JSON, default=list)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    study_sessions = relationship("StudySession", back_populates="concept")
    ai_recommendations = relationship("AIRecommendation", back_populates="concept")

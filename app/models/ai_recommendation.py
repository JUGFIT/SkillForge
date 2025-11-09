import uuid
from sqlalchemy import Column, String, JSON, Float, TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    concept_id = Column(UUID(as_uuid=True), ForeignKey("learning_concepts.id"))
    suggestion_type = Column(String(50))  # e.g., 'concept', 'project', 'task'
    content = Column(JSON, nullable=False)  # structured AI output
    confidence = Column(Float, default=0.0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    concept = relationship("LearningConcept", back_populates="ai_recommendations")

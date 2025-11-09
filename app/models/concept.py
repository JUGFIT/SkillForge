import uuid
from sqlalchemy import Column, String, Text, Boolean, Integer, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Concept(Base):
    __tablename__ = "concepts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(Integer, nullable=True)  # 1–5 scale
    tags = Column(String(200), nullable=True)  # comma-separated tags
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    roadmap_steps = relationship(
        "RoadmapStep",
        back_populates="concept",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    progress_entries = relationship(
        "UserProgress",
        back_populates="concept",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<Concept(title={self.title}, difficulty={self.difficulty})>"

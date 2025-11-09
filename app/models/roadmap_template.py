import uuid

from sqlalchemy import (JSON, TIMESTAMP, Boolean, Column, ForeignKey, String,
                        func)
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class RoadmapTemplate(Base):
    __tablename__ = "roadmap_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(120), nullable=False)
    description = Column(String(500))
    structure = Column(JSON, default=dict)
    is_public = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

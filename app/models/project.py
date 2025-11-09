# app/models/project.py
import uuid
from sqlalchemy import Column, String, Text, Enum, ForeignKey, TIMESTAMP, Boolean, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum("active", "archived", "completed", name="project_status"), default="active")
    visibility = Column(String(20), default="private")
    tags = Column(Text, nullable=True)  # keep as JSON/text if needed, adjust later
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    # relationships
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    owner = relationship("User", backref="owned_projects")

    def __repr__(self):
        return f"<Project(name='{self.name}', owner='{self.owner_id}')>"

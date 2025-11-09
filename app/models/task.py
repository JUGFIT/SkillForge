import uuid

from sqlalchemy import (TIMESTAMP, Column, Enum, ForeignKey, Integer, String,
                        Text, func)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(
        Enum("pending", "in_progress", "completed", name="task_status"),
        default="pending",
    )
    priority = Column(Integer, default=1)
    task_key = Column(String, unique=True, index=True)
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE")
    )
    assignee_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    due_date = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="tasks")
    comments = relationship(
        "Comment", back_populates="task", cascade="all, delete-orphan"
    )


class TaskDuplicate(Base):
    __tablename__ = "task_duplicates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    duplicate_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))

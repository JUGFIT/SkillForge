# app/models/activity_log.py
import uuid

from sqlalchemy import JSON, TIMESTAMP, Column, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ActivityLog(Base):
    """
    Records lifecycle events for projects and their members.
    Examples:
      - member_added / member_removed
      - invite_generated / invite_accepted
      - ownership_transferred
      - project_updated / project_archived
    """

    __tablename__ = "activity_logs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    action = Column(String(50), nullable=False)
    details = Column(Text, nullable=True)
    meta_data = Column(
        JSON, nullable=True, name="metadata"
    )  # 'metadata' is reserved by SQLAlchemy
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    project = relationship("Project", backref="activity_logs")
    user = relationship("User", backref="activity_logs")

    def __repr__(self) -> str:
        return f"<ActivityLog(action='{self.action}', project='{self.project_id}', user='{self.user_id}')>"

# app/models/project_member.py
import uuid

from sqlalchemy import JSON, TIMESTAMP, Column, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    invited_by = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    role = Column(
        String(20), default="member", nullable=False
    )  # owner, admin, member, invitee
    status = Column(
        String(20), default="active", nullable=False
    )  # active, pending, removed

    invite_token_hash = Column(String, nullable=True)
    invite_token_expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    joined_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    meta = Column(JSON, default={})

    # relationship backrefs
    project = relationship("Project", back_populates="members")
    user = relationship(
        "User", back_populates="project_members", foreign_keys=[user_id]
    )

    def __repr__(self):
        return f"<ProjectMember(project_id={self.project_id}, user_id={self.user_id}, role={self.role})>"

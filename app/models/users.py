# app/models/users.py
import uuid
from sqlalchemy import Column, String, Boolean, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String(100), nullable=True)
    bio = Column(String(255), nullable=True)
    profile_image = Column(String, nullable=True)
    role = Column(String(20), default="user")  # global role: user / staff / sysadmin (optional)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    project_members = relationship(
        "ProjectMember",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="ProjectMember.user_id",  
    )

    # refresh_tokens model assumed present (table created by alembic)
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    notifications = relationship(
        "Notification",
        backref="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    study_sessions = relationship(
        "StudySession",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    roadmaps = relationship(
        "Roadmap",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    progress_entries = relationship(
        "UserProgress",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

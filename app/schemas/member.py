# app/schemas/member.py
from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field


class ProjectMemberBase(BaseModel):
    project_id: UUID
    role: Optional[str] = Field(default="member", description="member / owner / admin / invitee")
    status: Optional[str] = Field(default="active")


class ProjectMemberCreate(ProjectMemberBase):
    user_id: Optional[UUID] = None


class ProjectMemberUpdate(BaseModel):
    role: Optional[str] = None
    status: Optional[str] = None


class ProjectMemberResponse(ProjectMemberBase):
    id: UUID
    user_id: Optional[UUID]
    invited_by: Optional[UUID]
    joined_at: Optional[datetime]
    meta: Optional[Any] = None

    class Config:
        from_attributes = True

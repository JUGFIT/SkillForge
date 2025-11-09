from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field


# -----------------------------------------------------------
# 🟢 SHARED ATTRIBUTES
# -----------------------------------------------------------
class ProjectBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = None
    visibility: Optional[str] = Field("private", description="private/public")


# -----------------------------------------------------------
# 🟢 CREATE / UPDATE SCHEMAS
# -----------------------------------------------------------
class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    visibility: Optional[str] = None
    status: Optional[str] = None


# -----------------------------------------------------------
# 🟢 RESPONSE SCHEMA
# -----------------------------------------------------------
class ProjectResponse(ProjectBase):
    id: UUID
    status: Optional[str]
    owner_id: UUID
    is_active: Optional[bool]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# ============================================================
# 🧩 PROJECT MEMBERSHIP SCHEMAS
# ============================================================
class ProjectMemberBase(BaseModel):
    project_id: UUID
    role: Optional[str] = Field(default="member", description="member / owner / viewer")
    status: Optional[str] = Field(default="active", description="Membership status")


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


# ============================================================
# ✉️ INVITE SCHEMAS
# ============================================================

class InviteCreate(BaseModel):
    project_id: UUID
    role: Optional[str] = "member"


class InviteResponse(BaseModel):
    invite_token: str
    expires_at: datetime
    project_id: UUID
    role: str

    class Config:
        from_attributes = True
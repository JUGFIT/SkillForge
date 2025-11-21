# app/schemas/invite.py
from datetime import datetime

from pydantic import BaseModel


class InviteBase(BaseModel):
    email: str
    project_id: int
    role: str = "member"


class InviteCreate(InviteBase):
    pass


class InviteResponse(InviteBase):
    id: int
    token: str
    created_at: datetime
    expires_at: datetime
    used: bool = False

    class Config:
        from_attributes = True

# app/schemas/comment.py
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, constr

# ============================================================
# 💬 COMMENT SCHEMAS
# ============================================================


class CommentBase(BaseModel):
    content: constr(min_length=1, max_length=300)


class CommentCreate(CommentBase):
    task_id: Optional[UUID] = None


class CommentResponse(CommentBase):
    id: UUID
    user_id: UUID
    task_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

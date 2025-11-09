from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NotificationBase(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

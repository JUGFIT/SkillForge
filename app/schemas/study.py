from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class StudySessionCreate(BaseModel):
    user_id: UUID
    roadmap_id: Optional[UUID] = None
    step_id: Optional[UUID] = None
    duration_minutes: int
    notes: Optional[str] = None


class StudySessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    roadmap_id: Optional[UUID]
    step_id: Optional[UUID]
    duration_minutes: int
    notes: Optional[str]
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}

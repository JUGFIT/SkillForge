from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class UserProgressCreate(BaseModel):
    roadmap_id: UUID
    concept_id: Optional[UUID] = None
    progress_percent: Optional[float] = Field(default=0.0, ge=0.0, le=100.0)
    notes: Optional[dict] = None


class UserProgressUpdate(BaseModel):
    progress_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    completed: Optional[bool] = False
    notes: Optional[dict] = None


class UserProgressResponse(BaseModel):
    id: UUID
    user_id: UUID
    roadmap_id: UUID
    concept_id: Optional[UUID]
    progress_percent: float
    completed: bool
    last_updated: datetime
    notes: Optional[dict]

    model_config = {"from_attributes": True}

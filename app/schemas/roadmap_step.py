from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class RoadmapStepBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    position: Optional[int] = 0
    estimated_hours: Optional[float] = None
    resources: Optional[str] = None


class RoadmapStepCreate(RoadmapStepBase):
    roadmap_id: UUID


class RoadmapStepUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    position: Optional[int] = None
    estimated_hours: Optional[float] = None
    resources: Optional[str] = None


class RoadmapStepResponse(BaseModel):
    id: UUID
    roadmap_id: UUID
    title: str
    description: Optional[str]
    position: int
    estimated_hours: Optional[float]
    resources: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}

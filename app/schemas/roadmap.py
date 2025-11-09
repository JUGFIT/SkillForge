from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RoadmapBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    is_public: Optional[bool] = False
    template_id: Optional[UUID] = None


class RoadmapCreate(RoadmapBase):
    pass


class RoadmapUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    template_id: Optional[UUID] = None


class RoadmapStepNested(BaseModel):
    id: UUID
    title: str
    position: int

    model_config = {"from_attributes": True}


class RoadmapResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    owner_id: UUID
    is_public: bool
    template_id: Optional[UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    steps: List[RoadmapStepNested] = []

    model_config = {"from_attributes": True}

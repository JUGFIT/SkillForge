from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ConceptBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    tags: Optional[str] = None
    is_active: bool = True


class ConceptCreate(ConceptBase):
    pass


class ConceptUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    tags: Optional[str] = None
    is_active: Optional[bool] = None


class ConceptResponse(ConceptBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}

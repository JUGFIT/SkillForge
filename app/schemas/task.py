from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    project_id: UUID
    title: str
    description: Optional[str] = None
    priority: Optional[int] = 1
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: UUID
    task_key: Optional[str]
    title: str
    description: Optional[str]
    status: str
    priority: int
    project_id: UUID
    assignee_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

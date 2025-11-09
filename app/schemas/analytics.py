from pydantic import BaseModel


class TaskAnalyticsResponse(BaseModel):
    total: int
    completed: int
    in_progress: int
    pending: int
    completion_rate: str

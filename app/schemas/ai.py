from pydantic import BaseModel, Field
from typing import List, Optional

class AIProjectIdeaRequest(BaseModel):
    user_goal: str = Field(..., example="I want to build a web app to track study habits")
    skill_level: Optional[str] = Field("intermediate", example="beginner / intermediate / advanced")

class AIProjectIdeaResponse(BaseModel):
    title: str
    description: str
    tags: List[str]
    suggested_stack: List[str]

class AIRoadmapRequest(BaseModel):
    project_title: str
    goal: str
    duration_weeks: int = Field(..., example=6)
    skill_level: Optional[str] = Field("intermediate")

class AIRoadmapResponse(BaseModel):
    roadmap_steps: List[str]
    estimated_time_per_week: int
    learning_outcomes: List[str]

class AITaskGenerationRequest(BaseModel):
    project_title: str
    description: str
    roadmap_context: Optional[str] = None

class AITaskResponse(BaseModel):
    tasks: List[str]

class AIQuestionRequest(BaseModel):
    question: str

class AIAnswerResponse(BaseModel):
    answer: str

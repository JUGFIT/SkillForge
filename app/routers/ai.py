from fastapi import APIRouter, HTTPException
from app.schemas.ai import (
    AIProjectIdeaRequest,
    AIProjectIdeaResponse,
    AIRoadmapRequest,
    AIRoadmapResponse,
    AITaskGenerationRequest,
    AITaskResponse,
    AIQuestionRequest,
    AIAnswerResponse,
)
from app.services.ai_service import get_ai_provider

router = APIRouter(prefix="/ai", tags=["AI Assistant"])
ai = get_ai_provider()


@router.post("/idea", response_model=AIProjectIdeaResponse)
def generate_project_idea(req: AIProjectIdeaRequest):
    try:
        result = ai.generate_project_idea(req.user_goal, req.skill_level)
        if isinstance(result, str):
            return AIProjectIdeaResponse(
                title="Generated Project",
                description=result,
                tags=["learning", "ai"],
                suggested_stack=["FastAPI", "React"],
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/roadmap", response_model=AIRoadmapResponse)
def generate_roadmap(req: AIRoadmapRequest):
    try:
        result = ai.generate_roadmap(
            req.project_title, req.goal, req.duration_weeks, req.skill_level
        )
        if isinstance(result, str):
            return AIRoadmapResponse(
                roadmap_steps=result.split("\n"),
                estimated_time_per_week=6,
                learning_outcomes=["Skill growth", "Practical experience"],
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks", response_model=AITaskResponse)
def generate_tasks(req: AITaskGenerationRequest):
    try:
        result = ai.generate_tasks(
            req.project_title, req.description, req.roadmap_context
        )
        if isinstance(result, str):
            return AITaskResponse(tasks=result.split("\n"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask", response_model=AIAnswerResponse)
def ask_ai(req: AIQuestionRequest):
    try:
        result = ai.answer_question(req.question)
        if isinstance(result, str):
            return AIAnswerResponse(answer=result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

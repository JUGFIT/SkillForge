# app/schemas/__init__.py

# === Module-level imports (for schemas.module.Class pattern) ===
from app.schemas import ai, auth, concept, progress, project, roadmap, roadmap_step

# === AI ===
from app.schemas.ai import (
    AIAnswerResponse,
    AIProjectIdeaRequest,
    AIProjectIdeaResponse,
    AIQuestionRequest,
    AIRoadmapRequest,
    AIRoadmapResponse,
    AITaskGenerationRequest,
    AITaskResponse,
)

# === Analytics ===
from app.schemas.analytics import TaskAnalyticsResponse

# === Auth ===
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    TokenPair,
    TokenResponse,
    UserProfile,
)

# === Concept ===
from app.schemas.concept import ConceptCreate, ConceptResponse, ConceptUpdate

# === Progress ===
from app.schemas.progress import (
    UserProgressCreate,
    UserProgressResponse,
    UserProgressUpdate,
)

# === Project (includes Member & Invite schemas) ===
from app.schemas.project import (
    InviteCreate,
    InviteResponse,
    ProjectBase,
    ProjectCreate,
    ProjectMemberBase,
    ProjectMemberCreate,
    ProjectMemberResponse,
    ProjectMemberUpdate,
    ProjectResponse,
    ProjectUpdate,
)

# === Roadmap ===
from app.schemas.roadmap import (
    RoadmapCreate,
    RoadmapResponse,
    RoadmapStepNested,
    RoadmapUpdate,
)

# === Roadmap Step ===
from app.schemas.roadmap_step import (
    RoadmapStepCreate,
    RoadmapStepResponse,
    RoadmapStepUpdate,
)

# === Task ===
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

__all__ = [
    # Modules (for schemas.module access)
    "ai",
    "auth",
    "concept",
    "progress",
    "project",
    "roadmap",
    "roadmap_step",
    # Project
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    # Members
    "ProjectMemberBase",
    "ProjectMemberCreate",
    "ProjectMemberUpdate",
    "ProjectMemberResponse",
    # Invites
    "InviteCreate",
    "InviteResponse",
    # Tasks
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    # Analytics
    "TaskAnalyticsResponse",
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "TokenPair",
    "TokenResponse",
    "RefreshRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "UserProfile",
    "RegisterResponse",
    # Concept
    "ConceptCreate",
    "ConceptUpdate",
    "ConceptResponse",
    # Progress
    "UserProgressCreate",
    "UserProgressUpdate",
    "UserProgressResponse",
    # Roadmap
    "RoadmapCreate",
    "RoadmapUpdate",
    "RoadmapResponse",
    "RoadmapStepNested",
    # Roadmap Step
    "RoadmapStepCreate",
    "RoadmapStepUpdate",
    "RoadmapStepResponse",
    # AI
    "AIProjectIdeaRequest",
    "AIProjectIdeaResponse",
    "AIRoadmapRequest",
    "AIRoadmapResponse",
    "AITaskGenerationRequest",
    "AITaskResponse",
    "AIQuestionRequest",
    "AIAnswerResponse",
]

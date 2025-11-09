# app/models/__init__.py

from app.models.users import User
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.notification import Notification
from app.models.task import Task
from app.models.comment import Comment
from app.models.refresh_token import RefreshToken
from app.models.roadmap import Roadmap
from app.models.roadmap_step import RoadmapStep
from app.models.roadmap_template import RoadmapTemplate  
from app.models.study_session import StudySession
from app.models.user_progress import UserProgress
from app.models.learning_concept import LearningConcept
from app.models.concept import Concept
from app.models.ai_recommendation import AIRecommendation
from app.models.activity_log import ActivityLog

__all__ = [
    "User",
    "Project",
    "ProjectMember",
    "Notification",
    "Task",
    "Comment",
    "RefreshToken",
    "Roadmap",
    "RoadmapStep",
    "RoadmapTemplate",  # ✅ Added to __all__
    "StudySession",
    "UserProgress",
    "LearningConcept",
    "Concept",
    "AIRecommendation",
    "ActivityLog",
]

import requests
import logging
from typing import List
from app.core.config import settings

logger = logging.getLogger("skillstack.ai")


# -------------------- Provider Interfaces --------------------
class AIProvider:
    def generate_project_idea(self, goal: str, skill_level: str):
        raise NotImplementedError

    def generate_roadmap(
        self, title: str, goal: str, duration_weeks: int, skill_level: str
    ):
        raise NotImplementedError

    def generate_tasks(self, title: str, description: str, roadmap_context: str = None):
        raise NotImplementedError

    def answer_question(self, question: str):
        raise NotImplementedError


# -------------------- Gemini Provider --------------------
class GeminiProvider(AIProvider):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def _ask_gemini(self, prompt: str) -> str:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(self.url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            logger.error(f"Gemini response parse error: {e}")
            return "Sorry, I couldn’t understand the AI response."

    def generate_project_idea(self, goal, skill_level):
        prompt = f"Generate a concise project idea for a {skill_level} learner. Goal: {goal}. Include title, short description, and suggested stack."
        return self._ask_gemini(prompt)

    def generate_roadmap(self, title, goal, duration_weeks, skill_level):
        prompt = f"Create a {duration_weeks}-week learning roadmap for project '{title}'. Goal: {goal}. Skill level: {skill_level}. Include weekly milestones and learning outcomes."
        return self._ask_gemini(prompt)

    def generate_tasks(self, title, description, roadmap_context=None):
        context = roadmap_context or ""
        prompt = f"Generate clear actionable development tasks for the project '{title}'. Description: {description}. Context: {context}"
        return self._ask_gemini(prompt)

    def answer_question(self, question):
        prompt = f"Answer concisely and educationally: {question}"
        return self._ask_gemini(prompt)


# -------------------- Mock Provider (for local/dev) --------------------
class MockAIProvider(AIProvider):
    def generate_project_idea(self, goal, skill_level):
        return {
            "title": "Habit Tracker App",
            "description": "A simple app to monitor study sessions and productivity.",
            "tags": ["productivity", "fastapi", "frontend"],
            "suggested_stack": ["FastAPI", "PostgreSQL", "React"],
        }

    def generate_roadmap(self, title, goal, duration_weeks, skill_level):
        return {
            "roadmap_steps": [
                f"Week {i+1}: Learn {topic}"
                for i, topic in enumerate(["FastAPI", "PostgreSQL", "React"])
            ],
            "estimated_time_per_week": 5,
            "learning_outcomes": [
                "REST API basics",
                "Database design",
                "Frontend integration",
            ],
        }

    def generate_tasks(self, title, description, roadmap_context=None):
        return {"tasks": ["Set up backend", "Design UI", "Integrate database"]}

    def answer_question(self, question):
        return {"answer": f"This is a mock answer for: {question}"}


# -------------------- Factory --------------------
def get_ai_provider() -> AIProvider:
    if settings.AI_PROVIDER.lower() == "gemini" and settings.GEMINI_API_KEY:
        logger.info(f"Using Gemini provider ({settings.GEMINI_MODEL})")
        return GeminiProvider()
    logger.info("Using Mock AI provider")
    return MockAIProvider()

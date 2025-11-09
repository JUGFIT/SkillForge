#app/core/config.py :
import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus

# -------------------------------------------------------------------
# 🌍 Load Environment Variables
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    # -------------------------------------------------------------------
    # 🧠 App Information
    # -------------------------------------------------------------------
    PROJECT_NAME: str = os.getenv("APP_NAME", "SkillStack 2.0")
    VERSION: str = "2.0.0"
    DESCRIPTION: str = (
        "Modernized backend for SkillStack — a scalable multi-user, AI-driven learning & project management platform."
    )
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # -------------------------------------------------------------------
    # 🗄️ Database Configuration
    # -------------------------------------------------------------------
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "skillstack")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))

    @property
    def DATABASE_URL(self) -> str:
        """
        Dynamically builds a fully URL-encoded connection string for SQLAlchemy + Alembic.
        Prevents issues with special characters in passwords.
        """
        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)
        db = quote_plus(self.POSTGRES_DB)
        host = self.POSTGRES_HOST
        port = self.POSTGRES_PORT

        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"

    # -------------------------------------------------------------------
    # 🔐 Security & JWT
    # -------------------------------------------------------------------
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret")
    JWT_SECRET_KEY: str = SECRET_KEY
    ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ALGORITHM: str = ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    # -------------------------------------------------------------------
    # 🌐 OAuth (Google)
    # -------------------------------------------------------------------
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")

    # -------------------------------------------------------------------
    # 🤖 AI Configuration
    # -------------------------------------------------------------------
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "1024"))
    AI_RATE_LIMIT_PER_MIN: int = int(os.getenv("AI_RATE_LIMIT_PER_MIN", "10"))

    # -------------------------------------------------------------------
    # ⚙️ Redis & Celery
    # -------------------------------------------------------------------
    USE_CELERY: bool = os.getenv("USE_CELERY", "false").lower() in ("true", "1", "yes")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # -------------------------------------------------------------------
    # 🧩 Logging & Debugging
    # -------------------------------------------------------------------
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # -------------------------------------------------------------------
    # 🧪 Optional: Connection Self-Test
    # -------------------------------------------------------------------
    def test_connections(self):
        """
        Lightweight test to verify connectivity for Postgres and Redis.
        Useful for CI/CD health checks or startup diagnostics.
        """
        from sqlalchemy import create_engine
        import redis

        results = {}
        # Test Postgres
        try:
            engine = create_engine(self.DATABASE_URL)
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            results["postgres"] = "ok"
        except Exception as e:
            results["postgres"] = f"error: {e}"

        # Test Redis
        try:
            r = redis.Redis.from_url(self.REDIS_URL)
            r.ping()
            results["redis"] = "ok"
        except Exception as e:
            results["redis"] = f"error: {e}"

        return results


# ✅ Global instance
settings = Settings()

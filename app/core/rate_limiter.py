# app/core/rate_limiter.py
import logging

from fastapi import FastAPI, Request
from redis import Redis
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.config import settings

# ------------------------------------------------------------------
# ✅ Setup Redis safely (for rate limiter storage)
# ------------------------------------------------------------------
try:
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_client.ping()
    logging.info("✅ Connected to Redis for rate limiting")
except Exception as e:
    redis_client = None
    logging.warning(f"⚠️ Redis unavailable for rate limiting: {e}")

# ------------------------------------------------------------------
# ⚙️ Initialize the global rate limiter
# ------------------------------------------------------------------
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # global fallback
    storage_uri=settings.REDIS_URL if redis_client else "memory://",
)


# ------------------------------------------------------------------
# 🔗 Attach to app
# ------------------------------------------------------------------
def init_rate_limiter(app: FastAPI):
    """Attach SlowAPI limiter middleware and exception handler."""
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ------------------------------------------------------------------
# 🚫 Handle Limit Exceeded
# ------------------------------------------------------------------
def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return request.app.state.limiter._rate_limit_exceeded_handler(request, exc)

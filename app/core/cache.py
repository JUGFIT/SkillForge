# app/core/cache.py
import json
import time
from contextlib import contextmanager

from redis import ConnectionError, Redis, TimeoutError

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


# -------------------------------------------------------------------
# 🚀 Redis Connection Setup (Robust + Retry)
# -------------------------------------------------------------------
def create_redis_connection(retries: int = 5, delay: int = 2) -> Redis:
    """Initialize a resilient Redis client with retry and error handling."""
    for attempt in range(retries):
        try:
            client = Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=5,
                health_check_interval=30,
            )
            # Test connection
            client.ping()
            logger.info("✅ Connected to Redis successfully.")
            return client
        except (ConnectionError, TimeoutError) as e:
            logger.warning(
                f"⚠️ Redis connection failed (attempt {attempt + 1}/{retries}): {e}"
            )
            time.sleep(delay)
    logger.error("❌ Could not connect to Redis after multiple attempts.")
    raise ConnectionError("Redis is not available.")


# Initialize global client
_redis = create_redis_connection()


# -------------------------------------------------------------------
# 🔒 Distributed Lock (Safe for Multi-worker)
# -------------------------------------------------------------------
@contextmanager
def redis_lock(lock_key: str, ttl: int = 10, retry_interval: float = 0.2):
    """
    Redis-based distributed lock using SETNX pattern with TTL.
    Ensures only one process can hold a critical section.
    """
    token = str(time.time())
    acquired = False
    try:
        while not acquired:
            acquired = _redis.set(lock_key, token, nx=True, ex=ttl)
            if not acquired:
                time.sleep(retry_interval)
        yield
    finally:
        try:
            val = _redis.get(lock_key)
            if val == token:
                _redis.delete(lock_key)
        except Exception as e:
            logger.error(f"Failed to release Redis lock {lock_key}: {e}")


# -------------------------------------------------------------------
# ⚡ Caching Utilities (JSON-safe)
# -------------------------------------------------------------------
def cache_get(key: str):
    """Retrieve JSON-deserialized value from Redis cache."""
    try:
        val = _redis.get(key)
        return json.loads(val) if val else None
    except Exception as e:
        logger.error(f"cache_get error for key={key}: {e}")
        return None


def cache_set(key: str, value, ttl: int = 300):
    """Set JSON-serialized value in cache with TTL (default 5 min)."""
    try:
        _redis.setex(key, ttl, json.dumps(value))
    except Exception as e:
        logger.error(f"cache_set error for key={key}: {e}")


def cache_delete(key: str):
    """Delete a cached key safely."""
    try:
        _redis.delete(key)
    except Exception as e:
        logger.error(f"cache_delete error for key={key}: {e}")


# -------------------------------------------------------------------
# 🧠 Health & Utility
# -------------------------------------------------------------------
def redis_health() -> bool:
    """Check if Redis is alive."""
    try:
        return _redis.ping()
    except Exception:
        return False


def get_redis() -> Redis:
    """Return the Redis client (for direct low-level access)."""
    return _redis

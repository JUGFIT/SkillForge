# app/utils/cache.py
import time
import threading

_cache_store = {}
_cache_lock = threading.Lock()


def cache_get(key: str):
    """Retrieve a cached value if not expired."""
    with _cache_lock:
        entry = _cache_store.get(key)
        if not entry:
            return None
        value, expiry = entry
        if expiry and time.time() > expiry:
            del _cache_store[key]
            return None
        return value


def cache_set(key: str, value, expire_seconds: int = 60):
    """Store a value with an optional TTL."""
    expiry = time.time() + expire_seconds if expire_seconds else None
    with _cache_lock:
        _cache_store[key] = (value, expiry)


def cache_clear(key: str):
    """Remove a cache entry."""
    with _cache_lock:
        _cache_store.pop(key, None)


def cache_clear_all():
    """Flush entire cache (admin or debug use)."""
    with _cache_lock:
        _cache_store.clear()

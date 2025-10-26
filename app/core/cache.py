import json
from typing import Any, Optional
import redis
from app.core.config import settings

_redis_client: Optional[redis.Redis] = None

def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client

def cache_get_json(key: str) -> Optional[Any]:
    raw = get_redis().get(key)
    return json.loads(raw) if raw is not None else None

def cache_set_json(key: str, value: Any, ttl_seconds: int) -> None:
    get_redis().setex(key, ttl_seconds, json.dumps(value))

def cache_delete_pattern(pattern: str) -> int:
    r = get_redis()
    total = 0
    for key in r.scan_iter(pattern):
        total += int(r.delete(key))
    return total

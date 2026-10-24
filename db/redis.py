import redis.asyncio as redis

from core.config import settings

redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    health_check_interval=15,
    socket_keepalive=True,
    socket_timeout=10.0,
    socket_connect_timeout=10.0,
    retry_on_timeout=True,
)
"""Async Redis client for refresh token storage."""

import redis.asyncio as redis
import structlog

from app.config import settings

logger = structlog.get_logger()

redis_client: redis.Redis | None = None


async def init_redis() -> None:
    """Initialize the async Redis connection pool."""
    global redis_client
    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )
    # Verify connection
    await redis_client.ping()
    logger.info("Redis connected", url=settings.REDIS_URL)


async def close_redis() -> None:
    """Close the Redis connection pool."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
        logger.info("Redis connection closed")


def get_redis() -> redis.Redis:
    """Return the Redis client instance. Raises if not initialized."""
    if redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return redis_client

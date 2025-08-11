import redis.asyncio as redis
from typing import Optional
from app.core.config import settings


class RedisManager:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        # Create client and verify connectivity; if unreachable, leave unconnected
        client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        try:
            await client.ping()
            self.redis = client
        except Exception:
            # Keep redis as None to signal unavailable; app will gracefully degrade
            self.redis = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
    
    def get_redis(self) -> redis.Redis:
        """Get Redis connection"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        return self.redis


# Global Redis manager instance
redis_manager = RedisManager()

import time
import hashlib
from typing import Optional
from app.core.redis import redis_manager


class RateLimiter:
    """Token bucket rate limiter using Redis"""

    def __init__(self, key_prefix: str, rate: int, per_seconds: int):
        self.key_prefix = key_prefix
        self.rate = rate
        self.per_seconds = per_seconds
        self._memory_store: dict[str, list[float]] = {}
    
    async def allow_request(self, identifier: str) -> bool:
        """Check if request is allowed for given identifier.

        If Redis is not connected, rate limiting is bypassed to keep the
        application functional during tests or development environments.
        """
        try:
            redis = redis_manager.get_redis()
        except RuntimeError:
            # Fallback to in-memory tracking when Redis is unavailable
            now = time.time()
            timestamps = self._memory_store.setdefault(identifier, [])
            # Remove expired timestamps
            while timestamps and timestamps[0] <= now - self.per_seconds:
                timestamps.pop(0)
            if len(timestamps) >= self.rate:
                return False
            timestamps.append(now)
            return True
        key = f"{self.key_prefix}:{identifier}"
        now = time.time()
        
        # Use Redis pipeline for atomic operations
        pipe = redis.pipeline()
        
        # Remove old entries outside the time window
        pipe.zremrangebyscore(key, 0, now - self.per_seconds)
        # Count current requests in window
        pipe.zcard(key)
        # Add current request
        pipe.zadd(key, {str(now): now})
        # Set expiration
        pipe.expire(key, self.per_seconds)
        
        results = await pipe.execute()
        count = results[1]  # Number of requests in current window
        
        return count < self.rate
    
    async def get_remaining_requests(self, identifier: str) -> int:
        """Get number of remaining requests for identifier"""
        redis = redis_manager.get_redis()
        key = f"{self.key_prefix}:{identifier}"
        now = time.time()
        
        # Clean old entries and count current
        await redis.zremrangebyscore(key, 0, now - self.per_seconds)
        count = await redis.zcard(key)
        
        return max(0, self.rate - count)
    
    async def get_reset_time(self, identifier: str) -> Optional[float]:
        """Get timestamp when rate limit resets"""
        redis = redis_manager.get_redis()
        key = f"{self.key_prefix}:{identifier}"
        
        # Get oldest entry in current window
        oldest = await redis.zrange(key, 0, 0, withscores=True)
        if oldest:
            return oldest[0][1] + self.per_seconds
        return None


# Pre-configured rate limiters
class RateLimiters:
    # API rate limits
    api_general = RateLimiter("api_general", rate=100, per_seconds=60)  # 100 req/min
    api_auth = RateLimiter("api_auth", rate=5, per_seconds=300)  # 5 auth attempts per 5 min
    api_expensive = RateLimiter("api_expensive", rate=10, per_seconds=60)  # 10 expensive ops/min
    
    # Global rate limits
    global_api = RateLimiter("global", rate=1000, per_seconds=60)  # 1000 req/min globally

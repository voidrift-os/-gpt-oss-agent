import json
import hashlib
from typing import Any, Optional, Union
from functools import wraps
import logging
from app.core.redis import redis_manager

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis-based caching manager"""
    
    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate a cache key from data"""
        if isinstance(data, (dict, list)):
            serialized = json.dumps(data, sort_keys=True)
        else:
            serialized = str(data)
        
        hash_obj = hashlib.sha256(serialized.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            redis = redis_manager.get_redis()
            cached = await redis.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            redis = redis_manager.get_redis()
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, default=str)
            await redis.set(key, serialized, ex=ttl)
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            redis = redis_manager.get_redis()
            await redis.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            redis = redis_manager.get_redis()
            keys = await redis.keys(pattern)
            if keys:
                return await redis.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache clear pattern error: {e}")
            return 0


# Global cache manager
cache_manager = CacheManager()


def cache_response(
    prefix: str = "cache",
    ttl: int = 300,
    key_builder: Optional[callable] = None
):
    """
    Decorator to cache function responses
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
        key_builder: Custom function to build cache key from args/kwargs
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                key_data = {"args": args, "kwargs": kwargs}
                cache_key = cache_manager._generate_key(prefix, key_data)
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for key: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Cache the result
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


# Pre-configured cache decorators
cache_short = cache_response(prefix="short", ttl=60)  # 1 minute
cache_medium = cache_response(prefix="medium", ttl=300)  # 5 minutes
cache_long = cache_response(prefix="long", ttl=3600)  # 1 hour


class UserCache:
    """User-specific caching utilities"""
    
    @staticmethod
    def user_key_builder(user_id: int, *args, **kwargs) -> str:
        """Build cache key for user-specific data"""
        key_data = {"user_id": user_id, "args": args, "kwargs": kwargs}
        return cache_manager._generate_key("user", key_data)
    
    @staticmethod
    async def invalidate_user_cache(user_id: int):
        """Invalidate all cache entries for a user"""
        pattern = f"user:*user_id*{user_id}*"
        return await cache_manager.clear_pattern(pattern)


# User-specific cache decorators
def cache_user_data(ttl: int = 300):
    """Cache decorator for user-specific data"""
    return cache_response(
        prefix="user_data",
        ttl=ttl,
        key_builder=UserCache.user_key_builder
    )

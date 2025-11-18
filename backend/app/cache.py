"""
Redis caching service for SmartAmazon API

Provides caching with automatic expiration, cache warming, and cache invalidation
"""
import json
import redis
from typing import Any, Optional, Callable
from functools import wraps
import hashlib
from datetime import timedelta
import os

from .logging_config import get_logger
from .exceptions import CacheError


logger = get_logger(__name__)


class CacheService:
    """
    Redis-based caching service with automatic expiration
    """

    def __init__(self, redis_url: str = None):
        """
        Initialize cache service

        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        try:
            self.client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            # Test connection
            self.client.ping()
            logger.info("Redis cache connected successfully")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    def is_available(self) -> bool:
        """
        Check if cache is available

        Returns:
            True if cache is available, False otherwise
        """
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except redis.ConnectionError:
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.is_available():
            return None

        try:
            value = self.client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            else:
                logger.debug(f"Cache miss: {key}")
                return None
        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        expiration: int = 900  # 15 minutes default
    ) -> bool:
        """
        Set value in cache with expiration

        Args:
            key: Cache key
            value: Value to cache
            expiration: Expiration time in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False

        try:
            serialized = json.dumps(value, default=str)
            self.client.setex(key, expiration, serialized)
            logger.debug(f"Cache set: {key} (expires in {expiration}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete value from cache

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False

        try:
            self.client.delete(key)
            logger.debug(f"Cache deleted: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern

        Args:
            pattern: Pattern to match (e.g., "search:*")

        Returns:
            Number of keys deleted
        """
        if not self.is_available():
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                deleted = self.client.delete(*keys)
                logger.info(f"Deleted {deleted} cache keys matching '{pattern}'")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for '{pattern}': {e}")
            return 0

    def clear_all(self) -> bool:
        """
        Clear all cache (use with caution!)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False

        try:
            self.client.flushdb()
            logger.warning("All cache cleared")
            return True
        except Exception as e:
            logger.error(f"Cache clear all error: {e}")
            return False

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a counter in cache

        Args:
            key: Cache key
            amount: Amount to increment

        Returns:
            New value or None if failed
        """
        if not self.is_available():
            return None

        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key '{key}': {e}")
            return None

    def get_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        if not self.is_available():
            return {"status": "unavailable"}

        try:
            info = self.client.info('stats')
            return {
                "status": "available",
                "total_commands": info.get('total_commands_processed', 0),
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0),
                "hit_rate": round(
                    info.get('keyspace_hits', 0) /
                    (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1)) * 100,
                    2
                )
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"status": "error", "error": str(e)}


# Global cache instance
_cache_service = None


def get_cache() -> CacheService:
    """
    Get global cache service instance

    Returns:
        CacheService instance
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


def cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from arguments

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Cache key string
    """
    # Create a consistent string representation
    key_data = f"{args}:{sorted(kwargs.items())}"
    # Hash it for consistent length
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(
    expiration: int = 900,
    key_prefix: str = "",
    key_func: Optional[Callable] = None
):
    """
    Decorator to cache function results

    Args:
        expiration: Cache expiration in seconds
        key_prefix: Prefix for cache key
        key_func: Custom function to generate cache key

    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache = get_cache()

            # Generate cache key
            if key_func:
                key = f"{key_prefix}:{key_func(*args, **kwargs)}"
            else:
                key = f"{key_prefix}:{cache_key(*args, **kwargs)}"

            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            cache.set(key, result, expiration)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache = get_cache()

            # Generate cache key
            if key_func:
                key = f"{key_prefix}:{key_func(*args, **kwargs)}"
            else:
                key = f"{key_prefix}:{cache_key(*args, **kwargs)}"

            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(key, result, expiration)

            return result

        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

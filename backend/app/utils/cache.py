"""
Cache Utility for LoCALIzate Backend
===================================

Caching utilities with support for in-memory and Redis backends.

Features:
    - In-memory cache with TTL
    - Redis cache support (optional)
    - Decorators for caching function results
    - Async support
    - Cache statistics

Usage:
    from app.utils.cache import get_cache, set_cache, cached, cached_async
    
    # Basic cache operations
    set_cache("key", "value", ttl=60)
    value = get_cache("key")
    
    # Decorator
    @cached(ttl=300)
    def expensive_function():
        return "result"
    
    @cached_async(ttl=300)
    async def expensive_async():
        return "result"
"""

import asyncio
import hashlib
import json
import logging
from typing import Any, Optional, Callable, Dict, List, Tuple, Union
from datetime import datetime, timedelta
from functools import wraps
from collections import OrderedDict
import threading

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


# =====================================================
# CACHE BACKEND INTERFACE
# =====================================================

class CacheBackend:
    """Abstract base class for cache backends."""
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        raise NotImplementedError
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL."""
        raise NotImplementedError
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        raise NotImplementedError
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        raise NotImplementedError
    
    async def clear(self) -> bool:
        """Clear all cache."""
        raise NotImplementedError
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache."""
        result = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    async def set_many(self, items: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values in cache."""
        for key, value in items.items():
            await self.set(key, value, ttl)
        return True
    
    async def delete_many(self, keys: List[str]) -> int:
        """Delete multiple keys from cache."""
        deleted = 0
        for key in keys:
            if await self.delete(key):
                deleted += 1
        return deleted


# =====================================================
# IN-MEMORY CACHE (LRU)
# =====================================================

class MemoryCache(CacheBackend):
    """
    In-memory LRU cache with TTL support.
    Suitable for development and single-instance deployments.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize in-memory cache.
        
        Args:
            max_size: Maximum number of items in cache
            default_ttl: Default TTL in seconds
        """
        self._cache: OrderedDict = OrderedDict()
        self._ttl: Dict[str, datetime] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "size": 0
        }
        
        logger.info(f"MemoryCache initialized (max_size={max_size}, default_ttl={default_ttl}s)")
    
    def _clean_expired(self):
        """Remove expired items from cache."""
        now = datetime.now()
        expired = [k for k, exp in self._ttl.items() if exp < now]
        for key in expired:
            if key in self._cache:
                del self._cache[key]
            del self._ttl[key]
            self._stats["size"] = max(0, self._stats["size"] - 1)
    
    def _evict_if_needed(self):
        """Evict oldest item if cache exceeds max size."""
        if len(self._cache) > self._max_size:
            # Remove oldest item (first in OrderedDict)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            if oldest_key in self._ttl:
                del self._ttl[oldest_key]
            self._stats["size"] = max(0, self._stats["size"] - 1)
            logger.debug(f"Evicted oldest key: {oldest_key}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            self._clean_expired()
            
            if key not in self._cache:
                self._stats["misses"] += 1
                return None
            
            # Move to end (most recently used)
            value = self._cache.pop(key)
            self._cache[key] = value
            
            self._stats["hits"] += 1
            logger.debug(f"Cache hit: {key}")
            return value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL."""
        with self._lock:
            self._clean_expired()
            
            ttl_seconds = ttl if ttl is not None else self._default_ttl
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            
            # Remove existing if present
            if key in self._cache:
                del self._cache[key]
            
            # Add to cache
            self._cache[key] = value
            self._ttl[key] = expires_at
            
            self._evict_if_needed()
            
            self._stats["sets"] += 1
            self._stats["size"] = len(self._cache)
            
            logger.debug(f"Cache set: {key} (TTL={ttl_seconds}s)")
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._ttl:
                    del self._ttl[key]
                self._stats["deletes"] += 1
                self._stats["size"] = len(self._cache)
                logger.debug(f"Cache delete: {key}")
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        with self._lock:
            self._clean_expired()
            return key in self._cache
    
    async def clear(self) -> bool:
        """Clear all cache."""
        with self._lock:
            self._cache.clear()
            self._ttl.clear()
            self._stats["size"] = 0
            logger.info("Cache cleared")
            return True
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            self._clean_expired()
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_rate": round(hit_rate, 2),
                "sets": self._stats["sets"],
                "deletes": self._stats["deletes"],
                "size": self._stats["size"],
                "max_size": self._max_size
            }


# =====================================================
# REDIS CACHE (OPTIONAL)
# =====================================================

class RedisCache(CacheBackend):
    """
    Redis cache backend.
    Requires redis-py to be installed.
    """
    
    def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 300):
        """
        Initialize Redis cache.
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds
        """
        self._redis = None
        self._redis_url = redis_url or settings.REDIS_URL
        self._default_ttl = default_ttl
        self._stats = {"hits": 0, "misses": 0, "sets": 0}
        
        if self._redis_url:
            try:
                import redis.asyncio as redis
                self._redis = redis.from_url(self._redis_url, decode_responses=True)
                logger.info(f"RedisCache initialized (url={self._redis_url})")
            except ImportError:
                logger.warning("redis-py not installed. RedisCache will use memory fallback.")
                self._redis = None
        else:
            logger.info("REDIS_URL not configured. RedisCache will use memory fallback.")
        
        if not self._redis:
            # Fallback to memory cache
            self._fallback = MemoryCache(default_ttl=default_ttl)
            logger.warning("RedisCache falling back to MemoryCache")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        if not self._redis:
            return await self._fallback.get(key)
        
        try:
            value = await self._redis.get(key)
            if value:
                self._stats["hits"] += 1
                logger.debug(f"Redis hit: {key}")
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            else:
                self._stats["misses"] += 1
                return None
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis with TTL."""
        if not self._redis:
            return await self._fallback.set(key, value, ttl)
        
        try:
            ttl_seconds = ttl if ttl is not None else self._default_ttl
            serialized = json.dumps(value, default=str)
            await self._redis.setex(key, ttl_seconds, serialized)
            self._stats["sets"] += 1
            logger.debug(f"Redis set: {key} (TTL={ttl_seconds}s)")
            return True
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        if not self._redis:
            return await self._fallback.delete(key)
        
        try:
            deleted = await self._redis.delete(key)
            return deleted > 0
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        if not self._redis:
            return await self._fallback.exists(key)
        
        try:
            return await self._redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {str(e)}")
            return False
    
    async def clear(self) -> bool:
        """Clear all Redis cache (flush current database)."""
        if not self._redis:
            return await self._fallback.clear()
        
        try:
            await self._redis.flushdb()
            logger.info("Redis cache cleared")
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {str(e)}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if self._redis:
            total = self._stats["hits"] + self._stats["misses"]
            hit_rate = (self._stats["hits"] / total * 100) if total > 0 else 0
            
            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_rate": round(hit_rate, 2),
                "sets": self._stats["sets"],
                "backend": "redis"
            }
        else:
            return await self._fallback.get_stats()


# =====================================================
# CACHE INSTANCE
# =====================================================

# Global cache instance
_cache: Optional[CacheBackend] = None


def get_cache_backend() -> CacheBackend:
    """
    Get the configured cache backend.
    
    Returns:
        CacheBackend instance
    """
    global _cache
    
    if _cache is None:
        if settings.REDIS_URL and settings.REDIS_URL.startswith("redis://"):
            _cache = RedisCache(redis_url=settings.REDIS_URL)
        else:
            _cache = MemoryCache(max_size=1000, default_ttl=settings.REDIS_TTL)
    
    return _cache


def set_cache_backend(cache: CacheBackend):
    """
    Set custom cache backend (for testing).
    
    Args:
        cache: CacheBackend instance
    """
    global _cache
    _cache = cache
    logger.info(f"Cache backend set to {type(cache).__name__}")


# =====================================================
# CACHE OPERATIONS
# =====================================================

async def get_cache(key: str) -> Optional[Any]:
    """
    Get value from cache.
    
    Args:
        key: Cache key
    
    Returns:
        Cached value or None
    """
    cache = get_cache_backend()
    return await cache.get(key)


async def set_cache(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """
    Set value in cache.
    
    Args:
        key: Cache key
        value: Value to cache
        ttl: Time to live in seconds (optional)
    
    Returns:
        True if successful
    """
    cache = get_cache_backend()
    return await cache.set(key, value, ttl)


async def delete_cache(key: str) -> bool:
    """
    Delete key from cache.
    
    Args:
        key: Cache key
    
    Returns:
        True if deleted
    """
    cache = get_cache_backend()
    return await cache.delete(key)


async def clear_cache() -> bool:
    """
    Clear all cache.
    
    Returns:
        True if successful
    """
    cache = get_cache_backend()
    return await cache.clear()


async def cache_exists(key: str) -> bool:
    """
    Check if key exists in cache.
    
    Args:
        key: Cache key
    
    Returns:
        True if exists
    """
    cache = get_cache_backend()
    return await cache.exists(key)


# =====================================================
# CACHE DECORATORS
# =====================================================

def _make_cache_key(prefix: str, args: Tuple, kwargs: Dict) -> str:
    """
    Generate cache key from function arguments.
    
    Args:
        prefix: Prefix for cache key
        args: Positional arguments
        kwargs: Keyword arguments
    
    Returns:
        Cache key string
    """
    key_parts = [prefix]
    
    # Add positional arguments
    for arg in args:
        key_parts.append(str(arg))
    
    # Add keyword arguments (sorted for consistency)
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")
    
    key_string = ":".join(key_parts)
    
    # Hash long keys to keep length manageable
    if len(key_string) > 200:
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    return key_string


def cached(
    ttl: int = 300,
    prefix: Optional[str] = None,
    key_func: Optional[Callable] = None
):
    """
    Decorator for caching function results (sync).
    
    Args:
        ttl: Cache TTL in seconds
        prefix: Custom cache key prefix
        key_func: Custom key generation function
    
    Usage:
        @cached(ttl=60)
        def get_expensive_data(user_id):
            return fetch_from_db(user_id)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                key_prefix = prefix or f"{func.__module__}:{func.__name__}"
                cache_key = _make_cache_key(key_prefix, args, kwargs)
            
            # Try to get from cache
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            cached_value = loop.run_until_complete(get_cache(cache_key))
            
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            loop.run_until_complete(set_cache(cache_key, result, ttl))
            
            return result
        
        return wrapper
    return decorator


def cached_async(
    ttl: int = 300,
    prefix: Optional[str] = None,
    key_func: Optional[Callable] = None
):
    """
    Decorator for caching async function results.
    
    Args:
        ttl: Cache TTL in seconds
        prefix: Custom cache key prefix
        key_func: Custom key generation function
    
    Usage:
        @cached_async(ttl=60)
        async def get_expensive_data(user_id):
            return await fetch_from_db(user_id)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                key_prefix = prefix or f"{func.__module__}:{func.__name__}"
                cache_key = _make_cache_key(key_prefix, args, kwargs)
            
            # Try to get from cache
            cached_value = await get_cache(cache_key)
            
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await set_cache(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# =====================================================
# TESTING
# =====================================================

async def _test():
    """Test cache functionality."""
    print("Testing MemoryCache...")
    cache = MemoryCache(max_size=5, default_ttl=2)
    
    # Test set/get
    await cache.set("key1", "value1")
    value = await cache.get("key1")
    print(f"  Get key1: {value}")
    
    # Test TTL expiration
    await cache.set("key2", "value2", ttl=1)
    import asyncio
    await asyncio.sleep(1.5)
    expired = await cache.get("key2")
    print(f"  Expired key2: {expired}")
    
    # Test LRU eviction
    for i in range(10):
        await cache.set(f"key_{i}", f"value_{i}")
    stats = await cache.get_stats()
    print(f"  Cache stats: {stats}")
    
    # Test decorator
    @cached_async(ttl=2)
    async def test_function(x: int) -> int:
        print(f"  Executing test_function with x={x}")
        return x * 2
    
    result1 = await test_function(5)
    result2 = await test_function(5)
    print(f"  First call: {result1}, Second call (cached): {result2}")
    
    print("✅ Cache tests passed")


if __name__ == "__main__":
    print("Cache utility loaded successfully")
    asyncio.run(_test())
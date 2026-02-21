"""
Redis Caching Layer
Enterprise caching with fallback to in-memory cache
"""
import logging
import json
import pickle
from typing import Any, Optional
from datetime import timedelta

logger = logging.getLogger(__name__)


class RedisCacheLayer:
    """
    Redis caching with automatic fallback to in-memory cache
    """
    
    def __init__(self):
        self._redis_client = None
        self._memory_cache: dict = {}
        self._enabled = True
        self._use_redis = False
        
        # Try to initialize Redis
        try:
            import redis
            from core.config import settings
            
            if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
                self._redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=False,
                    socket_connect_timeout=2
                )
                # Test connection
                self._redis_client.ping()
                self._use_redis = True
                logger.info("✅ Redis cache layer initialized")
            else:
                logger.info("⚠️  Redis not configured, using in-memory cache")
        
        except Exception as e:
            logger.warning(f"Redis unavailable, using in-memory cache: {e}")
            self._use_redis = False
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set a cache value"""
        if not self._enabled:
            return
        
        try:
            if self._use_redis and self._redis_client:
                # Use Redis
                serialized = pickle.dumps(value)
                if ttl:
                    self._redis_client.setex(key, ttl, serialized)
                else:
                    self._redis_client.set(key, serialized)
            else:
                # Use memory cache
                self._memory_cache[key] = value
        
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            # Fallback to memory
            self._memory_cache[key] = value
    
    def get(self, key: str) -> Optional[Any]:
        """Get a cache value"""
        if not self._enabled:
            return None
        
        try:
            if self._use_redis and self._redis_client:
                # Try Redis first
                value = self._redis_client.get(key)
                if value:
                    return pickle.loads(value)
                return None
            else:
                # Use memory cache
                return self._memory_cache.get(key)
        
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            # Fallback to memory
            return self._memory_cache.get(key)
    
    def delete(self, key: str):
        """Delete a cache key"""
        try:
            if self._use_redis and self._redis_client:
                self._redis_client.delete(key)
            else:
                self._memory_cache.pop(key, None)
        
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
    
    def clear(self):
        """Clear all cache"""
        try:
            if self._use_redis and self._redis_client:
                self._redis_client.flushdb()
            else:
                self._memory_cache.clear()
            
            logger.info("Cache cleared")
        
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            if self._use_redis and self._redis_client:
                return bool(self._redis_client.exists(key))
            else:
                return key in self._memory_cache
        
        except Exception as e:
            logger.error(f"Failed to check key existence: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        try:
            if self._use_redis and self._redis_client:
                info = self._redis_client.info()
                return {
                    "backend": "redis",
                    "keys": self._redis_client.dbsize(),
                    "memory_used": info.get("used_memory_human", "unknown"),
                    "enabled": self._enabled
                }
            else:
                return {
                    "backend": "memory",
                    "keys": len(self._memory_cache),
                    "enabled": self._enabled
                }
        
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"backend": "unknown", "enabled": self._enabled}
    
    def disable(self):
        """Disable cache"""
        self._enabled = False
        logger.warning("Cache disabled")
    
    def enable(self):
        """Enable cache"""
        self._enabled = True
        logger.info("Cache enabled")


# Global instance
cache_layer = RedisCacheLayer()

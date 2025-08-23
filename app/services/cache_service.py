# V2 Redis Cache Service
import logging
from typing import Optional, Any, Union
import redis.asyncio as redis
import json
from datetime import datetime, timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    """Redis cache service for V2 POC"""
    
    def __init__(self):
        self.redis_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Redis client"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            logger.info(f"Redis client initialized for: {settings.REDIS_URL}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            raise RuntimeError(f"Redis initialization failed: {e}")
    
    async def set(
        self, 
        key: str, 
        value: Union[str, dict, list, int, float], 
        expires: Optional[int] = None
    ) -> bool:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized if not string)
            expires: Expiration time in seconds (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Serialize non-string values
            if not isinstance(value, str):
                cache_value = json.dumps(value, default=str)
            else:
                cache_value = value
            
            # Set with optional expiration
            if expires:
                result = await self.redis_client.setex(key, expires, cache_value)
            else:
                result = await self.redis_client.set(key, cache_value)
            
            logger.debug(f"Cached key '{key}' with expiry {expires}s" if expires else f"Cached key '{key}'")
            return bool(result)
            
        except Exception as e:
            logger.error(f"Error setting cache key '{key}': {e}")
            return False
    
    async def get(self, key: str, parse_json: bool = True) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            parse_json: Whether to attempt JSON parsing of the value
            
        Returns:
            Cached value or None if not found
        """
        try:
            value = await self.redis_client.get(key)
            
            if value is None:
                logger.debug(f"Cache miss for key '{key}'")
                return None
            
            # Try to parse as JSON if requested
            if parse_json:
                try:
                    parsed_value = json.loads(value)
                    logger.debug(f"Cache hit for key '{key}' (JSON parsed)")
                    return parsed_value
                except (json.JSONDecodeError, TypeError):
                    # Not JSON, return as string
                    logger.debug(f"Cache hit for key '{key}' (string)")
                    return value
            else:
                logger.debug(f"Cache hit for key '{key}' (raw string)")
                return value
                
        except Exception as e:
            logger.error(f"Error getting cache key '{key}': {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was deleted, False if key didn't exist
        """
        try:
            result = await self.redis_client.delete(key)
            
            if result > 0:
                logger.debug(f"Deleted cache key '{key}'")
                return True
            else:
                logger.debug(f"Cache key '{key}' not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting cache key '{key}': {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache.
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists, False otherwise
        """
        try:
            result = await self.redis_client.exists(key)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Error checking cache key existence '{key}': {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a numeric value in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment by (default 1)
            
        Returns:
            New value after increment, or None on error
        """
        try:
            result = await self.redis_client.incrby(key, amount)
            logger.debug(f"Incremented cache key '{key}' by {amount}, new value: {result}")
            return int(result)
            
        except Exception as e:
            logger.error(f"Error incrementing cache key '{key}': {e}")
            return None
    
    async def set_hash(self, key: str, field_values: dict, expires: Optional[int] = None) -> bool:
        """
        Set multiple fields in a hash.
        
        Args:
            key: Hash key
            field_values: Dictionary of field->value mappings
            expires: Optional expiration time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Set hash fields
            result = await self.redis_client.hset(key, mapping=field_values)
            
            # Set expiration if specified
            if expires:
                await self.redis_client.expire(key, expires)
            
            logger.debug(f"Set hash '{key}' with {len(field_values)} fields")
            return True
            
        except Exception as e:
            logger.error(f"Error setting hash '{key}': {e}")
            return False
    
    async def get_hash(self, key: str, field: Optional[str] = None) -> Optional[Union[dict, str]]:
        """
        Get hash field(s).
        
        Args:
            key: Hash key
            field: Specific field to get (if None, gets all fields)
            
        Returns:
            Field value (if field specified) or dict of all fields, or None if not found
        """
        try:
            if field:
                # Get specific field
                value = await self.redis_client.hget(key, field)
                logger.debug(f"Got hash field '{key}.{field}': {'found' if value else 'not found'}")
                return value
            else:
                # Get all fields
                values = await self.redis_client.hgetall(key)
                logger.debug(f"Got hash '{key}' with {len(values)} fields")
                return values if values else None
                
        except Exception as e:
            logger.error(f"Error getting hash '{key}': {e}")
            return None
    
    async def cache_ai_response(
        self, 
        system_prompt: str, 
        user_context: str, 
        ai_result: str,
        expires: int = 3600
    ) -> str:
        """
        Cache an AI response with a generated key.
        
        Args:
            system_prompt: System prompt used
            user_context: User context
            ai_result: AI response to cache
            expires: Cache expiration in seconds (default 1 hour)
            
        Returns:
            Cache key used
        """
        # Generate cache key from prompts
        import hashlib
        prompt_hash = hashlib.md5(f"{system_prompt}:{user_context}".encode()).hexdigest()
        cache_key = f"ai_response:{prompt_hash}"
        
        # Cache the response
        cached = await self.set(cache_key, {
            "system_prompt": system_prompt,
            "user_context": user_context,
            "ai_result": ai_result,
            "cached_at": datetime.utcnow().isoformat()
        }, expires)
        
        if cached:
            logger.info(f"Cached AI response with key: {cache_key}")
        
        return cache_key
    
    async def get_cached_ai_response(self, system_prompt: str, user_context: str) -> Optional[dict]:
        """
        Retrieve a cached AI response.
        
        Args:
            system_prompt: System prompt used
            user_context: User context
            
        Returns:
            Cached response dict or None if not found
        """
        import hashlib
        prompt_hash = hashlib.md5(f"{system_prompt}:{user_context}".encode()).hexdigest()
        cache_key = f"ai_response:{prompt_hash}"
        
        cached_response = await self.get(cache_key)
        
        if cached_response:
            logger.info(f"Found cached AI response for key: {cache_key}")
        
        return cached_response
    
    async def clear_all_cache(self) -> bool:
        """
        Clear all cache (use with caution!).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.redis_client.flushdb()
            logger.warning("Cleared all cache data")
            return bool(result)
            
        except Exception as e:
            logger.error(f"Error clearing all cache: {e}")
            return False
    
    async def get_cache_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache statistics
        """
        try:
            info = await self.redis_client.info()
            
            return {
                "redis_version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> dict:
        """Check Redis connectivity and functionality"""
        try:
            # Test basic connectivity
            pong = await self.redis_client.ping()
            
            # Test set/get operations
            test_key = "health_check_test"
            test_value = f"test_{datetime.utcnow().timestamp()}"
            
            await self.set(test_key, test_value, expires=60)
            retrieved_value = await self.get(test_key, parse_json=False)
            await self.delete(test_key)
            
            return {
                "status": "healthy",
                "ping": pong,
                "test_set_get_delete": "success" if retrieved_value == test_value else "failed",
                "redis_url": settings.REDIS_URL
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis client connection closed")

# Global service instance
cache_service = CacheService()
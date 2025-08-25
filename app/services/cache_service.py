# V2 Redis Cache Service
"""
This service provides an abstraction layer for interacting with the Redis cache.

It uses the `redis-py` asyncio interface to perform asynchronous cache operations.
Key features include:
- Simplified get/set/delete operations.
- Automatic JSON serialization/deserialization for non-string values.
- Helper methods for common caching patterns (e.g., caching AI responses).
- Health check endpoint to verify Redis connectivity.
"""

import logging
from typing import Optional, Any, Union
import redis.asyncio as redis
import json
import hashlib
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """
    A service class to handle all Redis cache operations.

    Attributes:
        redis_client: An `aioredis.Redis` client instance.
    """

    def __init__(self):
        """Initializes the CacheService and the underlying Redis client."""
        self.redis_client: Optional[redis.Redis] = None
        self._initialize_client()

    def _initialize_client(self):
        """Initializes the Redis client from the URL specified in the settings."""
        logger.info(f"Initializing Redis client for URL: {settings.REDIS_URL}...")
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,  # Decode responses from bytes to UTF-8 strings
                socket_timeout=5,
                socket_connect_timeout=5
            )
            logger.info("Redis client initialized successfully with timeout=5s")
        except Exception as e:
            logger.critical(f"Failed to initialize Redis client: {e}", exc_info=True)
            raise RuntimeError(f"Redis initialization failed: {e}")

    async def set(
        self, key: str, value: Any, expires: Optional[int] = None
    ) -> bool:
        """
        Sets a key-value pair in the cache.

        If the value is not a string, it will be automatically serialized to a JSON string.

        Args:
            key: The key for the cache entry.
            value: The value to store.
            expires: Optional expiration time in seconds.

        Returns:
            True if the operation was successful, False otherwise.
        """
        logger.debug(f"Setting cache key '{key}' with expiry={expires}s")
        try:
            # Serialize non-string values to JSON for consistent storage.
            cache_value = json.dumps(value, default=str) if not isinstance(value, str) else value
            value_size = len(cache_value) if isinstance(cache_value, str) else 0

            if expires:
                await self.redis_client.setex(key, expires, cache_value)
                logger.debug(f"Set key '{key}' with {value_size} bytes, expires in {expires}s")
            else:
                await self.redis_client.set(key, cache_value)
                logger.debug(f"Set key '{key}' with {value_size} bytes, no expiry")

            return True
        except Exception as e:
            logger.error(f"Error setting cache key '{key}': {e}", exc_info=True)
            return False

    async def get(self, key: str, parse_json: bool = True) -> Optional[Any]:
        """
        Retrieves a value from the cache by its key.

        Args:
            key: The key of the item to retrieve.
            parse_json: If True, attempts to deserialize the value from JSON.

        Returns:
            The cached value, which may be a dictionary or list if JSON parsing is successful.
            Returns None if the key is not found or an error occurs.
        """
        logger.debug(f"Getting cache key '{key}' (parse_json={parse_json})")
        try:
            value = await self.redis_client.get(key)
            if value is None:
                logger.debug(f"Cache miss for key '{key}'")
                return None

            value_size = len(value) if isinstance(value, str) else 0
            logger.debug(f"Cache hit for key '{key}', retrieved {value_size} bytes")

            if parse_json:
                try:
                    # Attempt to deserialize from JSON.
                    parsed = json.loads(value)
                    logger.debug(f"Successfully parsed JSON for key '{key}'")
                    return parsed
                except (json.JSONDecodeError, TypeError):
                    # If it fails, return the raw string value.
                    logger.debug(f"Could not parse JSON for key '{key}', returning raw value")
                    return value
            return value
        except Exception as e:
            logger.error(f"Error getting cache key '{key}': {e}", exc_info=True)
            return None

    async def cache_ai_response(
        self, system_prompt: str, user_context: str, ai_result: str, expires: int = 3600
    ) -> str:
        """
        A helper method to cache an AI response using a generated key.

        The cache key is a hash of the system and user prompts to ensure uniqueness.

        Args:
            system_prompt: The system prompt that was used.
            user_context: The user context that was used.
            ai_result: The AI response to cache.
            expires: The cache expiration time in seconds (defaults to 1 hour).

        Returns:
            The generated cache key used for the entry.
        """
        # Create a deterministic cache key by hashing the prompts.
        prompt_hash = hashlib.md5(f"{system_prompt}:{user_context}".encode()).hexdigest()
        cache_key = f"ai_response:{prompt_hash}"

        logger.info(f"Caching AI response with key: {cache_key}, expires in {expires}s")

        payload = {
            "ai_result": ai_result,
            "cached_at": datetime.utcnow().isoformat()
        }

        if await self.set(cache_key, payload, expires):
            logger.info(f"Successfully cached AI response (size: {len(ai_result)} chars) with key: {cache_key}")
        else:
            logger.warning(f"Failed to cache AI response with key: {cache_key}")

        return cache_key

    async def health_check(self) -> dict:
        """
        Performs a health check on the Redis service.

        This check verifies connectivity and basic SET/GET/DELETE operations.

        Returns:
            A dictionary containing the health status and diagnostic information.
        """
        logger.debug("Starting Redis health check...")
        try:
            # 1. Test basic connectivity.
            logger.debug("Testing Redis PING...")
            if not await self.redis_client.ping():
                raise ConnectionError("PING command failed")
            logger.debug("Redis PING successful")

            # 2. Test SET/GET/DELETE operations.
            test_key = f"health_check:{int(datetime.utcnow().timestamp())}"
            test_value = "ok"
            logger.debug(f"Testing SET/GET/DELETE with key: {test_key}")

            await self.set(test_key, test_value, expires=10)
            retrieved = await self.get(test_key, parse_json=False)
            await self.redis_client.delete(test_key)
            logger.debug(f"Deleted test key: {test_key}")

            if retrieved != test_value:
                raise ValueError(f"SET/GET operation mismatch: expected '{test_value}', got '{retrieved}'")

            logger.info("Redis health check completed successfully")
            return {"status": "healthy", "details": "Ping and SET/GET operations successful."}
        except Exception as e:
            logger.error(f"Redis health check failed: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    async def close(self):
        """Closes the Redis client connection gracefully."""
        if self.redis_client:
            logger.info("Closing Redis client connection...")
            await self.redis_client.close()
            self.redis_client = None
            logger.info("Redis client connection closed successfully")
        else:
            logger.debug("Redis client was not initialized, nothing to close")

# Create a single, global instance of the CacheService.
# This instance will be imported and used by other parts of the application.


cache_service = CacheService()

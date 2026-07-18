"""Caching service."""

import logging
import time
from typing import Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheManager:
    """In-memory cache manager."""

    def __init__(self, ttl: int = 300):
        """
        Initialize cache manager.

        Args:
            ttl: Time to live for cache entries in seconds.
        """
        self.ttl = ttl
        self.cache: dict[str, tuple[Any, float]] = {}

    def set(self, key: str, value: Any) -> None:
        """
        Store value in cache.

        Args:
            key: Cache key.
            value: Value to cache.
        """
        self.cache[key] = (value, time.time())
        logger.debug(f"Cache SET: {key}")

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache.

        Args:
            key: Cache key.

        Returns:
            Cached value if exists and not expired, None otherwise.
        """
        if key not in self.cache:
            return None

        value, timestamp = self.cache[key]
        if time.time() - timestamp > self.ttl:
            del self.cache[key]
            logger.debug(f"Cache EXPIRED: {key}")
            return None

        logger.debug(f"Cache HIT: {key}")
        return value

    def delete(self, key: str) -> None:
        """
        Delete value from cache.

        Args:
            key: Cache key.
        """
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache DELETE: {key}")

    def clear(self) -> None:
        """
        Clear all cache.
        """
        self.cache.clear()
        logger.debug("Cache CLEARED")

    def size(self) -> int:
        """
        Get number of items in cache.

        Returns:
            Number of cached items.
        """
        return len(self.cache)

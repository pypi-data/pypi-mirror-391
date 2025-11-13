"""
Hybrid caching system for the Py-Gamma SDK.
"""

import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional

import diskcache
from cachetools import LRUCache

from .config import GammaConfig

# Type alias for cache value structure
CacheValue = Dict[str, Any]

logger = logging.getLogger(__name__)


class CacheKey:
    """Utility class for generating consistent cache keys."""

    @staticmethod
    def generate(method: str, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Generate a cache key for a request."""
        key_data = {
            "method": method.upper(),
            "url": url,
            "params": params or {},
        }
        key_str = json.dumps(key_data, sort_keys=True, separators=(",", ":"))
        return hashlib.md5(key_str.encode()).hexdigest()


class CacheManager:
    """Hybrid cache manager with memory and disk storage."""

    def __init__(self, config: GammaConfig) -> None:
        self.config: GammaConfig = config
        self._memory_cache: Optional[LRUCache[str, CacheValue]] = None
        self._disk_cache: Optional[diskcache.Cache] = None
        self._initialized: bool = False

    def _initialize(self) -> None:
        """Initialize cache subsystems."""
        if self._initialized:
            return

        try:
            if self.config.enable_cache:
                # Initialize memory cache
                self._memory_cache = LRUCache(maxsize=self.config.memory_cache_size)

                # Initialize disk cache
                self.config.cache_dir.mkdir(parents=True, exist_ok=True)
                self._disk_cache = diskcache.Cache(
                    str(self.config.cache_dir),
                    size_limit=1024 * 1024 * 100,  # 100MB
                )

                logger.debug(
                    f"Cache initialized: memory={self.config.memory_cache_size} items, disk={self.config.cache_dir}"
                )

            self._initialized = True

        except Exception as e:
            logger.warning(f"Failed to initialize cache: {e}")
            self._initialized = True

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache (memory first, then disk)."""
        self._initialize()

        if not self.config.enable_cache or not self._memory_cache:
            return None

        # Try memory cache first
        try:
            cached_value = self._memory_cache.get(key)
            if cached_value is not None:
                assert isinstance(cached_value, dict), (
                    "Cached value must be a dictionary"
                )
                # Extract the actual data from cache structure
                return cached_value.get("data")
        except Exception as e:
            logger.debug(f"Memory cache error: {e}")

        # Try disk cache
        try:
            if self._disk_cache:
                cached_value = self._disk_cache.get(key)
                if cached_value is not None:
                    # Type assertion: disk cache should return our structured cache value
                    if not isinstance(cached_value, dict):
                        logger.warning(
                            f"Unexpected cache value type: {type(cached_value)}"
                        )
                        return None

                    # Store in memory cache for faster future access
                    self._memory_cache[key] = cached_value
                    logger.debug(f"Cache hit (disk): {key}")
                    return cached_value.get("data")
        except Exception as e:
            logger.debug(f"Disk cache error: {e}")

        logger.debug(f"Cache miss: {key}")
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> None:
        """Set value in cache with optional TTL."""
        self._initialize()

        if not self.config.enable_cache or not self._memory_cache:
            return

        ttl = ttl or self.config.cache_ttl
        expire_time = time.time() + ttl

        try:
            # Store in memory cache
            cache_value: CacheValue = {
                "data": value,
                "expire_time": expire_time,
            }
            self._memory_cache[key] = cache_value

            # Store in disk cache
            if self._disk_cache:
                self._disk_cache.set(key, cache_value, expire=expire_time)  # type: ignore[arg-type]

            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")

        except Exception as e:
            logger.debug(f"Cache set error: {e}")

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        self._initialize()

        try:
            if self._memory_cache and key in self._memory_cache:
                del self._memory_cache[key]

            if self._disk_cache:
                self._disk_cache.delete(key)

            logger.debug(f"Cache delete: {key}")

        except Exception as e:
            logger.debug(f"Cache delete error: {e}")

    async def clear(self) -> None:
        """Clear all cache data."""
        self._initialize()

        try:
            if self._memory_cache:
                self._memory_cache.clear()

            if self._disk_cache:
                self._disk_cache.clear()

            logger.debug("Cache cleared")

        except Exception as e:
            logger.debug(f"Cache clear error: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        self._initialize()

        stats = {
            "enabled": self.config.enable_cache,
            "memory_size": 0,
            "disk_size": 0,
        }

        try:
            if self._memory_cache:
                stats["memory_size"] = len(self._memory_cache)
                stats["memory_max_size"] = int(self._memory_cache.maxsize)

            if self._disk_cache:
                try:
                    stats["disk_size"] = len(self._disk_cache)  # type: ignore[arg-type]
                    stats["disk_volume"] = self._disk_cache.volume()  # type: ignore[assignment]
                except Exception:
                    stats["disk_size"] = 0
                    stats["disk_volume"] = 0

        except Exception as e:
            logger.debug(f"Cache stats error: {e}")

        return stats

    def close(self) -> None:
        """Close cache resources."""
        try:
            if self._disk_cache:
                self._disk_cache.close()
        except Exception as e:
            logger.debug(f"Cache close error: {e}")

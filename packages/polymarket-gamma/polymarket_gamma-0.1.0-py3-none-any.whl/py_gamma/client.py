"""
Main HTTP client for the Py-Gamma SDK.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

from .cache import CacheManager, CacheKey
from .config import GammaConfig
from .exceptions import (
    GammaAPIError,
    GammaNetworkError,
    RateLimitError,
    AuthenticationError,
)

logger = logging.getLogger(__name__)


class AsyncHTTPClient:
    """Async HTTP client with retry logic and caching."""

    def __init__(self, config: GammaConfig) -> None:
        self.config = config
        self.cache = CacheManager(config)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "AsyncHTTPClient":
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def initialize(self) -> None:
        """Initialize HTTP client."""
        await self._ensure_client()

    async def _ensure_client(self) -> None:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            timeout = httpx.Timeout(
                connect=self.config.connect_timeout,
                read=self.config.request_timeout,
                write=self.config.request_timeout,
                pool=self.config.request_timeout,
            )

            import os

            # Disable proxy detection
            os.environ.pop("HTTP_PROXY", None)
            os.environ.pop("HTTPS_PROXY", None)
            os.environ.pop("http_proxy", None)
            os.environ.pop("https_proxy", None)
            os.environ.pop("ALL_PROXY", None)
            os.environ.pop("all_proxy", None)

            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=timeout,
                headers=self._get_headers(),
            )

    def _get_headers(self) -> Dict[str, str]:
        """Get default HTTP headers."""
        headers = {
            "User-Agent": "py-gamma/0.1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        return headers

    async def close(self) -> None:
        """Close HTTP client and cache."""
        if self._client:
            await self._client.aclose()
            self._client = None

        self.cache.close()

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
        cache_ttl: Optional[int] = None,
    ) -> httpx.Response:
        """Make HTTP request with retry logic and caching."""
        await self._ensure_client()

        # Generate cache key for GET requests
        cache_key = None
        if method.upper() == "GET" and use_cache:
            cache_key = CacheKey.generate(method, path, params)
            cached_response = await self.cache.get(cache_key)
            if cached_response:
                logger.debug(f"Using cached response for {method} {path}")
                return cached_response

        # Make request with retry logic
        response = await self._request_with_retry(
            method, path, params=params, json_data=json_data
        )

        # Cache successful GET responses
        if (
            method.upper() == "GET"
            and use_cache
            and response.status_code == 200
            and cache_key
        ):
            await self.cache.set(cache_key, response, cache_ttl)

        return response

    async def _request_with_retry(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Make HTTP request with exponential backoff retry."""

        last_exception: Optional[Exception] = None

        for attempt in range(self.config.max_retries + 1):
            try:
                if self.config.trace_requests:
                    logger.debug(f"Request: {method} {path} (attempt {attempt + 1})")
                    if params:
                        logger.debug(f"Params: {params}")
                    if json_data:
                        logger.debug(f"Data: {json_data}")

                if self._client is None:
                    await self._ensure_client()

                assert self._client is not None, "HTTP client must be initialized"
                response = await self._client.request(
                    method, path, params=params, json=json_data
                )

                if self.config.trace_requests:
                    logger.debug(
                        f"Response: {response.status_code} {len(response.content)} bytes"
                    )

                # Handle specific HTTP errors
                if response.status_code == 401:
                    raise AuthenticationError(
                        "Invalid API key or authentication failed"
                    )
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    raise RateLimitError("Rate limit exceeded", retry_after=retry_after)
                elif response.status_code >= 500:
                    # Server errors - retry on transient failures
                    if attempt < self.config.max_retries:
                        delay = self.config.retry_delay * (
                            self.config.retry_backoff_factor**attempt
                        )
                        logger.warning(
                            f"Server error {response.status_code}, retrying in {delay}s"
                        )
                        await asyncio.sleep(delay)
                        continue

                # For other status codes, raise immediately
                response.raise_for_status()
                return response

            except httpx.NetworkError as e:
                last_exception = GammaNetworkError(
                    f"Network error: {str(e)}", retry_count=attempt
                )

                if attempt < self.config.max_retries:
                    delay = self.config.retry_delay * (
                        self.config.retry_backoff_factor**attempt
                    )
                    logger.warning(f"Network error, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                    continue
                else:
                    break

            except (AuthenticationError, RateLimitError, GammaAPIError):
                # Don't retry on auth or client errors
                raise

            except httpx.HTTPStatusError as e:
                # Try to parse JSON response data, but handle cases where it's not valid JSON
                response_data = None
                if e.response.content:
                    try:
                        response_data = e.response.json()
                    except Exception:
                        # If JSON parsing fails, just use the raw text
                        response_data = e.response.text

                last_exception = GammaAPIError(
                    f"HTTP error {e.response.status_code}: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=response_data,
                )
                raise last_exception

        # All retries exhausted
        raise last_exception or GammaNetworkError("Request failed after all retries")

    async def get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
        cache_ttl: Optional[int] = None,
    ) -> httpx.Response:
        """Make GET request."""
        return await self.request(
            "GET", path, params=params, use_cache=use_cache, cache_ttl=cache_ttl
        )

    async def post(
        self,
        path: str,
        *,
        json_data: Optional[Dict[str, Any]] = None,
        use_cache: bool = False,
        cache_ttl: Optional[int] = None,
    ) -> httpx.Response:
        """Make POST request."""
        return await self.request(
            "POST", path, json_data=json_data, use_cache=use_cache, cache_ttl=cache_ttl
        )


class _SyncWrapper:
    """Synchronous wrapper for async client methods."""

    def __init__(self, client: "GammaClient") -> None:
        self.client = client

    def __getattr__(self, name: str) -> Any:
        """Get attribute from async client and run it synchronously."""
        attr = getattr(self.client, name)

        if asyncio.iscoroutinefunction(attr):

            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                return asyncio.run(attr(*args, **kwargs))

            return sync_wrapper
        return attr


class GammaClient:
    """Main client for the Gamma API."""

    def __init__(self, config: Optional[GammaConfig] = None) -> None:
        self.config = config or GammaConfig()
        self.http_client = AsyncHTTPClient(self.config)

        # Initialize endpoints here to avoid circular imports
        from .endpoints.markets import MarketsEndpoint
        from .endpoints.search import SearchEndpoint
        from .endpoints.tags import TagsEndpoint
        from .endpoints.comments import CommentsEndpoint
        from .endpoints.series import SeriesEndpoint
        from .endpoints.sports import SportsEndpoint
        from .endpoints.events import EventsEndpoint
        from .endpoints.user import UserEndpoint

        # Initialize endpoints
        self.markets = MarketsEndpoint(self.http_client)
        self.search = SearchEndpoint(self.http_client)
        self.tags = TagsEndpoint(self.http_client)
        self.comments = CommentsEndpoint(self.http_client)
        self.series = SeriesEndpoint(self.http_client)
        self.sports = SportsEndpoint(self.http_client)
        self.events = EventsEndpoint(self.http_client)
        self.user = UserEndpoint(self.http_client)

        # Sync wrapper for convenience
        self.sync = _SyncWrapper(self)

    async def __aenter__(self) -> "GammaClient":
        await self.http_client.initialize()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close client and cleanup resources."""
        await self.http_client.close()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.http_client.cache.get_cache_stats()

    async def clear_cache(self) -> None:
        """Clear all cache."""
        await self.http_client.cache.clear()

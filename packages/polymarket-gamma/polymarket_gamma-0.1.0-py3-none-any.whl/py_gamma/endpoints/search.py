"""
Search API endpoints for the Gamma SDK.
"""

from typing import Optional, List, Any

import httpx

from .base import BaseEndpoint
from ..models.search import SearchResult
from ..exceptions import GammaAPIError, SearchValidationError


class SearchEndpoint(BaseEndpoint[SearchResult]):
    """Search API endpoints."""

    async def search(
        self,
        query: str,
        *,
        cache: Optional[bool] = None,
        events_status: Optional[str] = None,
        limit_per_type: Optional[int] = None,
        page: Optional[int] = None,
        events_tag: Optional[List[str]] = None,
        keep_closed_markets: Optional[bool] = None,
        sort: Optional[str] = None,
        ascending: Optional[bool] = None,
        search_tags: Optional[bool] = None,
        search_profiles: Optional[bool] = None,
        recurrence: Optional[str] = None,
        exclude_tag_id: Optional[List[int]] = None,
        optimized: Optional[bool] = None,
        **kwargs: Any,
    ) -> SearchResult:
        """Search markets, events, and profiles.

        Based on API documentation:
        GET /public-search

        Args:
            query: Search query term (required)
            cache: Enable/disable response caching
            events_status: Filter events by status
            limit_per_type: Number of results per type
            page: Page number for pagination
            events_tag: Filter by event tags
            keep_closed_markets: Include closed markets
            sort: Sort order
            ascending: Sort direction
            search_tags: Include tag search
            search_profiles: Include profile search
            recurrence: Filter by recurrence
            exclude_tag_id: Exclude tag IDs
            optimized: Enable optimization
            **kwargs: Additional query parameters

        Returns:
            SearchResult object with events, tags, profiles, and pagination

        Raises:
            SearchValidationError: If query parameters are invalid
            GammaAPIError: For API errors
        """
        if not query or not query.strip():
            raise SearchValidationError("Search query cannot be empty")

        # Validate page size if provided
        if limit_per_type is not None:
            limit_per_type = self._validate_page_size(limit_per_type, max_size=1000)

        # Build query parameters
        params = self._build_params(
            q=query.strip(),
            cache=cache,
            events_status=events_status,
            limit_per_type=limit_per_type,
            page=page,
            events_tag=events_tag,
            keep_closed_markets=keep_closed_markets,
            sort=sort,
            ascending=ascending,
            search_tags=search_tags,
            search_profiles=search_profiles,
            recurrence=recurrence,
            exclude_tag_id=exclude_tag_id,
            optimized=optimized,
            **kwargs,
        )

        try:
            response = await self._get("/public-search", params=params)
            result = await self._parse_response(response, SearchResult)

            if self.client.config.debug:
                print(
                    f"Search completed for query '{query}': {result.total_count} total results"
                )

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise SearchValidationError(
                    f"Invalid search parameters: {e.response.text}"
                )
            elif e.response.status_code == 404:
                raise GammaAPIError(
                    f"Search endpoint not found: {e.response.text}", status_code=404
                )
            else:
                raise GammaAPIError(
                    f"Search failed for query '{query}': {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=e.response.json() if e.response.content else None,
                )

    async def search_markets(
        self,
        query: str,
        *,
        limit_per_type: int = 50,
        page: Optional[int] = None,
        sort: Optional[str] = None,
        ascending: Optional[bool] = None,
        **kwargs: Any,
    ) -> SearchResult:
        """Search markets only.

        Args:
            query: Search query term
            limit_per_type: Number of results per type (max 1000)
            page: Page number for pagination
            keep_closed_markets: Include closed markets in results
            sort: Sort order
            ascending: Sort direction
            **kwargs: Additional search parameters

        Returns:
            SearchResult object with market-focused results

        Raises:
            SearchValidationError: If query parameters are invalid
            GammaAPIError: For API errors
        """
        return await self.search(
            query=query,
            limit_per_type=limit_per_type,
            page=page,
            sort=sort,
            ascending=ascending,
            search_tags=False,  # Focus on markets only
            search_profiles=False,  # Focus on markets only
            **kwargs,
        )

    async def search_events(
        self,
        query: str,
        *,
        limit_per_type: int = 50,
        page: Optional[int] = None,
        events_status: Optional[str] = None,
        events_tag: Optional[List[str]] = None,
        sort: Optional[str] = None,
        ascending: Optional[bool] = None,
        **kwargs: Any,
    ) -> SearchResult:
        """Search events only.

        Args:
            query: Search query term
            limit_per_type: Number of results per type (max 1000)
            page: Page number for pagination
            events_status: Filter events by status
            events_tag: Filter by event tags
            sort: Sort order
            ascending: Sort direction
            **kwargs: Additional search parameters

        Returns:
            SearchResult object with event-focused results

        Raises:
            SearchValidationError: If query parameters are invalid
            GammaAPIError: For API errors
        """
        return await self.search(
            query=query,
            limit_per_type=limit_per_type,
            page=page,
            events_status=events_status,
            events_tag=events_tag,
            sort=sort,
            ascending=ascending,
            search_tags=False,  # Focus on events only
            search_profiles=False,  # Focus on events only
            **kwargs,
        )

    async def search_profiles(
        self,
        query: str,
        *,
        limit_per_type: int = 50,
        page: Optional[int] = None,
        sort: Optional[str] = None,
        ascending: Optional[bool] = None,
        **kwargs: Any,
    ) -> SearchResult:
        """Search user profiles only.

        Args:
            query: Search query term
            limit_per_type: Number of results per type (max 1000)
            page: Page number for pagination
            sort: Sort order
            ascending: Sort direction
            **kwargs: Additional search parameters

        Returns:
            SearchResult object with profile-focused results

        Raises:
            SearchValidationError: If query parameters are invalid
            GammaAPIError: For API errors
        """
        return await self.search(
            query=query,
            limit_per_type=limit_per_type,
            page=page,
            sort=sort,
            ascending=ascending,
            search_tags=False,  # Focus on profiles only
            search_profiles=True,  # Enable profile search
            **kwargs,
        )

    async def search_tags_only(
        self,
        query: str,
        *,
        limit_per_type: int = 50,
        page: Optional[int] = None,
        sort: Optional[str] = None,
        ascending: Optional[bool] = None,
        **kwargs: Any,
    ) -> SearchResult:
        """Search tags only.

        Args:
            query: Search query term
            limit_per_type: Number of results per type (max 1000)
            page: Page number for pagination
            sort: Sort order
            ascending: Sort direction
            **kwargs: Additional search parameters

        Returns:
            SearchResult object with tag-focused results

        Raises:
            SearchValidationError: If query parameters are invalid
            GammaAPIError: For API errors
        """
        return await self.search(
            query=query,
            limit_per_type=limit_per_type,
            page=page,
            sort=sort,
            ascending=ascending,
            search_tags=True,  # Enable tag search
            search_profiles=False,  # Focus on tags only
            **kwargs,
        )

    async def get_trending_tags(
        self,
        *,
        limit_per_type: int = 20,
        sort: str = "event_count",
        ascending: bool = False,
        **kwargs: Any,
    ) -> SearchResult:
        """Get trending tags (popular tags with most events).

        Args:
            limit_per_type: Number of results (max 1000)
            sort: Sort order (defaults to event_count)
            ascending: Sort direction (defaults to descending)
            **kwargs: Additional search parameters

        Returns:
            SearchResult object with trending tags

        Raises:
            GammaAPIError: For API errors
        """
        return await self.search(
            query="*",  # Use wildcard query to get all tags
            limit_per_type=limit_per_type,
            sort=sort,
            ascending=ascending,
            search_tags=True,
            search_profiles=False,
            **kwargs,
        )

    async def search_by_category(
        self,
        query: str,
        category: str,
        *,
        limit_per_type: int = 50,
        page: Optional[int] = None,
        **kwargs: Any,
    ) -> SearchResult:
        """Search within a specific category.

        Args:
            query: Search query term
            category: Category to filter by
            limit_per_type: Number of results per type (max 1000)
            page: Page number for pagination
            **kwargs: Additional search parameters

        Returns:
            SearchResult object filtered by category

        Raises:
            SearchValidationError: If category is empty
            GammaAPIError: For API errors
        """
        if not category or not category.strip():
            raise SearchValidationError("Category cannot be empty")

        # Note: This implementation assumes the API supports category filtering
        # If the API doesn't support this directly, we'd need to filter results
        return await self.search(
            query=f"{query} category:{category.strip()}",
            limit_per_type=limit_per_type,
            page=page,
            **kwargs,
        )

    def search_sync(
        self,
        query: str,
        **kwargs: Any,
    ) -> SearchResult:
        """Synchronous version of search for convenience."""
        import asyncio

        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # If we're in an event loop, we can't use asyncio.run()
            # Create a new task in the existing loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: asyncio.run(self.search(query, **kwargs))
                )
                return future.result()
        except RuntimeError:
            # No running loop, safe to use asyncio.run()
            return asyncio.run(self.search(query, **kwargs))

    def search_markets_sync(
        self,
        query: str,
        **kwargs: Any,
    ) -> SearchResult:
        """Synchronous version of search_markets for convenience."""
        import asyncio

        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # If we're in an event loop, we can't use asyncio.run()
            # Create a new task in the existing loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: asyncio.run(self.search_markets(query, **kwargs))
                )
                return future.result()
        except RuntimeError:
            # No running loop, safe to use asyncio.run()
            return asyncio.run(self.search_markets(query, **kwargs))

    def search_events_sync(
        self,
        query: str,
        **kwargs: Any,
    ) -> SearchResult:
        """Synchronous version of search_events for convenience."""
        import asyncio

        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # If we're in an event loop, we can't use asyncio.run()
            # Create a new task in the existing loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: asyncio.run(self.search_events(query, **kwargs))
                )
                return future.result()
        except RuntimeError:
            # No running loop, safe to use asyncio.run()
            return asyncio.run(self.search_events(query, **kwargs))

    def search_profiles_sync(
        self,
        query: str,
        **kwargs: Any,
    ) -> SearchResult:
        """Synchronous version of search_profiles for convenience."""
        import asyncio

        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # If we're in an event loop, we can't use asyncio.run()
            # Create a new task in the existing loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: asyncio.run(self.search_profiles(query, **kwargs))
                )
                return future.result()
        except RuntimeError:
            # No running loop, safe to use asyncio.run()
            return asyncio.run(self.search_profiles(query, **kwargs))

    def search_tags_only_sync(
        self,
        query: str,
        **kwargs: Any,
    ) -> SearchResult:
        """Synchronous version of search_tags_only for convenience."""
        import asyncio

        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # If we're in an event loop, we can't use asyncio.run()
            # Create a new task in the existing loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: asyncio.run(self.search_tags_only(query, **kwargs))
                )
                return future.result()
        except RuntimeError:
            # No running loop, safe to use asyncio.run()
            return asyncio.run(self.search_tags_only(query, **kwargs))

    def get_trending_tags_sync(
        self,
        **kwargs: Any,
    ) -> SearchResult:
        """Synchronous version of get_trending_tags for convenience."""
        import asyncio

        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # If we're in an event loop, we can't use asyncio.run()
            # Create a new task in the existing loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: asyncio.run(self.get_trending_tags(**kwargs))
                )
                return future.result()
        except RuntimeError:
            # No running loop, safe to use asyncio.run()
            return asyncio.run(self.get_trending_tags(**kwargs))

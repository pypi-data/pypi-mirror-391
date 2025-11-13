"""
Series API endpoints for the Gamma SDK.
"""

from typing import Optional, AsyncIterator, List, Any

import httpx

from .base import BaseEndpoint
from ..models.series import Series
from ..models.markets import Market
from ..exceptions import SeriesNotFoundError, GammaAPIError


class SeriesEndpoint(BaseEndpoint[Series]):
    """Series API endpoints."""

    async def get_series_by_id(
        self,
        series_id: str,
        include_chat: bool = False,
    ) -> Series:
        """Get series by ID.

        Based on API documentation:
        GET /series/{id}

        Args:
            series_id: Series identifier (must be valid integer/ID)
            include_chat: Include chat information in response

        Returns:
            Series object

        Raises:
            SeriesNotFoundError: If series not found
            GammaAPIError: For other API errors
        """
        # Build query parameters
        params = {"include_chat": include_chat} if include_chat else {}

        try:
            response = await self._get(f"/series/{series_id}", params=params)
            series = await self._parse_response(response, Series)

            if self.client.config.debug:
                print(f"Successfully fetched series: {series.title}")

            return series

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise SeriesNotFoundError(series_id)
            else:
                raise GammaAPIError(
                    f"Failed to get series {series_id}: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=e.response.json() if e.response.content else None,
                )

    async def get_series_by_slug(
        self,
        slug: str,
        include_chat: bool = False,
    ) -> Series:
        """Get series by slug.

        Based on API pattern from markets endpoint:
        GET /series/slug/{slug}

        Args:
            slug: URL-friendly series identifier
            include_chat: Include chat information in response

        Returns:
            Series object

        Raises:
            SeriesNotFoundError: If series not found
            GammaAPIError: For other API errors
        """
        # Build query parameters
        params = {"include_chat": include_chat} if include_chat else {}

        try:
            response = await self._get(f"/series/slug/{slug}", params=params)
            series = await self._parse_response(response, Series)

            if self.client.config.debug:
                print(f"Successfully fetched series by slug '{slug}': {series.title}")

            return series

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise SeriesNotFoundError(f"slug={slug}")
            else:
                raise GammaAPIError(
                    f"Failed to get series by slug '{slug}': {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=e.response.json() if e.response.content else None,
                )

    async def get_series(
        self,
        limit: int = 100,
        offset: int = 0,
        order: Optional[str] = None,
        ascending: Optional[bool] = None,
        slug: Optional[List[str]] = None,
        categories_ids: Optional[List[int]] = None,
        categories_labels: Optional[List[str]] = None,
        closed: Optional[bool] = None,
        include_chat: Optional[bool] = None,
        recurrence: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Series]:
        """List series.

        Based on API documentation:
        GET /series

        Args:
            limit: Number of series to return (max 1000)
            offset: Number of series to skip
            order: Order by field
            ascending: Sort direction
            slug: Filter by slug values
            categories_ids: Filter by category IDs
            categories_labels: Filter by category labels
            closed: Filter by closed status
            include_chat: Include chat information
            recurrence: Filter by recurrence type
            **kwargs: Additional query parameters

        Returns:
            List of Series objects

        Raises:
            GammaAPIError: For API errors
        """
        # Validate page size
        limit = self._validate_page_size(limit, max_size=1000)

        # Build query parameters
        params = self._build_params(
            limit=limit,
            offset=offset,
            order=order,
            ascending=ascending,
            slug=slug,
            categories_ids=categories_ids,
            categories_labels=categories_labels,
            closed=closed,
            include_chat=include_chat,
            recurrence=recurrence,
            **kwargs,
        )

        try:
            response = await self._get("/series", params=params)
            series_list = await self._parse_response_list(response, Series)

            if self.client.config.debug:
                print(f"Successfully fetched {len(series_list)} series")

            return series_list

        except httpx.HTTPStatusError as e:
            raise GammaAPIError(
                f"Failed to get series: {e.response.text}",
                status_code=e.response.status_code,
                response_data=e.response.json() if e.response.content else None,
            )

    async def iter_all_series(
        self,
        page_size: int = 100,
        **filters: Any,
    ) -> AsyncIterator[Series]:
        """Iterate through all series using pagination.

        Args:
            page_size: Number of series per page
            **filters: Filter parameters from get_series()

        Yields:
            Series objects

        Raises:
            GammaAPIError: For API errors
        """
        page_size = self._validate_page_size(page_size, max_size=1000)

        if self.client.config.debug:
            print(f"Starting pagination through series with page_size={page_size}")

        # Remove limit from filters to avoid keyword argument conflict
        paginate_filters = {k: v for k, v in filters.items() if k != 'limit'}

        async for series in self._paginate(
            "/series",
            Series,
            limit=page_size,
            **paginate_filters,
        ):
            yield series

    async def get_markets_for_series(
        self,
        series_id: str,
        limit: int = 100,
        offset: int = 0,
        active: Optional[bool] = None,
        closed: Optional[bool] = None,
        **kwargs: Any,
    ) -> List[Market]:
        """Get markets for a series.

        Based on API pattern from series documentation:
        GET /series/{id}/markets

        Args:
            series_id: Series identifier
            limit: Number of markets to return (max 1000)
            offset: Number of markets to skip
            active: Filter by active status
            closed: Filter by closed status
            **kwargs: Additional query parameters

        Returns:
            List of Market objects

        Raises:
            SeriesNotFoundError: If series not found
            GammaAPIError: For other API errors
        """
        # Validate page size
        limit = self._validate_page_size(limit, max_size=1000)

        # Build query parameters
        params = self._build_params(
            limit=limit,
            offset=offset,
            active=active,
            closed=closed,
            **kwargs,
        )

        try:
            response = await self._get(f"/series/{series_id}/markets", params=params)

            # Parse response manually for Market objects to avoid type issues
            try:
                data = response.json()
                if isinstance(data, list):
                    markets = [Market.model_validate(item) for item in data]
                elif isinstance(data, dict) and "data" in data:
                    markets = [Market.model_validate(item) for item in data["data"]]
                else:
                    markets = []
            except Exception as e:
                raise GammaAPIError(f"Failed to parse response: {e}")

            if self.client.config.debug:
                print(
                    f"Successfully fetched {len(markets)} markets for series {series_id}"
                )

            return markets

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise SeriesNotFoundError(series_id)
            else:
                raise GammaAPIError(
                    f"Failed to get markets for series {series_id}: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=e.response.json() if e.response.content else None,
                )

    async def iter_all_markets_for_series(
        self,
        series_id: str,
        page_size: int = 100,
        **filters: Any,
    ) -> AsyncIterator[Market]:
        """Iterate through all markets for a series using pagination.

        Args:
            series_id: Series identifier
            page_size: Number of markets per page
            **filters: Filter parameters from get_markets_for_series()

        Yields:
            Market objects

        Raises:
            SeriesNotFoundError: If series not found
            GammaAPIError: For API errors
        """
        page_size = self._validate_page_size(page_size, max_size=1000)

        if self.client.config.debug:
            print(
                f"Starting pagination through markets for series {series_id} with page_size={page_size}"
            )

        offset = 0
        while True:
            # Get next page of markets
            markets = await self.get_markets_for_series(
                series_id,
                limit=page_size,
                offset=offset,
                **filters,
            )

            # Yield each market
            for market in markets:
                yield market

            # If we got fewer markets than page_size, we're done
            if len(markets) < page_size:
                break

            # Move to next page
            offset += page_size

    async def search_series(
        self,
        query: str,
        limit: int = 50,
        **filters: Any,
    ) -> List[Series]:
        """Search series by query string.

        Args:
            query: Search query (searches in title and description)
            limit: Maximum number of results
            **filters: Additional filter parameters

        Returns:
            List of matching Series objects

        Raises:
            GammaAPIError: For API errors
        """
        # Note: The actual API might not support a direct search parameter
        # This implementation filters client-side by title/description
        # In a real implementation, you would use the API's search capabilities

        all_series = []
        page_size = min(limit, 100)  # Use smaller pages for search

        # Remove limit from filters to avoid keyword argument conflict
        search_filters = {k: v for k, v in filters.items() if k != 'limit'}

        async for series in self.iter_all_series(limit=page_size, **search_filters):
            # Check if query matches title or description (case-insensitive)
            query_lower = query.lower()
            if (
                (series.title and query_lower in series.title.lower())
                or (series.description and query_lower in series.description.lower())
                or (series.subtitle and query_lower in series.subtitle.lower())
            ):
                all_series.append(series)

                # Stop if we've reached the limit
                if len(all_series) >= limit:
                    break

        return all_series[:limit]

    def get_sync(self, series_id: str, include_chat: bool = False) -> Series:
        """Synchronous version of get_series_by_id for convenience."""
        import asyncio

        return asyncio.run(self.get_series_by_id(series_id, include_chat))

    def get_by_slug_sync(self, slug: str, include_chat: bool = False) -> Series:
        """Synchronous version of get_series_by_slug for convenience."""
        import asyncio

        return asyncio.run(self.get_series_by_slug(slug, include_chat))

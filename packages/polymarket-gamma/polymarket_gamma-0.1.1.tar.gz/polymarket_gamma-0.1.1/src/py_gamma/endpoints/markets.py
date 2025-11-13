"""
Markets API endpoints for the Gamma SDK.
"""

from typing import Optional, AsyncIterator, List, Any

import httpx

from .base import BaseEndpoint
from ..models.markets import Market
from ..exceptions import MarketNotFoundError, GammaAPIError


class MarketsEndpoint(BaseEndpoint[Market]):
    """Markets API endpoints."""

    async def get_market_by_id(
        self,
        market_id: str,
        include_tag: bool = False,
    ) -> Market:
        """Get market by ID.

        Based on API documentation:
        GET /markets/{id}

        Args:
            market_id: Market identifier
            include_tag: Include tag information in response

        Returns:
            Market object

        Raises:
            MarketNotFoundError: If market not found
            GammaAPIError: For other API errors
        """
        # Build query parameters
        params = {"include_tag": include_tag} if include_tag else {}

        try:
            response = await self._get(f"/markets/{market_id}", params=params)
            market = await self._parse_response(response, Market)

            if self.client.config.debug:
                print(f"Successfully fetched market: {market.question}")

            return market

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise MarketNotFoundError(market_id)
            else:
                raise GammaAPIError(
                    f"Failed to get market {market_id}: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=e.response.json() if e.response.content else None,
                )

    async def get_market_by_slug(
        self,
        slug: str,
        include_tag: bool = False,
    ) -> Market:
        """Get market by slug.

        Based on API documentation:
        GET /markets/slug/{slug}

        Args:
            slug: URL-friendly market identifier
            include_tag: Include tag information in response

        Returns:
            Market object

        Raises:
            MarketNotFoundError: If market not found
            GammaAPIError: For other API errors
        """
        # Build query parameters
        params = {"include_tag": include_tag} if include_tag else {}

        try:
            response = await self._get(f"/markets/slug/{slug}", params=params)
            market = await self._parse_response(response, Market)

            if self.client.config.debug:
                print(
                    f"Successfully fetched market by slug '{slug}': {market.question}"
                )

            return market

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise MarketNotFoundError(f"slug={slug}")
            else:
                raise GammaAPIError(
                    f"Failed to get market by slug '{slug}': {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=e.response.json() if e.response.content else None,
                )

    async def get_markets(
        self,
        limit: int = 100,
        offset: int = 0,
        active: Optional[bool] = None,
        closed: Optional[bool] = None,
        slug: Optional[str] = None,
        tags: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        description: Optional[str] = None,
        question: Optional[str] = None,
        order: Optional[str] = None,
        ascending: Optional[bool] = None,
        include_tag: Optional[bool] = None,
        **kwargs: Any,
    ) -> List[Market]:
        """List markets.

        Based on API documentation:
        GET /markets

        Args:
            limit: Number of markets to return (max 1000)
            offset: Number of markets to skip
            active: Filter by active status
            closed: Filter by closed status
            slug: Filter by slug
            tags: Filter by tags
            categories: Filter by categories
            description: Filter by description (contains)
            question: Filter by question (contains)
            order: Order by field
            ascending: Sort direction
            include_tag: Include tag information
            **kwargs: Additional query parameters

        Returns:
            List of Market objects

        Raises:
            GammaAPIError: For API errors
        """
        # Validate page size
        limit = self._validate_page_size(limit, max_size=1000)

        # Build query parameters
        params = self._build_params(
            limit=limit,
            offset=offset,
            active=active,
            closed=closed,
            slug=slug,
            tags=tags,
            categories=categories,
            description=description,
            question=question,
            order=order,
            ascending=ascending,
            include_tag=include_tag,
            **kwargs,
        )

        try:
            response = await self._get("/markets", params=params)
            markets = await self._parse_response_list(response, Market)

            if self.client.config.debug:
                print(f"Successfully fetched {len(markets)} markets")

            return markets

        except httpx.HTTPStatusError as e:
            raise GammaAPIError(
                f"Failed to get markets: {e.response.text}",
                status_code=e.response.status_code,
                response_data=e.response.json() if e.response.content else None,
            )

    async def iter_all_markets(
        self,
        page_size: int = 100,
        **filters: Any,
    ) -> AsyncIterator[Market]:
        """Iterate through all markets using pagination.

        Args:
            page_size: Number of markets per page
            **filters: Filter parameters from get_markets()

        Yields:
            Market objects

        Raises:
            GammaAPIError: For API errors
        """
        page_size = self._validate_page_size(page_size, max_size=1000)

        if self.client.config.debug:
            print(f"Starting pagination through markets with page_size={page_size}")

        async for market in self._paginate(
            "/markets",
            Market,
            limit=page_size,
            **filters,
        ):
            yield market

    async def search_markets(
        self,
        query: str,
        limit: int = 50,
        **filters: Any,
    ) -> List[Market]:
        """Search markets by query string.

        Args:
            query: Search query
            limit: Maximum number of results
            **filters: Additional filter parameters

        Returns:
            List of matching Market objects

        Raises:
            GammaAPIError: For API errors
        """
        return await self.get_markets(
            limit=limit,
            question=query,  # Search in question field
            **filters,
        )

    def get_sync(self, market_id: str, include_tag: bool = False) -> Market:
        """Synchronous version of get_market_by_id for convenience."""
        import asyncio

        return asyncio.run(self.get_market_by_id(market_id, include_tag))

"""
Tags API endpoints for the Gamma SDK.
"""

from typing import Optional, AsyncIterator, List, Any

import httpx

from .base import BaseEndpoint
from ..models.tags import Tag
from ..exceptions import TagNotFoundError, GammaAPIError


class TagsEndpoint(BaseEndpoint[Tag]):
    """Tags API endpoints."""

    async def get_tag_by_id(
        self,
        tag_id: str,
        include_template: bool = False,
    ) -> Tag:
        """Get tag by ID.

        Based on API documentation:
        GET /tags/{id}

        Args:
            tag_id: Tag identifier
            include_template: Include template information in the response

        Returns:
            Tag object

        Raises:
            TagNotFoundError: If tag not found
            GammaAPIError: For other API errors
        """
        # Build query parameters
        params = {"include_template": include_template} if include_template else {}

        try:
            response = await self._get(f"/tags/{tag_id}", params=params)
            tag = await self._parse_response(response, Tag)

            if self.client.config.debug:
                print(f"Successfully fetched tag: {tag.label}")

            return tag

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise TagNotFoundError(tag_id)
            else:
                raise GammaAPIError(
                    f"Failed to get tag {tag_id}: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=e.response.json() if e.response.content else None,
                )

    async def get_tags(
        self,
        limit: int = 100,
        offset: int = 0,
        order: Optional[str] = None,
        ascending: Optional[bool] = None,
        include_template: Optional[bool] = None,
        is_carousel: Optional[bool] = None,
        **kwargs: Any,
    ) -> List[Tag]:
        """List tags.

        Based on API documentation:
        GET /tags

        Args:
            limit: Maximum number of results to return (min: 0)
            offset: Number of results to skip for pagination (min: 0)
            order: Comma-separated list of fields to order by
            ascending: Sort order (true for ascending, false for descending)
            include_template: Include template tags in the response
            is_carousel: Filter by carousel flag
            **kwargs: Additional query parameters

        Returns:
            List of Tag objects

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
            include_template=include_template,
            is_carousel=is_carousel,
            **kwargs,
        )

        try:
            response = await self._get("/tags", params=params)
            tags = await self._parse_response_list(response, Tag)

            if self.client.config.debug:
                print(f"Successfully fetched {len(tags)} tags")

            return tags

        except httpx.HTTPStatusError as e:
            raise GammaAPIError(
                f"Failed to get tags: {e.response.text}",
                status_code=e.response.status_code,
                response_data=e.response.json() if e.response.content else None,
            )

    async def iter_all_tags(
        self,
        page_size: int = 100,
        **filters: Any,
    ) -> AsyncIterator[Tag]:
        """Iterate through all tags using pagination.

        Args:
            page_size: Number of tags per page
            **filters: Filter parameters from get_tags()

        Yields:
            Tag objects

        Raises:
            GammaAPIError: For API errors
        """
        page_size = self._validate_page_size(page_size, max_size=1000)

        if self.client.config.debug:
            print(f"Starting pagination through tags with page_size={page_size}")

        async for tag in self._paginate(
            "/tags",
            Tag,
            limit=page_size,
            **filters,
        ):
            yield tag

    async def search_tags(
        self,
        query: str,
        limit: int = 50,
        **filters: Any,
    ) -> List[Tag]:
        """Search tags by query string.

        Args:
            query: Search query (searches in label field)
            limit: Maximum number of results
            **filters: Additional filter parameters

        Returns:
            List of matching Tag objects

        Raises:
            GammaAPIError: For API errors
        """
        # Note: API documentation doesn't specify search functionality for tags
        # This is a convenience method that filters after fetching
        all_tags = await self.get_tags(limit=limit, **filters)

        if not query:
            return all_tags

        query_lower = query.lower()
        return [
            tag for tag in all_tags if tag.label and query_lower in tag.label.lower()
        ]

    async def get_carousel_tags(
        self,
        limit: int = 100,
        **filters: Any,
    ) -> List[Tag]:
        """Get carousel tags.

        Args:
            limit: Maximum number of results
            **filters: Additional filter parameters

        Returns:
            List of carousel Tag objects

        Raises:
            GammaAPIError: For API errors
        """
        return await self.get_tags(limit=limit, is_carousel=True, **filters)

    def get_sync(self, tag_id: str, include_template: bool = False) -> Tag:
        """Synchronous version of get_tag_by_id for convenience."""
        import asyncio

        return asyncio.run(self.get_tag_by_id(tag_id, include_template))

    def list_sync(self, limit: int = 100, offset: int = 0, **kwargs: Any) -> List[Tag]:
        """Synchronous version of get_tags for convenience."""
        import asyncio

        return asyncio.run(self.get_tags(limit=limit, offset=offset, **kwargs))

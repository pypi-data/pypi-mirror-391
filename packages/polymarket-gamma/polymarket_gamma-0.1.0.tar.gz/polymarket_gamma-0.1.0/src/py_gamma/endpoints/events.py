"""
Events API endpoints for the Gamma SDK.
"""

from typing import Optional, AsyncIterator, List, Any

import httpx

from .base import BaseEndpoint
from ..models.events import Event
from ..exceptions import EventNotFoundError, GammaAPIError


class EventsEndpoint(BaseEndpoint[Event]):
    """Events API endpoints."""

    async def get_event_by_id(
        self,
        event_id: str,
        include_chat: bool = False,
        include_template: bool = False,
    ) -> Event:
        """Get event by ID.

        Based on API documentation:
        GET /events/{id}

        Args:
            event_id: Event identifier
            include_chat: Include chat data in response
            include_template: Include template data in response

        Returns:
            Event object

        Raises:
            EventNotFoundError: If event not found
            GammaAPIError: For other API errors
        """
        # Build query parameters
        params = {}
        if include_chat:
            params["include_chat"] = True
        if include_template:
            params["include_template"] = True

        try:
            response = await self._get(f"/events/{event_id}", params=params)
            event = await self._parse_response(response, Event)

            if self.client.config.debug:
                print(f"Successfully fetched event: {event.title}")

            return event

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise EventNotFoundError(event_id)
            else:
                raise GammaAPIError(
                    f"Failed to get event {event_id}: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=e.response.json() if e.response.content else None,
                )

    async def get_event_by_slug(
        self,
        slug: str,
        include_chat: bool = False,
        include_template: bool = False,
    ) -> Event:
        """Get event by slug.

        Based on API documentation:
        GET /events/slug/{slug}

        Args:
            slug: URL-friendly event identifier
            include_chat: Include chat data in response
            include_template: Include template data in response

        Returns:
            Event object

        Raises:
            EventNotFoundError: If event not found
            GammaAPIError: For other API errors
        """
        # Build query parameters
        params = {}
        if include_chat:
            params["include_chat"] = True
        if include_template:
            params["include_template"] = True

        try:
            response = await self._get(f"/events/slug/{slug}", params=params)
            event = await self._parse_response(response, Event)

            if self.client.config.debug:
                print(f"Successfully fetched event by slug '{slug}': {event.title}")

            return event

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise EventNotFoundError(f"slug={slug}")
            else:
                raise GammaAPIError(
                    f"Failed to get event by slug '{slug}': {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=e.response.json() if e.response.content else None,
                )

    async def get_events(
        self,
        limit: int = 100,
        offset: int = 0,
        order: Optional[str] = None,
        ascending: Optional[bool] = None,
        id: Optional[List[int]] = None,
        slug: Optional[List[str]] = None,
        tag_id: Optional[int] = None,
        exclude_tag_id: Optional[List[int]] = None,
        related_tags: Optional[bool] = None,
        featured: Optional[bool] = None,
        cyom: Optional[bool] = None,
        include_chat: Optional[bool] = None,
        include_template: Optional[bool] = None,
        recurrence: Optional[str] = None,
        closed: Optional[bool] = None,
        start_date_min: Optional[str] = None,
        start_date_max: Optional[str] = None,
        end_date_min: Optional[str] = None,
        end_date_max: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Event]:
        """List events.

        Based on API documentation:
        GET /events

        Args:
            limit: Number of events to return (max 1000)
            offset: Number of events to skip
            order: Fields to order results by (comma-separated)
            ascending: Sort direction (true for ascending)
            id: Filter by specific event IDs
            slug: Filter by specific event slugs
            tag_id: Filter by tag ID
            exclude_tag_id: Exclude events with these tag IDs
            related_tags: Include related tags in response
            featured: Filter for featured events only
            cyom: Filter for CYOM (Create Your Own Market) events
            include_chat: Include chat data in response
            include_template: Include template data in response
            recurrence: Filter by recurrence type
            closed: Filter for closed events only
            start_date_min: Minimum start date filter (ISO 8601 format)
            start_date_max: Maximum start date filter (ISO 8601 format)
            end_date_min: Minimum end date filter (ISO 8601 format)
            end_date_max: Maximum end date filter (ISO 8601 format)
            **kwargs: Additional query parameters

        Returns:
            List of Event objects

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
            id=id,
            slug=slug,
            tag_id=tag_id,
            exclude_tag_id=exclude_tag_id,
            related_tags=related_tags,
            featured=featured,
            cyom=cyom,
            include_chat=include_chat,
            include_template=include_template,
            recurrence=recurrence,
            closed=closed,
            start_date_min=start_date_min,
            start_date_max=start_date_max,
            end_date_min=end_date_min,
            end_date_max=end_date_max,
            **kwargs,
        )

        try:
            response = await self._get("/events", params=params)
            events = await self._parse_response_list(response, Event)

            if self.client.config.debug:
                print(f"Successfully fetched {len(events)} events")

            return events

        except httpx.HTTPStatusError as e:
            raise GammaAPIError(
                f"Failed to get events: {e.response.text}",
                status_code=e.response.status_code,
                response_data=e.response.json() if e.response.content else None,
            )

    async def iter_all_events(
        self,
        page_size: int = 100,
        **filters: Any,
    ) -> AsyncIterator[Event]:
        """Iterate through all events using pagination.

        Args:
            page_size: Number of events per page
            **filters: Filter parameters from get_events()

        Yields:
            Event objects

        Raises:
            GammaAPIError: For API errors
        """
        page_size = self._validate_page_size(page_size, max_size=1000)

        if self.client.config.debug:
            print(f"Starting pagination through events with page_size={page_size}")

        async for event in self._paginate(
            "/events",
            Event,
            limit=page_size,
            **filters,
        ):
            yield event

    async def get_featured_events(
        self,
        limit: int = 50,
        **filters: Any,
    ) -> List[Event]:
        """Get featured events.

        Args:
            limit: Maximum number of results
            **filters: Additional filter parameters

        Returns:
            List of featured Event objects

        Raises:
            GammaAPIError: For API errors
        """
        return await self.get_events(
            limit=limit,
            featured=True,
            **filters,
        )

    async def get_active_events(
        self,
        limit: int = 100,
        **filters: Any,
    ) -> List[Event]:
        """Get active events.

        Args:
            limit: Maximum number of results
            **filters: Additional filter parameters

        Returns:
            List of active Event objects

        Raises:
            GammaAPIError: For API errors
        """
        return await self.get_events(
            limit=limit,
            closed=False,
            **filters,
        )

    async def get_closed_events(
        self,
        limit: int = 100,
        **filters: Any,
    ) -> List[Event]:
        """Get closed events.

        Args:
            limit: Maximum number of results
            **filters: Additional filter parameters

        Returns:
            List of closed Event objects

        Raises:
            GammaAPIError: For API errors
        """
        return await self.get_events(
            limit=limit,
            closed=True,
            **filters,
        )

    async def search_events(
        self,
        query: str,
        limit: int = 50,
        **filters: Any,
    ) -> List[Event]:
        """Search events by query string.

        Args:
            query: Search query
            limit: Maximum number of results
            **filters: Additional filter parameters

        Returns:
            List of matching Event objects

        Raises:
            GammaAPIError: For API errors
        """
        return await self.get_events(
            limit=limit,
            # Search in title and description fields
            # Note: API doesn't seem to have a dedicated search parameter for events
            # This might need to be adjusted based on actual API capabilities
            **filters,
        )

    async def get_events_by_tag(
        self,
        tag_id: int,
        limit: int = 100,
        **filters: Any,
    ) -> List[Event]:
        """Get events by tag ID.

        Args:
            tag_id: Tag identifier
            limit: Maximum number of results
            **filters: Additional filter parameters

        Returns:
            List of Event objects with the specified tag

        Raises:
            GammaAPIError: For API errors
        """
        return await self.get_events(
            limit=limit,
            tag_id=tag_id,
            **filters,
        )

    async def get_events_by_date_range(
        self,
        start_date_min: Optional[str] = None,
        start_date_max: Optional[str] = None,
        end_date_min: Optional[str] = None,
        end_date_max: Optional[str] = None,
        limit: int = 100,
        **filters: Any,
    ) -> List[Event]:
        """Get events within a specific date range.

        Args:
            start_date_min: Minimum start date (ISO 8601 format)
            start_date_max: Maximum start date (ISO 8601 format)
            end_date_min: Minimum end date (ISO 8601 format)
            end_date_max: Maximum end date (ISO 8601 format)
            limit: Maximum number of results
            **filters: Additional filter parameters

        Returns:
            List of Event objects within the date range

        Raises:
            GammaAPIError: For API errors
        """
        return await self.get_events(
            limit=limit,
            start_date_min=start_date_min,
            start_date_max=start_date_max,
            end_date_min=end_date_min,
            end_date_max=end_date_max,
            **filters,
        )

    def get_sync(
        self, event_id: str, include_chat: bool = False, include_template: bool = False
    ) -> Event:
        """Synchronous version of get_event_by_id for convenience."""
        import asyncio

        return asyncio.run(
            self.get_event_by_id(event_id, include_chat, include_template)
        )

    def get_by_slug_sync(
        self, slug: str, include_chat: bool = False, include_template: bool = False
    ) -> Event:
        """Synchronous version of get_event_by_slug for convenience."""
        import asyncio

        return asyncio.run(self.get_event_by_slug(slug, include_chat, include_template))

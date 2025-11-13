"""
Sports API endpoints for the Gamma SDK.
"""

from typing import Optional, AsyncIterator, List, Any

import httpx

from .base import BaseEndpoint
from ..models.sports import Sport, League, SportEvent
from ..exceptions import SportNotFoundError, LeagueNotFoundError, GammaAPIError


def _parse_response_data(error_response: httpx.Response) -> Optional[Any]:
    """Parse response data safely, handling non-JSON responses."""
    if not error_response.content:
        return None
    try:
        return error_response.json()
    except Exception:
        # If JSON parsing fails, return the raw text
        return error_response.text


class SportsEndpoint(BaseEndpoint[Any]):
    """Sports API endpoints."""

    # Sports endpoints

    async def get_sports(self) -> List[Sport]:
        """Get all sports categories.

        Based on API documentation:
        GET /sports

        Returns:
            List of Sport objects

        Raises:
            GammaAPIError: For API errors
        """
        try:
            response = await self._get("/sports")
            sports = await self._parse_response_list(response, Sport)

            if self.client.config.debug:
                print(f"Successfully fetched {len(sports)} sports")

            return sports

        except httpx.HTTPStatusError as e:
            raise GammaAPIError(
                f"Failed to get sports: {e.response.text}",
                status_code=e.response.status_code,
                response_data=_parse_response_data(e.response),
            )

    async def get_sport_by_identifier(
        self,
        sport_identifier: str,
    ) -> Sport:
        """Get sport by identifier (abbreviation).

        Args:
            sport_identifier: Sport identifier or abbreviation

        Returns:
            Sport object

        Raises:
            SportNotFoundError: If sport not found
            GammaAPIError: For other API errors
        """
        try:
            # First get all sports and find the matching one
            sports = await self.get_sports()

            for sport in sports:
                if sport.sport == sport_identifier:
                    if self.client.config.debug:
                        print(f"Successfully fetched sport: {sport.sport}")
                    return sport

            # If not found, raise error
            raise SportNotFoundError(sport_identifier)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise SportNotFoundError(sport_identifier)
            else:
                raise GammaAPIError(
                    f"Failed to get sport {sport_identifier}: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=_parse_response_data(e.response),
                )

    # League endpoints

    async def get_leagues_for_sport(
        self,
        sport_id: str,
        limit: int = 100,
        offset: int = 0,
        active: Optional[bool] = None,
        featured: Optional[bool] = None,
        **kwargs: Any,
    ) -> List[League]:
        """Get leagues for a specific sport.

        Based on API documentation:
        GET /sports/{id}/leagues

        Args:
            sport_id: Sport identifier
            limit: Number of leagues to return (max 1000)
            offset: Number of leagues to skip
            active: Filter by active status
            featured: Filter by featured status
            **kwargs: Additional query parameters

        Returns:
            List of League objects

        Raises:
            SportNotFoundError: If sport not found
            GammaAPIError: For API errors
        """
        # Validate page size
        limit = self._validate_page_size(limit, max_size=1000)

        # Build query parameters
        params = self._build_params(
            limit=limit,
            offset=offset,
            active=active,
            featured=featured,
            **kwargs,
        )

        try:
            response = await self._get(f"/sports/{sport_id}/leagues", params=params)
            leagues = await self._parse_response_list(response, League)

            if self.client.config.debug:
                print(
                    f"Successfully fetched {len(leagues)} leagues for sport {sport_id}"
                )

            return leagues

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise SportNotFoundError(sport_id)
            else:
                raise GammaAPIError(
                    f"Failed to get leagues for sport {sport_id}: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=_parse_response_data(e.response),
                )

    async def get_league_by_id(
        self,
        league_id: str,
    ) -> League:
        """Get league by ID.

        Based on API documentation:
        GET /sports/leagues/{id}

        Args:
            league_id: League identifier

        Returns:
            League object

        Raises:
            LeagueNotFoundError: If league not found
            GammaAPIError: For other API errors
        """
        try:
            response = await self._get(f"/sports/leagues/{league_id}")
            league = await self._parse_response(response, League)

            if self.client.config.debug:
                print(f"Successfully fetched league: {league.name or league.id}")

            return league

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise LeagueNotFoundError(league_id)
            else:
                raise GammaAPIError(
                    f"Failed to get league {league_id}: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=_parse_response_data(e.response),
                )

    async def get_events_for_league(
        self,
        league_id: str,
        limit: int = 100,
        offset: int = 0,
        active: Optional[bool] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs: Any,
    ) -> List[SportEvent]:
        """Get events for a specific league.

        Based on API documentation:
        GET /sports/leagues/{id}/events

        Args:
            league_id: League identifier
            limit: Number of events to return (max 1000)
            offset: Number of events to skip
            active: Filter by active status
            status: Filter by event status
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            **kwargs: Additional query parameters

        Returns:
            List of SportEvent objects

        Raises:
            LeagueNotFoundError: If league not found
            GammaAPIError: For API errors
        """
        # Validate page size
        limit = self._validate_page_size(limit, max_size=1000)

        # Build query parameters
        params = self._build_params(
            limit=limit,
            offset=offset,
            active=active,
            status=status,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )

        try:
            response = await self._get(
                f"/sports/leagues/{league_id}/events", params=params
            )
            events = await self._parse_response_list(response, SportEvent)

            if self.client.config.debug:
                print(
                    f"Successfully fetched {len(events)} events for league {league_id}"
                )

            return events

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise LeagueNotFoundError(league_id)
            else:
                raise GammaAPIError(
                    f"Failed to get events for league {league_id}: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=_parse_response_data(e.response),
                )

    # Iterator methods

    async def iter_all_leagues_for_sport(
        self,
        sport_id: str,
        page_size: int = 100,
        **filters: Any,
    ) -> AsyncIterator[League]:
        """Iterate through all leagues for a sport using pagination.

        Args:
            sport_id: Sport identifier
            page_size: Number of leagues per page
            **filters: Filter parameters from get_leagues_for_sport()

        Yields:
            League objects

        Raises:
            SportNotFoundError: If sport not found
            GammaAPIError: For API errors
        """
        page_size = self._validate_page_size(page_size, max_size=1000)

        if self.client.config.debug:
            print(
                f"Starting pagination through leagues for sport {sport_id} with page_size={page_size}"
            )

        async for league in self._paginate(
            f"/sports/{sport_id}/leagues",
            League,
            limit=page_size,
            **filters,
        ):
            yield league

    async def iter_all_events_for_league(
        self,
        league_id: str,
        page_size: int = 100,
        **filters: Any,
    ) -> AsyncIterator[SportEvent]:
        """Iterate through all events for a league using pagination.

        Args:
            league_id: League identifier
            page_size: Number of events per page
            **filters: Filter parameters from get_events_for_league()

        Yields:
            SportEvent objects

        Raises:
            LeagueNotFoundError: If league not found
            GammaAPIError: For API errors
        """
        page_size = self._validate_page_size(page_size, max_size=1000)

        if self.client.config.debug:
            print(
                f"Starting pagination through events for league {league_id} with page_size={page_size}"
            )

        async for event in self._paginate(
            f"/sports/leagues/{league_id}/events",
            SportEvent,
            limit=page_size,
            **filters,
        ):
            yield event

    # Search methods

    async def search_leagues(
        self,
        sport_id: str,
        query: str,
        limit: int = 50,
        **filters: Any,
    ) -> List[League]:
        """Search leagues by query string.

        Args:
            sport_id: Sport identifier
            query: Search query
            limit: Maximum number of results
            **filters: Additional filter parameters

        Returns:
            List of matching League objects

        Raises:
            SportNotFoundError: If sport not found
            GammaAPIError: For API errors
        """
        return await self.get_leagues_for_sport(
            sport_id,
            limit=limit,
            # Note: This would need to be adjusted based on actual API search capabilities
            **filters,
        )

    async def search_events(
        self,
        league_id: str,
        query: str,
        limit: int = 50,
        **filters: Any,
    ) -> List[SportEvent]:
        """Search events by query string.

        Args:
            league_id: League identifier
            query: Search query
            limit: Maximum number of results
            **filters: Additional filter parameters

        Returns:
            List of matching SportEvent objects

        Raises:
            LeagueNotFoundError: If league not found
            GammaAPIError: For API errors
        """
        return await self.get_events_for_league(
            league_id,
            limit=limit,
            # Note: This would need to be adjusted based on actual API search capabilities
            **filters,
        )

    # Synchronous convenience methods

    def get_sports_sync(self) -> List[Sport]:
        """Synchronous version of get_sports for convenience."""
        import asyncio

        return asyncio.run(self.get_sports())

    def get_sport_by_identifier_sync(self, sport_identifier: str) -> Sport:
        """Synchronous version of get_sport_by_identifier for convenience."""
        import asyncio

        return asyncio.run(self.get_sport_by_identifier(sport_identifier))

    def get_leagues_for_sport_sync(self, sport_id: str, **kwargs: Any) -> List[League]:
        """Synchronous version of get_leagues_for_sport for convenience."""
        import asyncio

        return asyncio.run(self.get_leagues_for_sport(sport_id, **kwargs))

    def get_league_by_id_sync(self, league_id: str) -> League:
        """Synchronous version of get_league_by_id for convenience."""
        import asyncio

        return asyncio.run(self.get_league_by_id(league_id))

    def get_events_for_league_sync(
        self, league_id: str, **kwargs: Any
    ) -> List[SportEvent]:
        """Synchronous version of get_events_for_league for convenience."""
        import asyncio

        return asyncio.run(self.get_events_for_league(league_id, **kwargs))

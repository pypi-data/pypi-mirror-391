"""
User API endpoints for the Gamma SDK.
"""

from typing import Optional, AsyncIterator, List, Any
import asyncio

import httpx

from .base import BaseEndpoint
from ..models.user import (
    Profile,
    User,
    Position,
    UserStats,
    UserHistory,
    PositionList,
    UserHistoryList,
)
from ..exceptions import (
    UserNotFoundError,
    ProfileNotFoundError,
    UserStatsNotFoundError,
    ProfileAccessDeniedError,
    GammaAPIError,
)


class UserEndpoint(BaseEndpoint[Profile]):
    """User API endpoints."""

    async def get_profile(self) -> Profile:
        """Get current user's profile.

        Based on API documentation:
        GET /profile

        Returns:
            Profile object for the authenticated user

        Raises:
            AuthenticationError: If not authenticated
            GammaAPIError: For other API errors
        """
        try:
            response = await self._get("/profile")
            profile = await self._parse_response(response, Profile)

            if self.client.config.debug:
                print(f"Successfully fetched profile for user: {profile.username}")

            return profile

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                from ..exceptions import AuthenticationError
                raise AuthenticationError("Authentication required to access profile")
            elif e.response.status_code == 403:
                raise ProfileAccessDeniedError("current_user")
            else:
                raise GammaAPIError(
                    f"Failed to get profile: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=e.response.json() if e.response.content else None,
                )

    async def get_profile_by_id(
        self,
        user_id: str,
    ) -> Profile:
        """Get user profile by ID.

        Based on API documentation:
        GET /profile/{id}

        Args:
            user_id: User identifier

        Returns:
            Profile object for the specified user

        Raises:
            ProfileNotFoundError: If profile not found
            ProfileAccessDeniedError: If access is denied
            GammaAPIError: For other API errors
        """
        try:
            response = await self._get(f"/profile/{user_id}")
            profile = await self._parse_response(response, Profile)

            if self.client.config.debug:
                print(
                    f"Successfully fetched profile for user {user_id}: {profile.username}"
                )

            return profile

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ProfileNotFoundError(user_id)
            elif e.response.status_code == 403:
                raise ProfileAccessDeniedError(user_id)
            else:
                raise GammaAPIError(
                    f"Failed to get profile {user_id}: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=e.response.json() if e.response.content else None,
                )

    async def get_positions(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        active_only: bool = False,
        market_id: Optional[str] = None,
        outcome: Optional[str] = None,
        **kwargs: Any,
    ) -> PositionList:
        """Get user's positions.

        Based on API documentation:
        GET /profile/{id}/positions (if user_id provided)
        GET /profile/positions (for current user)

        Args:
            user_id: User identifier (None for current user)
            limit: Number of positions to return (max 1000)
            offset: Number of positions to skip
            active_only: Filter to only active positions
            market_id: Filter by market ID
            outcome: Filter by outcome name
            **kwargs: Additional query parameters

        Returns:
            PositionList object containing user positions

        Raises:
            ProfileNotFoundError: If user not found
            ProfileAccessDeniedError: If access is denied
            GammaAPIError: For other API errors
        """
        # Validate page size
        limit = self._validate_page_size(limit, max_size=1000)

        # Build query parameters
        params = self._build_params(
            limit=limit,
            offset=offset,
            active_only=active_only,
            market_id=market_id,
            outcome=outcome,
            **kwargs,
        )

        # Determine endpoint path
        path = f"/profile/{user_id}/positions" if user_id else "/profile/positions"

        try:
            response = await self._get(path, params=params)

            # Parse response manually since _parse_response expects the base type
            try:
                data = await self._safe_json_parse(response)
                if isinstance(data, list):
                    positions_list = [Position(**item) for item in data]
                    positions = PositionList(
                        positions=positions_list, limit=limit, offset=offset, total=None, hasMore=None
                    )
                elif isinstance(data, dict):
                    positions = PositionList(**data)
                else:
                    raise GammaAPIError(f"Unexpected response format: {type(data)}")
            except Exception as e:
                if isinstance(e, GammaAPIError):
                    raise
                raise GammaAPIError(f"Failed to parse positions response: {e}")

            if self.client.config.debug:
                print(
                    f"Successfully fetched {positions.count} positions for user {user_id or 'current'}"
                )

            return positions

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                if user_id:
                    raise ProfileNotFoundError(user_id)
                else:
                    raise UserNotFoundError("current_user")
            elif e.response.status_code == 403:
                raise ProfileAccessDeniedError(user_id or "current_user")
            else:
                raise GammaAPIError(
                    f"Failed to get positions: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=e.response.json() if e.response.content else None,
                )

    async def get_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        transaction_type: Optional[str] = None,
        market_id: Optional[str] = None,
        outcome: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs: Any,
    ) -> UserHistoryList:
        """Get user's transaction history.

        Based on API documentation:
        GET /profile/{id}/history (if user_id provided)
        GET /profile/history (for current user)

        Args:
            user_id: User identifier (None for current user)
            limit: Number of history entries to return (max 1000)
            offset: Number of history entries to skip
            transaction_type: Filter by transaction type
            market_id: Filter by market ID
            outcome: Filter by outcome name
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            **kwargs: Additional query parameters

        Returns:
            UserHistoryList object containing user history

        Raises:
            ProfileNotFoundError: If user not found
            ProfileAccessDeniedError: If access is denied
            GammaAPIError: For other API errors
        """
        # Validate page size
        limit = self._validate_page_size(limit, max_size=1000)

        # Build query parameters
        params = self._build_params(
            limit=limit,
            offset=offset,
            transaction_type=transaction_type,
            market_id=market_id,
            outcome=outcome,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )

        # Determine endpoint path
        path = f"/profile/{user_id}/history" if user_id else "/profile/history"

        try:
            response = await self._get(path, params=params)

            # Parse response manually since _parse_response expects the base type
            try:
                data = await self._safe_json_parse(response)
                if isinstance(data, list):
                    history_list = [UserHistory(**item) for item in data]
                    history = UserHistoryList(
                        history=history_list, limit=limit, offset=offset, total=None, hasMore=None
                    )
                elif isinstance(data, dict):
                    history = UserHistoryList(**data)
                else:
                    raise GammaAPIError(f"Unexpected response format: {type(data)}")
            except Exception as e:
                if isinstance(e, GammaAPIError):
                    raise
                raise GammaAPIError(f"Failed to parse history response: {e}")

            if self.client.config.debug:
                print(
                    f"Successfully fetched {history.count} history entries for user {user_id or 'current'}"
                )

            return history

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                if user_id:
                    raise ProfileNotFoundError(user_id)
                else:
                    raise UserNotFoundError("current_user")
            elif e.response.status_code == 403:
                raise ProfileAccessDeniedError(user_id or "current_user")
            else:
                raise GammaAPIError(
                    f"Failed to get history: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=e.response.json() if e.response.content else None,
                )

    async def get_stats(
        self,
        user_id: Optional[str] = None,
        **kwargs: Any,
    ) -> UserStats:
        """Get user's statistics.

        Based on API documentation:
        GET /profile/{id}/stats (if user_id provided)
        GET /profile/stats (for current user)

        Args:
            user_id: User identifier (None for current user)
            **kwargs: Additional query parameters

        Returns:
            UserStats object containing user statistics

        Raises:
            UserStatsNotFoundError: If stats not found
            ProfileNotFoundError: If user not found
            ProfileAccessDeniedError: If access is denied
            GammaAPIError: For other API errors
        """
        # Build query parameters
        params = self._build_params(**kwargs)

        # Determine endpoint path
        path = f"/profile/{user_id}/stats" if user_id else "/profile/stats"

        try:
            response = await self._get(path, params=params)

            # Parse response manually
            try:
                data = await self._safe_json_parse(response)
                stats = UserStats(**data)
            except Exception as e:
                raise GammaAPIError(f"Failed to parse stats response: {e}")

            if self.client.config.debug:
                print(f"Successfully fetched stats for user {user_id or 'current'}")

            return stats

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                if user_id:
                    raise UserStatsNotFoundError(user_id)
                else:
                    raise UserStatsNotFoundError("current_user")
            elif e.response.status_code == 403:
                raise ProfileAccessDeniedError(user_id or "current_user")
            else:
                raise GammaAPIError(
                    f"Failed to get stats: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=e.response.json() if e.response.content else None,
                )

    async def get_user(
        self,
        user_id: str,
        include_stats: bool = False,
        include_positions: bool = False,
        include_history: bool = False,
        positions_limit: int = 50,
        history_limit: int = 50,
        **kwargs: Any,
    ) -> User:
        """Get complete user information including profile and optional data.

        This is a convenience method that combines multiple API calls to get
        a complete view of a user including their profile and optionally their
        positions, history, and stats.

        Args:
            user_id: User identifier
            include_stats: Whether to include user statistics
            include_positions: Whether to include user positions
            include_history: Whether to include user history
            positions_limit: Limit for positions if included
            history_limit: Limit for history if included
            **kwargs: Additional parameters for sub-calls

        Returns:
            User object with profile and optional additional data

        Raises:
            ProfileNotFoundError: If user not found
            ProfileAccessDeniedError: If access is denied
            GammaAPIError: For other API errors
        """
        # Get the profile first (required)
        profile = await self.get_profile_by_id(user_id)

        # Initialize optional data
        stats: Optional[UserStats] = None
        positions: Optional[List[Position]] = None
        history: Optional[List[UserHistory]] = None

        # Fetch optional data in parallel if requested
        if include_stats or include_positions or include_history:
            tasks = []

            if include_stats:
                tasks.append(("stats", self.get_stats(user_id, **kwargs)))

            if include_positions:
                tasks.append(
                    (
                        "positions",
                        self.get_positions(user_id, limit=positions_limit, **kwargs),
                    )
                )

            if include_history:
                tasks.append(
                    (
                        "history",
                        self.get_history(user_id, limit=history_limit, **kwargs),
                    )
                )

            # Execute all tasks concurrently
            if tasks:
                results = await asyncio.gather(
                    *[task for _, task in tasks],
                    return_exceptions=True,
                )

                # Process results
                for (name, _), result in zip(tasks, results):
                    if isinstance(result, Exception):
                        # Log error but continue with other data
                        if self.client.config.debug:
                            print(f"Failed to get {name} for user {user_id}: {result}")
                    else:
                        if name == "stats":
                            if not isinstance(result, Exception):
                                stats = result  # type: ignore[assignment]
                        elif name == "positions":
                            if not isinstance(result, Exception):
                                positions = result.positions  # type: ignore[assignment]
                        elif name == "history":
                            if not isinstance(result, Exception):
                                history = result.history  # type: ignore[assignment]

        return User(
            profile=profile,
            stats=stats,
            positions=positions,
            history=history,
        )

    async def iter_all_positions(
        self,
        user_id: Optional[str] = None,
        page_size: int = 100,
        **filters: Any,
    ) -> AsyncIterator[Position]:
        """Iterate through all user positions using pagination.

        Args:
            user_id: User identifier (None for current user)
            page_size: Number of positions per page
            **filters: Filter parameters from get_positions()

        Yields:
            Position objects

        Raises:
            ProfileNotFoundError: If user not found
            ProfileAccessDeniedError: If access is denied
            GammaAPIError: For other API errors
        """
        page_size = self._validate_page_size(page_size, max_size=1000)

        if self.client.config.debug:
            print(
                f"Starting pagination through positions for user {user_id or 'current'} with page_size={page_size}"
            )

        offset = 0
        while True:
            # Get a page of positions
            positions_page = await self.get_positions(
                user_id=user_id,
                limit=page_size,
                offset=offset,
                **filters,
            )

            # Yield positions from this page
            for position in positions_page.positions:
                yield position

            # Check if we got fewer positions than requested (last page)
            if len(positions_page.positions) < page_size:
                break

            # Prepare for next page
            offset += page_size

    async def iter_all_history(
        self,
        user_id: Optional[str] = None,
        page_size: int = 100,
        **filters: Any,
    ) -> AsyncIterator[UserHistory]:
        """Iterate through all user history using pagination.

        Args:
            user_id: User identifier (None for current user)
            page_size: Number of history entries per page
            **filters: Filter parameters from get_history()

        Yields:
            UserHistory objects

        Raises:
            ProfileNotFoundError: If user not found
            ProfileAccessDeniedError: If access is denied
            GammaAPIError: For other API errors
        """
        page_size = self._validate_page_size(page_size, max_size=1000)

        if self.client.config.debug:
            print(
                f"Starting pagination through history for user {user_id or 'current'} with page_size={page_size}"
            )

        offset = 0
        while True:
            # Get a page of history
            history_page = await self.get_history(
                user_id=user_id,
                limit=page_size,
                offset=offset,
                **filters,
            )

            # Yield history entries from this page
            for entry in history_page.history:
                yield entry

            # Check if we got fewer entries than requested (last page)
            if len(history_page.history) < page_size:
                break

            # Prepare for next page
            offset += page_size

    # Synchronous convenience methods
    def get_profile_sync(self) -> Profile:
        """Synchronous version of get_profile."""
        return asyncio.run(self.get_profile())

    def get_profile_by_id_sync(self, user_id: str) -> Profile:
        """Synchronous version of get_profile_by_id."""
        return asyncio.run(self.get_profile_by_id(user_id))

    def get_positions_sync(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        active_only: bool = False,
        market_id: Optional[str] = None,
        outcome: Optional[str] = None,
        **kwargs: Any,
    ) -> PositionList:
        """Synchronous version of get_positions."""
        return asyncio.run(
            self.get_positions(
                user_id=user_id,
                limit=limit,
                offset=offset,
                active_only=active_only,
                market_id=market_id,
                outcome=outcome,
                **kwargs,
            )
        )

    def get_history_sync(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        transaction_type: Optional[str] = None,
        market_id: Optional[str] = None,
        outcome: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs: Any,
    ) -> UserHistoryList:
        """Synchronous version of get_history."""
        return asyncio.run(
            self.get_history(
                user_id=user_id,
                limit=limit,
                offset=offset,
                transaction_type=transaction_type,
                market_id=market_id,
                outcome=outcome,
                start_date=start_date,
                end_date=end_date,
                **kwargs,
            )
        )

    def get_stats_sync(
        self,
        user_id: Optional[str] = None,
        **kwargs: Any,
    ) -> UserStats:
        """Synchronous version of get_stats."""
        return asyncio.run(self.get_stats(user_id, **kwargs))

    def get_user_sync(
        self,
        user_id: str,
        include_stats: bool = False,
        include_positions: bool = False,
        include_history: bool = False,
        positions_limit: int = 50,
        history_limit: int = 50,
        **kwargs: Any,
    ) -> User:
        """Synchronous version of get_user."""
        return asyncio.run(
            self.get_user(
                user_id=user_id,
                include_stats=include_stats,
                include_positions=include_positions,
                include_history=include_history,
                positions_limit=positions_limit,
                history_limit=history_limit,
                **kwargs,
            )
        )
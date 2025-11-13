"""
Custom exception classes for the Py-Gamma SDK.
"""

from typing import Optional, Any, Dict


class GammaAPIError(Exception):
    """Base exception for all Gamma API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self) -> str:
        if self.status_code:
            return f"GammaAPIError({self.status_code}): {self.message}"
        return f"GammaAPIError: {self.message}"


class GammaNetworkError(GammaAPIError):
    """Raised when network errors occur (timeouts, connection issues, etc.)."""

    def __init__(self, message: str, retry_count: int = 0) -> None:
        super().__init__(message)
        self.retry_count = retry_count


class AuthenticationError(GammaAPIError):
    """Raised when authentication fails (invalid API key, etc.)."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, status_code=401)


class RateLimitError(GammaAPIError):
    """Raised when rate limits are exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ) -> None:
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class MarketNotFoundError(GammaAPIError):
    """Raised when a market is not found."""

    def __init__(self, market_id: str) -> None:
        super().__init__(f"Market {market_id} not found", status_code=404)
        self.market_id = market_id


class EventNotFoundError(GammaAPIError):
    """Raised when an event is not found."""

    def __init__(self, event_id: str) -> None:
        super().__init__(f"Event {event_id} not found", status_code=404)
        self.event_id = event_id


class TagNotFoundError(GammaAPIError):
    """Raised when a tag is not found."""

    def __init__(self, tag_id: str) -> None:
        super().__init__(f"Tag {tag_id} not found", status_code=404)
        self.tag_id = tag_id


class SeriesNotFoundError(GammaAPIError):
    """Raised when a series is not found."""

    def __init__(self, series_id: str) -> None:
        super().__init__(f"Series {series_id} not found", status_code=404)
        self.series_id = series_id


class SportNotFoundError(GammaAPIError):
    """Raised when a sport is not found."""

    def __init__(self, sport_id: str) -> None:
        super().__init__(f"Sport {sport_id} not found", status_code=404)
        self.sport_id = sport_id


class LeagueNotFoundError(GammaAPIError):
    """Raised when a league is not found."""

    def __init__(self, league_id: str) -> None:
        super().__init__(f"League {league_id} not found", status_code=404)
        self.league_id = league_id


class SportEventNotFoundError(GammaAPIError):
    """Raised when a sport event is not found."""

    def __init__(self, event_id: str) -> None:
        super().__init__(f"Sport event {event_id} not found", status_code=404)
        self.event_id = event_id


class CommentNotFoundError(GammaAPIError):
    """Raised when a comment is not found."""

    def __init__(self, comment_id: str) -> None:
        super().__init__(f"Comment {comment_id} not found", status_code=404)
        self.comment_id = comment_id


class SearchValidationError(GammaAPIError):
    """Raised when search query parameters are invalid."""

    def __init__(self, message: str, query: Optional[str] = None) -> None:
        super().__init__(message, status_code=400)
        self.query = query


class SearchTimeoutError(GammaAPIError):
    """Raised when a search request times out."""

    def __init__(self, query: str, timeout_seconds: int) -> None:
        super().__init__(
            f"Search timeout for query '{query}' after {timeout_seconds} seconds"
        )
        self.query = query
        self.timeout_seconds = timeout_seconds


class SearchQuotaExceededError(GammaAPIError):
    """Raised when search quota limits are exceeded."""

    def __init__(self, message: str = "Search quota exceeded") -> None:
        super().__init__(message, status_code=429)


class ProfileNotFoundError(GammaAPIError):
    """Raised when a profile is not found."""

    def __init__(self, profile_id: str) -> None:
        super().__init__(f"Profile {profile_id} not found", status_code=404)
        self.profile_id = profile_id


class ValidationError(GammaAPIError):
    """Raised when data validation fails."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        super().__init__(message)
        self.field = field


class UserNotFoundError(GammaAPIError):
    """Raised when a user is not found."""

    def __init__(self, user_id: str) -> None:
        super().__init__(f"User {user_id} not found", status_code=404)
        self.user_id = user_id




class PositionNotFoundError(GammaAPIError):
    """Raised when a user position is not found."""

    def __init__(self, position_id: str) -> None:
        super().__init__(f"Position {position_id} not found", status_code=404)
        self.position_id = position_id


class UserStatsNotFoundError(GammaAPIError):
    """Raised when user statistics are not found."""

    def __init__(self, user_id: str) -> None:
        super().__init__(f"Statistics for user {user_id} not found", status_code=404)
        self.user_id = user_id


class UserHistoryNotFoundError(GammaAPIError):
    """Raised when user history is not found."""

    def __init__(self, user_id: str) -> None:
        super().__init__(f"History for user {user_id} not found", status_code=404)
        self.user_id = user_id


class InsufficientPermissionsError(GammaAPIError):
    """Raised when user lacks permissions to access a resource."""

    def __init__(
        self, message: str = "Insufficient permissions to access this resource"
    ) -> None:
        super().__init__(message, status_code=403)


class ProfileAccessDeniedError(GammaAPIError):
    """Raised when access to a user profile is denied."""

    def __init__(self, user_id: str) -> None:
        super().__init__(f"Access denied to profile {user_id}", status_code=403)
        self.user_id = user_id

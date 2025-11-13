"""
Py-Gamma: Modern Python SDK for Polymarket Gamma API

A async-first Python client with strict type safety and comprehensive caching.
"""

from .client import GammaClient
from .config import GammaConfig
from .models import (
    Tag,
    Sport,
    League,
    SportEvent,
    Series,
    SeriesList,
    Event,
    EventList,
    Profile,
    User,
    UserSettings,
    PrivacySettings,
    Position,
    UserStats,
    UserHistory,
    UserList,
    PositionList,
    UserHistoryList,
    ProfileVisibility,
    SearchResult,
)
from .endpoints import (
    TagsEndpoint,
    SportsEndpoint,
    SeriesEndpoint,
    EventsEndpoint,
    UserEndpoint,
    SearchEndpoint,
)
from .exceptions import (
    GammaAPIError,
    GammaNetworkError,
    MarketNotFoundError,
    TagNotFoundError,
    SportNotFoundError,
    LeagueNotFoundError,
    SportEventNotFoundError,
    SeriesNotFoundError,
    EventNotFoundError,
    AuthenticationError,
    RateLimitError,
    UserNotFoundError,
    ProfileNotFoundError,
    PositionNotFoundError,
    UserStatsNotFoundError,
    UserHistoryNotFoundError,
    InsufficientPermissionsError,
    ProfileAccessDeniedError,
    SearchValidationError,
)

__version__ = "0.1.0"
__all__ = [
    "GammaClient",
    "GammaConfig",
    # Models
    "Tag",
    "Sport",
    "League",
    "SportEvent",
    "Series",
    "SeriesList",
    "Event",
    "EventList",
    # User models
    "Profile",
    "User",
    "UserSettings",
    "PrivacySettings",
    "Position",
    "UserStats",
    "UserHistory",
    "UserList",
    "PositionList",
    "UserHistoryList",
    "ProfileVisibility",
    "SearchResult",
    # Endpoints
    "TagsEndpoint",
    "SportsEndpoint",
    "SeriesEndpoint",
    "EventsEndpoint",
    "UserEndpoint",
    "SearchEndpoint",
    # Exceptions
    "GammaAPIError",
    "GammaNetworkError",
    "MarketNotFoundError",
    "TagNotFoundError",
    "SportNotFoundError",
    "LeagueNotFoundError",
    "SportEventNotFoundError",
    "SeriesNotFoundError",
    "EventNotFoundError",
    "AuthenticationError",
    "RateLimitError",
    # User exceptions
    "UserNotFoundError",
    "ProfileNotFoundError",
    "PositionNotFoundError",
    "UserStatsNotFoundError",
    "UserHistoryNotFoundError",
    "InsufficientPermissionsError",
    "ProfileAccessDeniedError",
    "SearchValidationError",
]

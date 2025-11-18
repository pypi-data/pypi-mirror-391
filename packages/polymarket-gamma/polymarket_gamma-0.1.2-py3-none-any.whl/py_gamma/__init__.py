"""
Py-Gamma: Modern Python SDK for Polymarket Gamma API

A async-first Python client with strict type safety and comprehensive caching.
"""

from .client import GammaClient
from .config import GammaConfig
from .endpoints import (
    EventsEndpoint,
    SearchEndpoint,
    SeriesEndpoint,
    SportsEndpoint,
    TagsEndpoint,
    UserEndpoint,
)
from .exceptions import (
    AuthenticationError,
    EventNotFoundError,
    GammaAPIError,
    GammaNetworkError,
    InsufficientPermissionsError,
    LeagueNotFoundError,
    MarketNotFoundError,
    PositionNotFoundError,
    ProfileAccessDeniedError,
    ProfileNotFoundError,
    RateLimitError,
    SearchValidationError,
    SeriesNotFoundError,
    SportEventNotFoundError,
    SportNotFoundError,
    TagNotFoundError,
    UserHistoryNotFoundError,
    UserNotFoundError,
    UserStatsNotFoundError,
)
from .models import (
    Event,
    EventList,
    League,
    Position,
    PositionList,
    PrivacySettings,
    Profile,
    ProfileVisibility,
    SearchResult,
    Series,
    SeriesList,
    Sport,
    SportEvent,
    Tag,
    User,
    UserHistory,
    UserHistoryList,
    UserList,
    UserSettings,
    UserStats,
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

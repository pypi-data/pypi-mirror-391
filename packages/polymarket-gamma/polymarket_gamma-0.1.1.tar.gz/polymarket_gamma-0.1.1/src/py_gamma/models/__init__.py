"""
Pydantic models for Gamma API data structures.
"""

# Base models
from .base import BaseGammaModel

# Domain models
from .markets import Market, MarketList, Category, OutcomePrice
from .tags import Tag
from .sports import Sport, League, SportEvent, SportList, LeagueList, SportEventList
from .series import (
    Series,
    SeriesList,
    SeriesCategory,
    SeriesTag,
    SeriesEvent,
    SeriesCollection,
    SeriesChat,
)
from .user import (
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
)

# Event models (excluding Series which is now in series.py)
from .events import Event, EventList, Collection, ImageOptimization, Chat, Template

# Comments models
from .comments import Comment, CommentList, CommentProfile, Reaction

# Import will be added as models are implemented
# from .tags import TagList
# from .tags import TagList
# Search models
from .search import (
    SearchResult,
    SearchMarket,
    SearchEvent,
    SearchCategory,
    SearchEventTag,
    SearchTag,
    SearchPagination,
)

__all__ = [
    "BaseGammaModel",
    "Market",
    "MarketList",
    "Category",
    "Tag",
    "OutcomePrice",
    # Sports models
    "Sport",
    "League",
    "SportEvent",
    "SportList",
    "LeagueList",
    "SportEventList",
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
    # Event models
    "Event",
    "EventList",
    "Collection",
    "ImageOptimization",
    "Chat",
    "Template",
    # Series models (from series.py)
    "Series",
    "SeriesList",
    "SeriesCategory",
    "SeriesTag",
    "SeriesEvent",
    "SeriesCollection",
    "SeriesChat",
    # Comments models
    "Comment",
    "CommentList",
    "CommentProfile",
    "Reaction",
    # Note: Series is imported from series.py as the main Series model
    # Search models
    "SearchResult",
    "SearchMarket",
    "SearchEvent",
    "SearchCategory",
    "SearchEventTag",
    "SearchTag",
    "SearchPagination",
    # Add model exports as they are implemented
]

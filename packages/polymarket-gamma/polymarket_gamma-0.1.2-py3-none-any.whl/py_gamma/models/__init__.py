"""
Pydantic models for Gamma API data structures.
"""

# Base models
from .base import BaseGammaModel

# Comments models
from .comments import Comment, CommentList, CommentProfile, Reaction

# Event models (excluding Series which is now in series.py)
from .events import Chat, Collection, Event, EventList, ImageOptimization, Template

# Domain models
from .markets import Category, Market, MarketList, OutcomePrice

# Import will be added as models are implemented
# from .tags import TagList
# from .tags import TagList
# Search models
from .search import (
    SearchCategory,
    SearchEvent,
    SearchEventTag,
    SearchMarket,
    SearchPagination,
    SearchResult,
    SearchTag,
)
from .series import (
    Series,
    SeriesCategory,
    SeriesChat,
    SeriesCollection,
    SeriesEvent,
    SeriesList,
    SeriesTag,
)
from .sports import League, LeagueList, Sport, SportEvent, SportEventList, SportList
from .tags import Tag
from .user import (
    Position,
    PositionList,
    PrivacySettings,
    Profile,
    ProfileVisibility,
    User,
    UserHistory,
    UserHistoryList,
    UserList,
    UserSettings,
    UserStats,
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

"""
API endpoint implementations for the Gamma SDK.
"""

from .base import BaseEndpoint

# Import endpoint classes as they are implemented
from .markets import MarketsEndpoint
from .tags import TagsEndpoint
from .sports import SportsEndpoint
from .events import EventsEndpoint
from .series import SeriesEndpoint
from .user import UserEndpoint
from .comments import CommentsEndpoint
from .search import SearchEndpoint

__all__ = [
    "BaseEndpoint",
    "MarketsEndpoint",
    "TagsEndpoint",
    "SportsEndpoint",
    "EventsEndpoint",
    "SeriesEndpoint",
    "UserEndpoint",
    "CommentsEndpoint",
    "SearchEndpoint",
    # Add endpoint exports as they are implemented
]

"""
API endpoint implementations for the Gamma SDK.
"""

from .base import BaseEndpoint
from .comments import CommentsEndpoint
from .events import EventsEndpoint

# Import endpoint classes as they are implemented
from .markets import MarketsEndpoint
from .search import SearchEndpoint
from .series import SeriesEndpoint
from .sports import SportsEndpoint
from .tags import TagsEndpoint
from .user import UserEndpoint

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

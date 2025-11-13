"""
Event models for the Gamma API.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Union

from pydantic import Field, model_validator, field_validator

from .base import BaseGammaModel
from .markets import Market, Category, Tag


class ImageOptimization(BaseGammaModel):
    """Model for optimized image data."""

    small: Optional[str] = Field(None, description="Small image URL")
    medium: Optional[str] = Field(None, description="Medium image URL")
    large: Optional[str] = Field(None, description="Large image URL")
    thumbnail: Optional[str] = Field(None, description="Thumbnail URL")


class Collection(BaseGammaModel):
    """Collection model for event collections."""

    id: Optional[str] = Field(None, description="Collection identifier")
    slug: Optional[str] = Field(None, description="URL-friendly slug")
    name: Optional[str] = Field(None, description="Collection name")
    description: Optional[str] = Field(None, description="Collection description")
    image: Optional[str] = Field(None, description="Collection image URL")
    created_at: Optional[datetime] = Field(
        None, alias="createdAt", description="Creation date"
    )
    updated_at: Optional[datetime] = Field(
        None, alias="updatedAt", description="Last update date"
    )

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Optional[datetime]:
        """Parse datetime from string or return None."""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None


class Series(BaseGammaModel):
    """Series model for recurring events."""

    id: Optional[str] = Field(None, description="Series identifier")
    slug: Optional[str] = Field(None, description="URL-friendly slug")
    name: Optional[str] = Field(None, description="Series name")
    description: Optional[str] = Field(None, description="Series description")
    recurrence: Optional[str] = Field(None, description="Recurrence pattern")
    created_at: Optional[datetime] = Field(
        None, alias="createdAt", description="Creation date"
    )
    updated_at: Optional[datetime] = Field(
        None, alias="updatedAt", description="Last update date"
    )

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Optional[datetime]:
        """Parse datetime from string or return None."""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None


class Chat(BaseGammaModel):
    """Chat model for event chat data."""

    id: Optional[str] = Field(None, description="Chat identifier")
    enabled: Optional[bool] = Field(None, description="Whether chat is enabled")
    message_count: Optional[int] = Field(
        None, alias="messageCount", description="Number of messages"
    )
    participant_count: Optional[int] = Field(
        None, alias="participantCount", description="Number of participants"
    )
    last_message: Optional[Dict[str, Any]] = Field(
        None, alias="lastMessage", description="Last message data"
    )


class Template(BaseGammaModel):
    """Template model for event template data."""

    id: Optional[str] = Field(None, description="Template identifier")
    name: Optional[str] = Field(None, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    structure: Optional[Dict[str, Any]] = Field(
        None, description="Template structure data"
    )


class Event(BaseGammaModel):
    """Event model based on Gamma API documentation."""

    # Core fields
    id: str = Field(..., description="Event identifier")
    ticker: Optional[str] = Field(None, description="Event ticker symbol")
    slug: str = Field(..., description="URL-friendly identifier")
    title: str = Field(..., description="Event title")
    subtitle: Optional[str] = Field(None, description="Event subtitle")
    description: str = Field(..., description="Event description")

    # Resolution and dates
    resolution_source: Optional[str] = Field(
        None, alias="resolutionSource", description="Source of event resolution"
    )
    start_date: Optional[datetime] = Field(
        None, alias="startDate", description="Event start date"
    )
    creation_date: Optional[datetime] = Field(
        None, alias="creationDate", description="Event creation date"
    )
    end_date: Optional[datetime] = Field(
        None, alias="endDate", description="Event end date"
    )
    closed_time: Optional[datetime] = Field(
        None, alias="closedTime", description="Event closure time"
    )

    # Status flags
    active: Optional[bool] = Field(None, description="Whether event is active")
    closed: Optional[bool] = Field(None, description="Whether event is closed")
    archived: Optional[bool] = Field(None, description="Whether event is archived")
    featured: Optional[bool] = Field(None, description="Whether event is featured")
    restricted: Optional[bool] = Field(None, description="Whether event is restricted")

    # Trading data
    liquidity: Optional[Union[float, str]] = Field(
        None, description="Total liquidity in event"
    )
    volume: Optional[Union[float, str]] = Field(
        None, description="Total trading volume"
    )
    open_interest: Optional[Union[float, str]] = Field(
        None, alias="openInterest", description="Open interest amount"
    )
    volume_24hr: Optional[Union[float, str]] = Field(
        None, alias="volume24hr", description="24-hour trading volume"
    )
    volume_1wk: Optional[Union[float, str]] = Field(
        None, alias="volume1wk", description="1-week trading volume"
    )
    volume_1mo: Optional[Union[float, str]] = Field(
        None, alias="volume1mo", description="1-month trading volume"
    )
    volume_1yr: Optional[Union[float, str]] = Field(
        None, alias="volume1yr", description="1-year trading volume"
    )

    # Nested objects
    markets: List[Market] = Field(
        default_factory=list, description="Associated markets"
    )
    categories: List[Category] = Field(
        default_factory=list, description="Event categories"
    )
    tags: List[Tag] = Field(default_factory=list, description="Event tags")
    collections: List[Collection] = Field(
        default_factory=list, description="Event collections"
    )
    series: List[Series] = Field(default_factory=list, description="Associated series")

    # Media
    image: Optional[str] = Field(None, description="Event image URL")
    icon: Optional[str] = Field(None, description="Event icon URL")
    featured_image: Optional[str] = Field(
        None, alias="featuredImage", description="Featured image URL"
    )

    # Optimized images
    image_optimized: Optional[ImageOptimization] = Field(
        None, alias="imageOptimized", description="Optimized image data"
    )
    icon_optimized: Optional[ImageOptimization] = Field(
        None, alias="iconOptimized", description="Optimized icon data"
    )
    featured_image_optimized: Optional[ImageOptimization] = Field(
        None,
        alias="featuredImageOptimized",
        description="Optimized featured image data",
    )

    # Optional data (when requested)
    chat: Optional[Chat] = Field(None, description="Chat data (if included)")
    template: Optional[Template] = Field(
        None, description="Template data (if included)"
    )

    @field_validator(
        "start_date", "creation_date", "end_date", "closed_time", mode="before"
    )
    @classmethod
    def parse_datetime(cls, v: Any) -> Optional[datetime]:
        """Parse datetime from string or return None."""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                # Fallback for various datetime formats
                return None
        return None

    @field_validator(
        "liquidity",
        "volume",
        "open_interest",
        "volume_24hr",
        "volume_1wk",
        "volume_1mo",
        "volume_1yr",
        mode="before",
    )
    @classmethod
    def parse_numeric_field(cls, v: Any) -> Optional[Union[float, str]]:
        """Parse numeric fields that might be strings."""
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                return v  # Keep original string if conversion fails
        return None

    @model_validator(mode="before")
    @classmethod
    def parse_api_response(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse API response data and handle field conversions."""
        # Handle nested objects
        if "markets" in data and isinstance(data["markets"], list):
            data["markets"] = [
                Market(**market) if isinstance(market, dict) else market
                for market in data["markets"]
            ]

        if "categories" in data and isinstance(data["categories"], list):
            data["categories"] = [
                Category(**cat) if isinstance(cat, dict) else cat
                for cat in data["categories"]
            ]

        if "tags" in data and isinstance(data["tags"], list):
            data["tags"] = [
                Tag(**tag) if isinstance(tag, dict) else tag for tag in data["tags"]
            ]

        if "collections" in data and isinstance(data["collections"], list):
            data["collections"] = [
                Collection(**collection) if isinstance(collection, dict) else collection
                for collection in data["collections"]
            ]

        if "series" in data and isinstance(data["series"], list):
            data["series"] = [
                Series(**series_item) if isinstance(series_item, dict) else series_item
                for series_item in data["series"]
            ]

        # Handle optimized image objects
        for image_field in [
            "imageOptimized",
            "iconOptimized",
            "featuredImageOptimized",
        ]:
            if image_field in data and isinstance(data[image_field], dict):
                data[image_field] = ImageOptimization(**data[image_field])

        # Handle optional chat and template objects
        if "chat" in data and isinstance(data["chat"], dict):
            data["chat"] = Chat(**data["chat"])

        if "template" in data and isinstance(data["template"], dict):
            data["template"] = Template(**data["template"])

        return data

    @property
    def is_expired(self) -> bool:
        """Check if event has expired."""
        if self.end_date is None:
            return False
        return datetime.now(timezone.utc) > self.end_date

    @property
    def is_upcoming(self) -> bool:
        """Check if event is upcoming."""
        if self.start_date is None:
            return False
        return datetime.now(timezone.utc) < self.start_date

    @property
    def is_active_period(self) -> bool:
        """Check if event is currently in its active period."""
        now = datetime.now(timezone.utc)
        if self.start_date and self.end_date:
            return self.start_date <= now <= self.end_date
        return self.active or False

    @property
    def market_count(self) -> int:
        """Get the number of associated markets."""
        return len(self.markets)

    @property
    def category_count(self) -> int:
        """Get the number of categories."""
        return len(self.categories)

    @property
    def tag_count(self) -> int:
        """Get the number of tags."""
        return len(self.tags)

    def get_tag_by_label(self, label: str) -> Optional[Tag]:
        """Find a tag by its label."""
        for tag in self.tags:
            if tag.label == label:
                return tag
        return None

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Find a category by name."""
        for category in self.categories:
            if category.name == name:
                return category
        return None

    def get_market_by_id(self, market_id: str) -> Optional[Market]:
        """Find a market by ID."""
        for market in self.markets:
            if market.id == market_id:
                return market
        return None

    def get_featured_markets(self) -> List[Market]:
        """Get all featured markets."""
        return [
            market for market in self.markets if getattr(market, "is_featured", False)
        ]

    def get_active_markets(self) -> List[Market]:
        """Get all active markets."""
        return [market for market in self.markets if getattr(market, "active", True)]


class EventList(BaseGammaModel):
    """Container for a list of events."""

    events: List[Event] = Field(default_factory=list, description="List of events")
    total: Optional[int] = Field(None, description="Total number of events")
    limit: Optional[int] = Field(None, description="Page size limit")
    offset: Optional[int] = Field(None, description="Page offset")
    has_more: Optional[bool] = Field(
        None, alias="hasMore", description="Whether more events are available"
    )

    @property
    def count(self) -> int:
        """Get the number of events in this list."""
        return len(self.events)

    @property
    def featured_events(self) -> List[Event]:
        """Get all featured events."""
        return [event for event in self.events if getattr(event, "featured", False)]

    @property
    def active_events(self) -> List[Event]:
        """Get all active events."""
        return [event for event in self.events if getattr(event, "active", True)]

    @property
    def closed_events(self) -> List[Event]:
        """Get all closed events."""
        return [event for event in self.events if getattr(event, "closed", False)]

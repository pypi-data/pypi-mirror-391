"""
Series models for the Gamma API.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import Field, model_validator, field_validator

from .base import BaseGammaModel


class ImageOptimization(BaseGammaModel):
    """Image optimization data for responsive images."""

    src: Optional[str] = Field(None, description="Optimized image source URL")
    src_set: Optional[str] = Field(
        None, alias="srcSet", description="Responsive image source set"
    )
    sizes: Optional[str] = Field(None, description="Image size descriptors")
    width: Optional[int] = Field(None, description="Image width")
    height: Optional[int] = Field(None, description="Image height")
    aspect_ratio: Optional[float] = Field(
        None, alias="aspectRatio", description="Image aspect ratio"
    )


class SeriesCategory(BaseGammaModel):
    """Category model for series categorization."""

    id: Optional[str] = Field(None, description="Category identifier")
    label: Optional[str] = Field(None, description="Category label")
    slug: Optional[str] = Field(None, description="URL-friendly slug")
    parent_category: Optional[str] = Field(
        None, alias="parentCategory", description="Parent category identifier"
    )
    published_at: Optional[datetime] = Field(
        None, alias="publishedAt", description="Publication timestamp"
    )
    created_by: Optional[str] = Field(
        None, alias="createdBy", description="Creator identifier"
    )
    updated_by: Optional[str] = Field(
        None, alias="updatedBy", description="Last updater identifier"
    )
    created_at: Optional[datetime] = Field(
        None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        None, alias="updatedAt", description="Last update timestamp"
    )

    @field_validator("published_at", "created_at", "updated_at", mode="before")
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


class SeriesTag(BaseGammaModel):
    """Tag model for series tags."""

    id: Optional[str] = Field(None, description="Tag identifier")
    label: Optional[str] = Field(None, description="Tag label")
    slug: Optional[str] = Field(None, description="URL-friendly slug")
    force_show: Optional[bool] = Field(
        None, alias="forceShow", description="Force show in UI"
    )
    force_hide: Optional[bool] = Field(
        None, alias="forceHide", description="Force hide in UI"
    )
    is_carousel: Optional[bool] = Field(
        None, alias="isCarousel", description="Show in carousel"
    )
    published_at: Optional[datetime] = Field(
        None, alias="publishedAt", description="Publication timestamp"
    )
    created_by: Optional[int] = Field(None, alias="createdBy", description="Creator ID")
    updated_by: Optional[int] = Field(None, alias="updatedBy", description="Updater ID")
    created_at: Optional[datetime] = Field(
        None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        None, alias="updatedAt", description="Last update timestamp"
    )

    @field_validator("published_at", "created_at", "updated_at", mode="before")
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


class SeriesEvent(BaseGammaModel):
    """Event model for series events."""

    id: Optional[str] = Field(None, description="Event identifier")
    ticker: Optional[str] = Field(None, description="Event ticker")
    slug: Optional[str] = Field(None, description="Event slug")
    title: Optional[str] = Field(None, description="Event title")
    subtitle: Optional[str] = Field(None, description="Event subtitle")
    description: Optional[str] = Field(None, description="Event description")
    image: Optional[str] = Field(None, description="Event image URL")
    icon: Optional[str] = Field(None, description="Event icon URL")
    active: Optional[bool] = Field(None, description="Whether event is active")
    closed: Optional[bool] = Field(None, description="Whether event is closed")
    archived: Optional[bool] = Field(None, description="Whether event is archived")
    new: Optional[bool] = Field(None, description="Whether event is marked as new")
    featured: Optional[bool] = Field(None, description="Whether event is featured")
    restricted: Optional[bool] = Field(
        None, description="Whether event has restrictions"
    )
    start_date: Optional[datetime] = Field(
        None, alias="startDate", description="Event start date"
    )
    end_date: Optional[datetime] = Field(
        None, alias="endDate", description="Event end date"
    )
    volume: Optional[float] = Field(None, description="Total trading volume")
    volume24hr: Optional[float] = Field(
        None, alias="volume24hr", description="24-hour trading volume"
    )

    @field_validator("start_date", "end_date", mode="before")
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


class SeriesCollection(BaseGammaModel):
    """Collection model for series collections."""

    id: Optional[str] = Field(None, description="Collection identifier")
    ticker: Optional[str] = Field(None, description="Collection ticker")
    slug: Optional[str] = Field(None, description="Collection slug")
    title: Optional[str] = Field(None, description="Collection title")
    subtitle: Optional[str] = Field(None, description="Collection subtitle")
    collection_type: Optional[str] = Field(
        None, alias="collectionType", description="Type of collection"
    )
    description: Optional[str] = Field(None, description="Collection description")
    image: Optional[str] = Field(None, description="Collection image URL")
    icon: Optional[str] = Field(None, description="Collection icon URL")
    header_image: Optional[str] = Field(
        None, alias="headerImage", description="Header image URL"
    )
    active: Optional[bool] = Field(None, description="Whether collection is active")
    closed: Optional[bool] = Field(None, description="Whether collection is closed")
    archived: Optional[bool] = Field(None, description="Whether collection is archived")
    image_optimized: Optional[ImageOptimization] = Field(
        None, alias="imageOptimized", description="Optimized image data"
    )
    icon_optimized: Optional[ImageOptimization] = Field(
        None, alias="iconOptimized", description="Optimized icon data"
    )
    header_image_optimized: Optional[ImageOptimization] = Field(
        None, alias="headerImageOptimized", description="Optimized header image data"
    )


class SeriesChat(BaseGammaModel):
    """Chat model for series chat rooms."""

    id: Optional[str] = Field(None, description="Chat identifier")
    channel_id: Optional[str] = Field(
        None, alias="channelId", description="Chat channel ID"
    )
    channel_name: Optional[str] = Field(
        None, alias="channelName", description="Chat channel name"
    )
    channel_image: Optional[str] = Field(
        None, alias="channelImage", description="Chat channel image URL"
    )
    live: Optional[bool] = Field(None, description="Whether chat is currently live")
    start_time: Optional[datetime] = Field(
        None, alias="startTime", description="Chat start time"
    )
    end_time: Optional[datetime] = Field(
        None, alias="endTime", description="Chat end time"
    )

    @field_validator("start_time", "end_time", mode="before")
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
    """Series model based on Gamma API documentation."""

    # Core fields
    id: str = Field(..., description="Unique identifier for the series")
    ticker: Optional[str] = Field(None, description="Series ticker symbol")
    slug: Optional[str] = Field(None, description="URL-friendly slug for the series")
    title: Optional[str] = Field(None, description="Series title")
    subtitle: Optional[str] = Field(None, description="Series subtitle")

    # Series classification
    series_type: Optional[str] = Field(
        None, alias="seriesType", description="Type of series"
    )
    recurrence: Optional[str] = Field(None, description="Recurrence pattern")
    layout: Optional[str] = Field(None, description="Layout type for the series")

    # Content
    description: Optional[str] = Field(None, description="Series description")
    image: Optional[str] = Field(None, description="Series image URL")
    icon: Optional[str] = Field(None, description="Series icon URL")

    # Status flags
    active: Optional[bool] = Field(None, description="Whether the series is active")
    closed: Optional[bool] = Field(None, description="Whether the series is closed")
    archived: Optional[bool] = Field(None, description="Whether the series is archived")
    new: Optional[bool] = Field(None, description="Whether the series is marked as new")
    featured: Optional[bool] = Field(None, description="Whether the series is featured")
    restricted: Optional[bool] = Field(
        None, description="Whether the series has restrictions"
    )
    is_template: Optional[bool] = Field(
        None, alias="isTemplate", description="Whether this is a template series"
    )
    template_variables: Optional[bool] = Field(
        None, alias="templateVariables", description="Template variables configuration"
    )

    # Interaction settings
    comments_enabled: Optional[bool] = Field(
        None, alias="commentsEnabled", description="Whether comments are enabled"
    )

    # Trading data
    competitive: Optional[str] = Field(None, description="Competitive status")
    volume24hr: Optional[float] = Field(
        None, alias="volume24hr", description="24-hour trading volume"
    )
    volume: Optional[float] = Field(None, description="Total trading volume")
    liquidity: Optional[float] = Field(None, description="Liquidity measure")

    # External integrations
    pyth_token_id: Optional[str] = Field(
        None, alias="pythTokenID", description="Pyth token identifier"
    )
    cg_asset_name: Optional[str] = Field(
        None, alias="cgAssetName", description="CoinGecko asset name"
    )

    # Metadata
    score: Optional[int] = Field(None, description="Series score")
    comment_count: Optional[int] = Field(
        None, alias="commentCount", description="Number of comments"
    )

    # Timestamps
    published_at: Optional[datetime] = Field(
        None, alias="publishedAt", description="Publication timestamp"
    )
    created_by: Optional[str] = Field(
        None, alias="createdBy", description="Creator identifier"
    )
    updated_by: Optional[str] = Field(
        None, alias="updatedBy", description="Last updater identifier"
    )
    created_at: Optional[datetime] = Field(
        None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        None, alias="updatedAt", description="Last update timestamp"
    )
    start_date: Optional[datetime] = Field(
        None, alias="startDate", description="Start date"
    )

    # Nested objects
    events: Optional[List[SeriesEvent]] = Field(
        default_factory=list, description="Events in this series"
    )
    collections: Optional[List[SeriesCollection]] = Field(
        default_factory=list, description="Collections in this series"
    )
    categories: Optional[List[SeriesCategory]] = Field(
        default_factory=list, description="Categories for this series"
    )
    tags: Optional[List[SeriesTag]] = Field(
        default_factory=list, description="Tags for this series"
    )
    chats: Optional[List[SeriesChat]] = Field(
        default_factory=list, description="Chat rooms for this series"
    )

    @field_validator(
        "published_at", "created_at", "updated_at", "start_date", mode="before"
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
                return None
        return None

    @model_validator(mode="before")
    @classmethod
    def parse_api_response(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse API response data and handle field conversions."""
        # Handle numeric fields that might be strings
        numeric_fields = ["volume24hr", "volume", "liquidity", "score", "comment_count"]
        for field in numeric_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = float(data[field])
                except (ValueError, TypeError):
                    pass
            elif field in data and isinstance(data[field], (int, float)):
                data[field] = float(data[field])

        # Handle nested objects
        if "events" in data and isinstance(data["events"], list):
            data["events"] = [
                SeriesEvent(**event) if isinstance(event, dict) else event
                for event in data["events"]
            ]

        if "collections" in data and isinstance(data["collections"], list):
            data["collections"] = [
                SeriesCollection(**collection)
                if isinstance(collection, dict)
                else collection
                for collection in data["collections"]
            ]

        if "categories" in data and isinstance(data["categories"], list):
            data["categories"] = [
                SeriesCategory(**category) if isinstance(category, dict) else category
                for category in data["categories"]
            ]

        if "tags" in data and isinstance(data["tags"], list):
            data["tags"] = [
                SeriesTag(**tag) if isinstance(tag, dict) else tag
                for tag in data["tags"]
            ]

        if "chats" in data and isinstance(data["chats"], list):
            data["chats"] = [
                SeriesChat(**chat) if isinstance(chat, dict) else chat
                for chat in data["chats"]
            ]

        return data

    @property
    def is_expired(self) -> bool:
        """Check if series has expired based on end dates of events."""
        if not self.events:
            return False
        # Consider series expired if all events are past their end dates
        now = datetime.now()
        for event in self.events:
            if event.end_date is None or event.end_date > now:
                return False
        return True

    @property
    def event_count(self) -> int:
        """Get the number of events in this series."""
        return len(self.events) if self.events else 0

    @property
    def category_count(self) -> int:
        """Get the number of categories for this series."""
        return len(self.categories) if self.categories else 0

    @property
    def tag_count(self) -> int:
        """Get the number of tags for this series."""
        return len(self.tags) if self.tags else 0

    def get_tag_by_label(self, label: str) -> Optional[SeriesTag]:
        """Find a tag by its label."""
        if not self.tags:
            return None
        for tag in self.tags:
            if tag.label == label:
                return tag
        return None

    def get_category_by_name(self, name: str) -> Optional[SeriesCategory]:
        """Find a category by name."""
        if not self.categories:
            return None
        for category in self.categories:
            if category.label == name:
                return category
        return None

    def get_event_by_id(self, event_id: str) -> Optional[SeriesEvent]:
        """Find an event by its ID."""
        if not self.events:
            return None
        for event in self.events:
            if event.id == event_id:
                return event
        return None

    def get_active_events(self) -> List[SeriesEvent]:
        """Get all active events in this series."""
        if not self.events:
            return []
        return [event for event in self.events if event.active]

    def get_closed_events(self) -> List[SeriesEvent]:
        """Get all closed events in this series."""
        if not self.events:
            return []
        return [event for event in self.events if event.closed]


class SeriesList(BaseGammaModel):
    """Container for a list of series."""

    series: List[Series] = Field(default_factory=list, description="List of series")
    total: Optional[int] = Field(None, description="Total number of series")
    limit: Optional[int] = Field(None, description="Page size limit")
    offset: Optional[int] = Field(None, description="Page offset")
    has_more: Optional[bool] = Field(
        None, alias="hasMore", description="Whether more series are available"
    )

    @property
    def count(self) -> int:
        """Get the number of series in this list."""
        return len(self.series)

"""
Series models for the Gamma API.
"""

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator, model_validator

from .base import BaseGammaModel


class ImageOptimization(BaseGammaModel):
    """Image optimization data for responsive images."""

    src: str | None = Field(None, description="Optimized image source URL")
    src_set: str | None = Field(
        None, alias="srcSet", description="Responsive image source set"
    )
    sizes: str | None = Field(None, description="Image size descriptors")
    width: int | None = Field(None, description="Image width")
    height: int | None = Field(None, description="Image height")
    aspect_ratio: float | None = Field(
        None, alias="aspectRatio", description="Image aspect ratio"
    )


class SeriesCategory(BaseGammaModel):
    """Category model for series categorization."""

    id: str | None = Field(None, description="Category identifier")
    label: str | None = Field(None, description="Category label")
    slug: str | None = Field(None, description="URL-friendly slug")
    parent_category: str | None = Field(
        None, alias="parentCategory", description="Parent category identifier"
    )
    published_at: datetime | None = Field(
        None, alias="publishedAt", description="Publication timestamp"
    )
    created_by: str | None = Field(
        None, alias="createdBy", description="Creator identifier"
    )
    updated_by: str | None = Field(
        None, alias="updatedBy", description="Last updater identifier"
    )
    created_at: datetime | None = Field(
        None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: datetime | None = Field(
        None, alias="updatedAt", description="Last update timestamp"
    )

    @field_validator("published_at", "created_at", "updated_at", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime | None:
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

    id: str | None = Field(None, description="Tag identifier")
    label: str | None = Field(None, description="Tag label")
    slug: str | None = Field(None, description="URL-friendly slug")
    force_show: bool | None = Field(
        None, alias="forceShow", description="Force show in UI"
    )
    force_hide: bool | None = Field(
        None, alias="forceHide", description="Force hide in UI"
    )
    is_carousel: bool | None = Field(
        None, alias="isCarousel", description="Show in carousel"
    )
    published_at: datetime | None = Field(
        None, alias="publishedAt", description="Publication timestamp"
    )
    created_by: int | None = Field(None, alias="createdBy", description="Creator ID")
    updated_by: int | None = Field(None, alias="updatedBy", description="Updater ID")
    created_at: datetime | None = Field(
        None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: datetime | None = Field(
        None, alias="updatedAt", description="Last update timestamp"
    )

    @field_validator("published_at", "created_at", "updated_at", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime | None:
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

    id: str | None = Field(None, description="Event identifier")
    ticker: str | None = Field(None, description="Event ticker")
    slug: str | None = Field(None, description="Event slug")
    title: str | None = Field(None, description="Event title")
    subtitle: str | None = Field(None, description="Event subtitle")
    description: str | None = Field(None, description="Event description")
    image: str | None = Field(None, description="Event image URL")
    icon: str | None = Field(None, description="Event icon URL")
    active: bool | None = Field(None, description="Whether event is active")
    closed: bool | None = Field(None, description="Whether event is closed")
    archived: bool | None = Field(None, description="Whether event is archived")
    new: bool | None = Field(None, description="Whether event is marked as new")
    featured: bool | None = Field(None, description="Whether event is featured")
    restricted: bool | None = Field(
        None, description="Whether event has restrictions"
    )
    start_date: datetime | None = Field(
        None, alias="startDate", description="Event start date"
    )
    end_date: datetime | None = Field(
        None, alias="endDate", description="Event end date"
    )
    volume: float | None = Field(None, description="Total trading volume")
    volume24hr: float | None = Field(
        None, alias="volume24hr", description="24-hour trading volume"
    )

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime | None:
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

    id: str | None = Field(None, description="Collection identifier")
    ticker: str | None = Field(None, description="Collection ticker")
    slug: str | None = Field(None, description="Collection slug")
    title: str | None = Field(None, description="Collection title")
    subtitle: str | None = Field(None, description="Collection subtitle")
    collection_type: str | None = Field(
        None, alias="collectionType", description="Type of collection"
    )
    description: str | None = Field(None, description="Collection description")
    image: str | None = Field(None, description="Collection image URL")
    icon: str | None = Field(None, description="Collection icon URL")
    header_image: str | None = Field(
        None, alias="headerImage", description="Header image URL"
    )
    active: bool | None = Field(None, description="Whether collection is active")
    closed: bool | None = Field(None, description="Whether collection is closed")
    archived: bool | None = Field(None, description="Whether collection is archived")
    image_optimized: ImageOptimization | None = Field(
        None, alias="imageOptimized", description="Optimized image data"
    )
    icon_optimized: ImageOptimization | None = Field(
        None, alias="iconOptimized", description="Optimized icon data"
    )
    header_image_optimized: ImageOptimization | None = Field(
        None, alias="headerImageOptimized", description="Optimized header image data"
    )


class SeriesChat(BaseGammaModel):
    """Chat model for series chat rooms."""

    id: str | None = Field(None, description="Chat identifier")
    channel_id: str | None = Field(
        None, alias="channelId", description="Chat channel ID"
    )
    channel_name: str | None = Field(
        None, alias="channelName", description="Chat channel name"
    )
    channel_image: str | None = Field(
        None, alias="channelImage", description="Chat channel image URL"
    )
    live: bool | None = Field(None, description="Whether chat is currently live")
    start_time: datetime | None = Field(
        None, alias="startTime", description="Chat start time"
    )
    end_time: datetime | None = Field(
        None, alias="endTime", description="Chat end time"
    )

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime | None:
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
    ticker: str | None = Field(None, description="Series ticker symbol")
    slug: str | None = Field(None, description="URL-friendly slug for the series")
    title: str | None = Field(None, description="Series title")
    subtitle: str | None = Field(None, description="Series subtitle")

    # Series classification
    series_type: str | None = Field(
        None, alias="seriesType", description="Type of series"
    )
    recurrence: str | None = Field(None, description="Recurrence pattern")
    layout: str | None = Field(None, description="Layout type for the series")

    # Content
    description: str | None = Field(None, description="Series description")
    image: str | None = Field(None, description="Series image URL")
    icon: str | None = Field(None, description="Series icon URL")

    # Status flags
    active: bool | None = Field(None, description="Whether the series is active")
    closed: bool | None = Field(None, description="Whether the series is closed")
    archived: bool | None = Field(None, description="Whether the series is archived")
    new: bool | None = Field(None, description="Whether the series is marked as new")
    featured: bool | None = Field(None, description="Whether the series is featured")
    restricted: bool | None = Field(
        None, description="Whether the series has restrictions"
    )
    is_template: bool | None = Field(
        None, alias="isTemplate", description="Whether this is a template series"
    )
    template_variables: bool | None = Field(
        None, alias="templateVariables", description="Template variables configuration"
    )

    # Interaction settings
    comments_enabled: bool | None = Field(
        None, alias="commentsEnabled", description="Whether comments are enabled"
    )

    # Trading data
    competitive: str | None = Field(None, description="Competitive status")
    volume24hr: float | None = Field(
        None, alias="volume24hr", description="24-hour trading volume"
    )
    volume: float | None = Field(None, description="Total trading volume")
    liquidity: float | None = Field(None, description="Liquidity measure")

    # External integrations
    pyth_token_id: str | None = Field(
        None, alias="pythTokenID", description="Pyth token identifier"
    )
    cg_asset_name: str | None = Field(
        None, alias="cgAssetName", description="CoinGecko asset name"
    )

    # Metadata
    score: int | None = Field(None, description="Series score")
    comment_count: int | None = Field(
        None, alias="commentCount", description="Number of comments"
    )

    # Timestamps
    published_at: datetime | None = Field(
        None, alias="publishedAt", description="Publication timestamp"
    )
    created_by: str | None = Field(
        None, alias="createdBy", description="Creator identifier"
    )
    updated_by: str | None = Field(
        None, alias="updatedBy", description="Last updater identifier"
    )
    created_at: datetime | None = Field(
        None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: datetime | None = Field(
        None, alias="updatedAt", description="Last update timestamp"
    )
    start_date: datetime | None = Field(
        None, alias="startDate", description="Start date"
    )

    # Nested objects
    events: list[SeriesEvent] | None = Field(
        default_factory=list, description="Events in this series"
    )
    collections: list[SeriesCollection] | None = Field(
        default_factory=list, description="Collections in this series"
    )
    categories: list[SeriesCategory] | None = Field(
        default_factory=list, description="Categories for this series"
    )
    tags: list[SeriesTag] | None = Field(
        default_factory=list, description="Tags for this series"
    )
    chats: list[SeriesChat] | None = Field(
        default_factory=list, description="Chat rooms for this series"
    )

    @field_validator(
        "published_at", "created_at", "updated_at", "start_date", mode="before"
    )
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime | None:
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
    def parse_api_response(cls, data: dict[str, Any]) -> dict[str, Any]:
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

    def get_tag_by_label(self, label: str) -> SeriesTag | None:
        """Find a tag by its label."""
        if not self.tags:
            return None
        for tag in self.tags:
            if tag.label == label:
                return tag
        return None

    def get_category_by_name(self, name: str) -> SeriesCategory | None:
        """Find a category by name."""
        if not self.categories:
            return None
        for category in self.categories:
            if category.label == name:
                return category
        return None

    def get_event_by_id(self, event_id: str) -> SeriesEvent | None:
        """Find an event by its ID."""
        if not self.events:
            return None
        for event in self.events:
            if event.id == event_id:
                return event
        return None

    def get_active_events(self) -> list[SeriesEvent]:
        """Get all active events in this series."""
        if not self.events:
            return []
        return [event for event in self.events if event.active]

    def get_closed_events(self) -> list[SeriesEvent]:
        """Get all closed events in this series."""
        if not self.events:
            return []
        return [event for event in self.events if event.closed]


class SeriesList(BaseGammaModel):
    """Container for a list of series."""

    series: list[Series] = Field(default_factory=list, description="List of series")
    total: int | None = Field(None, description="Total number of series")
    limit: int | None = Field(None, description="Page size limit")
    offset: int | None = Field(None, description="Page offset")
    has_more: bool | None = Field(
        None, alias="hasMore", description="Whether more series are available"
    )

    @property
    def count(self) -> int:
        """Get the number of series in this list."""
        return len(self.series)

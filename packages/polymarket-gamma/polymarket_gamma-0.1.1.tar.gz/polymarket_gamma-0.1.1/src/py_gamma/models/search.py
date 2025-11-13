"""
Search result models for the Gamma API.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import Field, model_validator, field_validator

from .base import BaseGammaModel


class SearchMarket(BaseGammaModel):
    """Simplified market model for search results."""

    # Core fields
    id: str = Field(..., description="Market identifier")
    question: str = Field(..., description="The market question")
    slug: Optional[str] = Field(None, description="URL-friendly identifier")

    # Contract information
    condition_id: Optional[str] = Field(
        None, alias="conditionId", description="Smart contract condition ID"
    )

    # Market status
    active: Optional[bool] = Field(
        None, description="Whether market is currently active"
    )
    closed: Optional[bool] = Field(None, description="Whether market is closed")
    end_date: Optional[datetime] = Field(
        None, alias="endDate", description="When market ends"
    )

    # Trading data
    liquidity: Optional[str] = Field(None, description="Available liquidity")
    volume: Optional[str] = Field(None, description="Trading volume")

    @field_validator("end_date", mode="before")
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

    @property
    def is_expired(self) -> bool:
        """Check if market has expired."""
        if self.end_date is None:
            return False
        return datetime.now().astimezone() > self.end_date


class SearchCategory(BaseGammaModel):
    """Category model for search results."""

    id: str = Field(..., description="Category identifier")
    label: Optional[str] = Field(None, description="Category label")
    parent_category: Optional[str] = Field(
        None, alias="parentCategory", description="Parent category identifier"
    )
    slug: Optional[str] = Field(None, description="URL-friendly slug")
    created_at: Optional[datetime] = Field(
        None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        None, alias="updatedAt", description="Last update timestamp"
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


class SearchEventTag(BaseGammaModel):
    """Tag model for search events."""

    id: str = Field(..., description="Tag identifier")
    label: Optional[str] = Field(None, description="Tag label")
    slug: Optional[str] = Field(None, description="URL-friendly slug")
    force_show: Optional[bool] = Field(
        None, alias="forceShow", description="Force show in UI"
    )
    is_carousel: Optional[bool] = Field(
        None, alias="isCarousel", description="Show in carousel"
    )
    created_at: Optional[datetime] = Field(
        None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        None, alias="updatedAt", description="Last update timestamp"
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


class SearchEvent(BaseGammaModel):
    """Event model for search results."""

    # Core fields
    id: str = Field(..., description="Event identifier")
    ticker: Optional[str] = Field(None, description="Event ticker symbol")
    slug: Optional[str] = Field(None, description="URL-friendly slug")
    title: Optional[str] = Field(None, description="Event title")
    subtitle: Optional[str] = Field(None, description="Event subtitle")
    description: Optional[str] = Field(None, description="Event description")

    # Event status
    active: Optional[bool] = Field(None, description="Whether event is active")
    closed: Optional[bool] = Field(None, description="Whether event is closed")

    # Timestamps
    start_date: Optional[datetime] = Field(
        None, alias="startDate", description="Event start date"
    )
    end_date: Optional[datetime] = Field(
        None, alias="endDate", description="Event end date"
    )

    # Nested data
    markets: List[SearchMarket] = Field(
        default_factory=list, description="Associated markets"
    )
    categories: List[SearchCategory] = Field(
        default_factory=list, description="Associated categories"
    )
    tags: List[SearchEventTag] = Field(
        default_factory=list, description="Associated tags"
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

    @model_validator(mode="before")
    @classmethod
    def parse_api_response(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse API response data and handle nested object construction."""
        # Handle nested objects
        if "markets" in data and isinstance(data["markets"], list):
            data["markets"] = [
                SearchMarket(**market) if isinstance(market, dict) else market
                for market in data["markets"]
            ]

        if "categories" in data and isinstance(data["categories"], list):
            data["categories"] = [
                SearchCategory(**category) if isinstance(category, dict) else category
                for category in data["categories"]
            ]

        if "tags" in data and isinstance(data["tags"], list):
            data["tags"] = [
                SearchEventTag(**tag) if isinstance(tag, dict) else tag
                for tag in data["tags"]
            ]

        return data

    @property
    def is_expired(self) -> bool:
        """Check if event has expired."""
        if self.end_date is None:
            return False
        return datetime.now().astimezone() > self.end_date

    @property
    def market_count(self) -> int:
        """Get the number of markets in this event."""
        return len(self.markets)

    @property
    def category_count(self) -> int:
        """Get the number of categories in this event."""
        return len(self.categories)

    @property
    def tag_count(self) -> int:
        """Get the number of tags in this event."""
        return len(self.tags)


class SearchTag(BaseGammaModel):
    """Search tag model for tag search results."""

    id: str = Field(..., description="Search tag identifier")
    label: str = Field(..., description="Search tag label")
    slug: str = Field(..., description="URL-friendly slug")
    event_count: int = Field(
        ..., alias="event_count", description="Number of events with this tag"
    )

    @property
    def popularity(self) -> str:
        """Get popularity indicator based on event count."""
        if self.event_count >= 50:
            return "high"
        elif self.event_count >= 10:
            return "medium"
        else:
            return "low"


class Profile(BaseGammaModel):
    """User profile model for search results."""

    # Core fields
    id: Optional[str] = Field(None, description="Profile identifier")
    name: Optional[str] = Field(None, description="Profile display name")
    user: Optional[int] = Field(None, description="User ID")
    pseudonym: Optional[str] = Field(None, description="Profile pseudonym")
    profile_image: Optional[str] = Field(
        None, alias="profileImage", description="Profile image URL"
    )
    bio: Optional[str] = Field(None, description="Profile bio/description")

    @model_validator(mode="before")
    @classmethod
    def generate_id_if_missing(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an ID if missing from the response."""
        if not data.get("id"):
            # Generate ID from available fields
            if data.get("user"):
                data["id"] = f"user_{data['user']}"
            elif data.get("pseudonym"):
                data["id"] = f"pseudo_{data['pseudonym']}"
            elif data.get("name"):
                data["id"] = f"name_{data['name'].replace(' ', '_')}"
            else:
                data["id"] = f"profile_{hash(str(data)) % 1000000}"
        return data

    @property
    def display_name(self) -> str:
        """Get the best display name for the profile."""
        if self.name:
            return self.name
        elif self.pseudonym:
            return self.pseudonym
        elif self.user:
            return f"User {self.user}"
        else:
            return "Unknown"

    @property
    def has_image(self) -> bool:
        """Check if profile has an image."""
        return bool(self.profile_image and self.profile_image.strip())


class SearchPagination(BaseGammaModel):
    """Pagination metadata for search results."""

    has_more: bool = Field(..., alias="hasMore", description="Whether more pages exist")
    total_results: int = Field(
        ..., alias="totalResults", description="Total number of results"
    )

    @property
    def has_results(self) -> bool:
        """Check if there are any results."""
        return self.total_results > 0


class SearchResult(BaseGammaModel):
    """Main search result container."""

    events: List[SearchEvent] = Field(
        default_factory=list, description="Array of Event objects"
    )
    tags: List[SearchTag] = Field(
        default_factory=list, description="Array of SearchTag objects"
    )
    profiles: List[Profile] = Field(
        default_factory=list, description="Array of Profile objects"
    )
    pagination: SearchPagination = Field(..., description="Pagination metadata")

    @model_validator(mode="before")
    @classmethod
    def parse_api_response(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse API response data and handle nested object construction."""
        # Handle pagination object
        if "pagination" in data and isinstance(data["pagination"], dict):
            data["pagination"] = SearchPagination(**data["pagination"])

        # Handle arrays of objects
        if "events" in data and isinstance(data["events"], list):
            data["events"] = [
                SearchEvent(**event) if isinstance(event, dict) else event
                for event in data["events"]
            ]

        if "tags" in data and isinstance(data["tags"], list):
            data["tags"] = [
                SearchTag(**tag) if isinstance(tag, dict) else tag
                for tag in data["tags"]
            ]

        if "profiles" in data and isinstance(data["profiles"], list):
            data["profiles"] = [
                Profile(**profile) if isinstance(profile, dict) else profile
                for profile in data["profiles"]
            ]

        return data

    @property
    def total_count(self) -> int:
        """Get total count of all results across all types."""
        return len(self.events) + len(self.tags) + len(self.profiles)

    @property
    def has_events(self) -> bool:
        """Check if there are event results."""
        return len(self.events) > 0

    @property
    def has_tags(self) -> bool:
        """Check if there are tag results."""
        return len(self.tags) > 0

    @property
    def has_profiles(self) -> bool:
        """Check if there are profile results."""
        return len(self.profiles) > 0

    @property
    def has_more_results(self) -> bool:
        """Check if there are more results available."""
        return self.pagination.has_more

    def get_event_by_id(self, event_id: str) -> Optional[SearchEvent]:
        """Find an event by ID."""
        for event in self.events:
            if event.id == event_id:
                return event
        return None

    def get_tag_by_id(self, tag_id: str) -> Optional[SearchTag]:
        """Find a tag by ID."""
        for tag in self.tags:
            if tag.id == tag_id:
                return tag
        return None

    def get_profile_by_id(self, profile_id: str) -> Optional[Profile]:
        """Find a profile by ID."""
        for profile in self.profiles:
            if profile.id == profile_id:
                return profile
        return None

    def get_events_by_category(self, category_label: str) -> List[SearchEvent]:
        """Get events filtered by category."""
        filtered_events = []
        for event in self.events:
            for category in event.categories:
                if category.label == category_label:
                    filtered_events.append(event)
                    break
        return filtered_events

    def get_events_by_tag(self, tag_label: str) -> List[SearchEvent]:
        """Get events filtered by tag."""
        filtered_events = []
        for event in self.events:
            for tag in event.tags:
                if tag.label == tag_label:
                    filtered_events.append(event)
                    break
        return filtered_events

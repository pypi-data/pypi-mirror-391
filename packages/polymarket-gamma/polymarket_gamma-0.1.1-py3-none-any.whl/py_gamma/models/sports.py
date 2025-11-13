"""
Sports models for the Gamma API.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import json

from pydantic import Field, model_validator, field_validator

from .base import BaseGammaModel


class Sport(BaseGammaModel):
    """Sport model based on Gamma API documentation."""

    # Core fields from /sports endpoint
    sport: str = Field(..., description="The sport identifier or abbreviation")
    image: str = Field(..., description="URL to the sport's logo or image asset")
    resolution: str = Field(..., description="URL to the official resolution source")
    ordering: str = Field(
        ...,
        description="Preferred ordering for sport display, typically 'home' or 'away'",
    )
    tags: str = Field(..., description="Comma-separated list of tag IDs")
    series: str = Field(
        ..., description="Series identifier linking the sport to a specific tournament"
    )

    @property
    def tag_list(self) -> List[str]:
        """Get tags as a list of strings."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    def has_tag(self, tag_id: str) -> bool:
        """Check if sport has a specific tag."""
        return tag_id in self.tag_list


class League(BaseGammaModel):
    """League model for sports leagues."""

    # Core fields
    id: Optional[str] = Field(None, description="League identifier")
    name: Optional[str] = Field(None, description="League name")
    slug: Optional[str] = Field(None, description="URL-friendly slug")
    sport: Optional[str] = Field(None, description="Sport this league belongs to")

    # League metadata
    description: Optional[str] = Field(None, description="League description")
    logo: Optional[str] = Field(None, description="URL to league logo")
    website: Optional[str] = Field(None, description="League website URL")

    # Status and configuration
    active: Optional[bool] = Field(
        None, description="Whether league is currently active"
    )
    featured: Optional[bool] = Field(None, description="Whether league is featured")

    # Timestamps
    created_at: Optional[datetime] = Field(
        None, alias="createdAt", description="Creation date"
    )
    updated_at: Optional[datetime] = Field(
        None, alias="updatedAt", description="Last update date"
    )

    # Additional metadata
    country: Optional[str] = Field(None, description="Country where league operates")
    season: Optional[str] = Field(None, description="Current or default season")
    level: Optional[str] = Field(
        None, description="League level (professional, amateur, etc.)"
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
                # Fallback to simple parsing if dateutil is not available
                return None
        return None

    @model_validator(mode="before")
    @classmethod
    def parse_api_response(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse API response data and handle field conversions."""

        # Handle ID that might be numeric
        if "id" in data and data["id"] is not None:
            data["id"] = str(data["id"])

        # Handle tags that might be arrays instead of comma-separated strings
        if "tags" in data and isinstance(data["tags"], list):
            data["tags"] = ",".join(str(tag) for tag in data["tags"])

        return data

    @property
    def is_current_season(self) -> bool:
        """Check if league is in current season (placeholder logic)."""
        # This would need actual season determination logic based on sport
        return self.active if self.active is not None else False

    def matches_sport(self, sport_name: str) -> bool:
        """Check if league matches a specific sport."""
        if not self.sport:
            return False
        return self.sport.lower() == sport_name.lower() or self.sport.lower().endswith(
            sport_name.lower()
        )


class SportEvent(BaseGammaModel):
    """Event model for sports events within leagues."""

    # Core fields
    id: Optional[str] = Field(None, description="Event identifier")
    league_id: Optional[str] = Field(
        None, alias="leagueId", description="League identifier"
    )
    title: Optional[str] = Field(None, description="Event title")
    description: Optional[str] = Field(None, description="Event description")

    # Event timing
    start_time: Optional[datetime] = Field(
        None, alias="startTime", description="Event start time"
    )
    end_time: Optional[datetime] = Field(
        None, alias="endTime", description="Event end time"
    )

    # Event status
    status: Optional[str] = Field(
        None, description="Event status (scheduled, live, completed, cancelled)"
    )
    active: Optional[bool] = Field(
        None, description="Whether event is currently active"
    )

    # Event metadata
    venue: Optional[str] = Field(None, description="Event venue")
    location: Optional[str] = Field(None, description="Event location")

    # Participants (for team sports)
    participants: Optional[List[Dict[str, Any]]] = Field(
        None, description="Event participants"
    )

    # Timestamps
    created_at: Optional[datetime] = Field(
        None, alias="createdAt", description="Creation date"
    )
    updated_at: Optional[datetime] = Field(
        None, alias="updatedAt", description="Last update date"
    )

    @field_validator(
        "start_time", "end_time", "created_at", "updated_at", mode="before"
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

        # Handle ID that might be numeric
        if "id" in data and data["id"] is not None:
            data["id"] = str(data["id"])

        if "leagueId" in data and data["leagueId"] is not None:
            data["leagueId"] = str(data["leagueId"])

        # Handle participants that might be JSON strings
        if "participants" in data and isinstance(data["participants"], str):
            try:
                data["participants"] = json.loads(data["participants"])
            except (json.JSONDecodeError, TypeError):
                data["participants"] = []

        return data

    @property
    def is_live(self) -> bool:
        """Check if event is currently live."""
        if self.status:
            return self.status.lower() in ["live", "in_progress", "inprogress"]
        return False

    @property
    def is_completed(self) -> bool:
        """Check if event is completed."""
        if self.status:
            return self.status.lower() in ["completed", "finished", "final"]
        return False

    @property
    def is_upcoming(self) -> bool:
        """Check if event is upcoming."""
        if self.status:
            return self.status.lower() in ["scheduled", "upcoming", "pending"]
        return False

    @property
    def duration_minutes(self) -> Optional[int]:
        """Calculate event duration in minutes."""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            return int(duration.total_seconds() / 60)
        return None


class SportList(BaseGammaModel):
    """Container for a list of sports."""

    sports: List[Sport] = Field(default_factory=list, description="List of sports")
    total: Optional[int] = Field(None, description="Total number of sports")

    @property
    def count(self) -> int:
        """Get the number of sports in this list."""
        return len(self.sports)

    def get_sport_by_identifier(self, sport_identifier: str) -> Optional[Sport]:
        """Find a sport by its identifier."""
        for sport in self.sports:
            if sport.sport == sport_identifier:
                return sport
        return None


class LeagueList(BaseGammaModel):
    """Container for a list of leagues."""

    leagues: List[League] = Field(default_factory=list, description="List of leagues")
    total: Optional[int] = Field(None, description="Total number of leagues")
    limit: Optional[int] = Field(None, description="Page size limit")
    offset: Optional[int] = Field(None, description="Page offset")
    has_more: Optional[bool] = Field(
        None, alias="hasMore", description="Whether more leagues are available"
    )

    @property
    def count(self) -> int:
        """Get the number of leagues in this list."""
        return len(self.leagues)

    def get_league_by_id(self, league_id: str) -> Optional[League]:
        """Find a league by its ID."""
        for league in self.leagues:
            if league.id == league_id:
                return league
        return None

    def get_leagues_by_sport(self, sport_name: str) -> List[League]:
        """Get all leagues for a specific sport."""
        return [league for league in self.leagues if league.matches_sport(sport_name)]


class SportEventList(BaseGammaModel):
    """Container for a list of sport events."""

    events: List[SportEvent] = Field(
        default_factory=list, description="List of sport events"
    )
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

    def get_events_by_league(self, league_id: str) -> List[SportEvent]:
        """Get all events for a specific league."""
        return [event for event in self.events if event.league_id == league_id]

    def get_live_events(self) -> List[SportEvent]:
        """Get all currently live events."""
        return [event for event in self.events if event.is_live]

    def get_upcoming_events(self) -> List[SportEvent]:
        """Get all upcoming events."""
        return [event for event in self.events if event.is_upcoming]

    def get_completed_events(self) -> List[SportEvent]:
        """Get all completed events."""
        return [event for event in self.events if event.is_completed]

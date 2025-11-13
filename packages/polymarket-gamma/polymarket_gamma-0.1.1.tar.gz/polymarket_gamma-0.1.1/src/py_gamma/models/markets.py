"""
Market models for the Gamma API.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Union
import json

from pydantic import Field, model_validator, field_validator

from .base import BaseGammaModel
from .tags import Tag


class Category(BaseGammaModel):
    """Category model for market categorization."""

    id: Optional[str] = Field(None, description="Category identifier")
    slug: Optional[str] = Field(None, description="URL-friendly slug")
    name: Optional[str] = Field(None, description="Category name")
    description: Optional[str] = Field(None, description="Category description")


class OutcomePrice(BaseGammaModel):
    """Price information for market outcomes."""

    outcome: str = Field(..., description="Outcome name")
    price: Union[float, str] = Field(..., description="Current price")
    timestamp: Optional[datetime] = Field(None, description="Price timestamp")


class Market(BaseGammaModel):
    """Market model based on Gamma API documentation."""

    # Core fields
    id: str = Field(..., description="Market identifier")
    question: str = Field(..., description="The market question")
    description: str = Field(..., description="Market description")
    slug: str = Field(..., description="URL-friendly identifier")

    # Market status
    active: bool = Field(..., description="Whether market is currently active")
    closed: bool = Field(..., description="Whether market is closed")
    end_date: Optional[datetime] = Field(
        None, alias="endDate", description="When market ends"
    )

    # Contract information
    condition_id: Optional[str] = Field(
        None, alias="conditionId", description="Smart contract condition ID"
    )

    # Trading data
    volume: Optional[str] = Field(None, description="Trading volume")
    liquidity: Optional[str] = Field(None, description="Available liquidity")
    outcomes: List[str] = Field(default_factory=list, description="Possible outcomes")

    # Categorical data
    categories: List[Category] = Field(
        default_factory=list, description="Associated categories"
    )
    tags: List[Tag] = Field(default_factory=list, description="Associated tags")

    # Additional metadata (based on full API response)
    icon: Optional[str] = Field(None, description="Market icon URL")
    image: Optional[str] = Field(None, description="Market image URL")
    resolution_title: Optional[str] = Field(
        None, alias="resolutionTitle", description="Resolution title"
    )
    resolution_description: Optional[str] = Field(
        None, alias="resolutionDescription", description="Resolution description"
    )

    # Timestamps
    created_at: Optional[datetime] = Field(
        None, alias="createdAt", description="Creation date"
    )
    updated_at: Optional[datetime] = Field(
        None, alias="updatedAt", description="Last update date"
    )

    # Additional fields that may be present
    starts_at: Optional[datetime] = Field(
        None, alias="startsAt", description="When market starts"
    )
    answer_date: Optional[datetime] = Field(
        None, alias="answerDate", description="Answer date"
    )

    # Boolean flags
    resolve_soon: Optional[bool] = Field(
        None, alias="resolveSoon", description="Resolves soon"
    )
    resolved: Optional[bool] = Field(None, description="Whether market is resolved")
    neg_risk: Optional[bool] = Field(
        None, alias="negRisk", description="Negative risk market"
    )
    is_featured: Optional[bool] = Field(
        None, alias="isFeatured", description="Featured market"
    )
    is_sorting_priority: Optional[bool] = Field(
        None, alias="isSortingPriority", description="Sorting priority"
    )

    # Price data
    prices: Optional[List[OutcomePrice]] = Field(
        None, description="Current outcome prices"
    )

    # Additional metadata
    question_id: Optional[str] = Field(
        None, alias="questionId", description="Question identifier"
    )
    data_source_identifier: Optional[str] = Field(
        None, alias="dataSourceIdentifier", description="Data source"
    )

    @field_validator(
        "end_date",
        "created_at",
        "updated_at",
        "starts_at",
        "answer_date",
        mode="before",
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
                # Fallback to simple parsing if dateutil is not available
                return None
        return None

    @model_validator(mode="before")
    @classmethod
    def parse_api_response(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse API response data and handle field conversions."""
        # Handle outcomes that might be JSON strings instead of arrays
        if "outcomes" in data and isinstance(data["outcomes"], str):
            try:
                data["outcomes"] = json.loads(data["outcomes"])
            except (json.JSONDecodeError, TypeError):
                # If parsing fails, make it a single-item list
                data["outcomes"] = [data["outcomes"]]

        # Handle price fields that might be strings
        if "volume" in data and isinstance(data["volume"], str):
            try:
                data["volume"] = str(data["volume"])
            except (ValueError, TypeError):
                pass

        if "liquidity" in data and isinstance(data["liquidity"], str):
            try:
                data["liquidity"] = str(data["liquidity"])
            except (ValueError, TypeError):
                pass

        # Handle nested objects
        if "categories" in data and isinstance(data["categories"], list):
            data["categories"] = [
                Category(**cat) if isinstance(cat, dict) else cat
                for cat in data["categories"]
            ]

        if "tags" in data and isinstance(data["tags"], list):
            data["tags"] = [
                Tag(**tag) if isinstance(tag, dict) else tag for tag in data["tags"]
            ]

        return data

    @property
    def is_expired(self) -> bool:
        """Check if market has expired."""
        if self.end_date is None:
            return False
        return datetime.now(timezone.utc) > self.end_date

    @property
    def outcome_count(self) -> int:
        """Get the number of possible outcomes."""
        return len(self.outcomes)

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


class MarketList(BaseGammaModel):
    """Container for a list of markets."""

    markets: List[Market] = Field(default_factory=list, description="List of markets")
    total: Optional[int] = Field(None, description="Total number of markets")
    limit: Optional[int] = Field(None, description="Page size limit")
    offset: Optional[int] = Field(None, description="Page offset")
    has_more: Optional[bool] = Field(
        None, alias="hasMore", description="Whether more markets are available"
    )

    @property
    def count(self) -> int:
        """Get the number of markets in this list."""
        return len(self.markets)

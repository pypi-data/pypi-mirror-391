"""
Market models for the Gamma API.
"""

import json
from datetime import UTC, datetime
from typing import Any

from pydantic import Field, field_validator, model_validator

from .base import BaseGammaModel
from .tags import Tag


class Category(BaseGammaModel):
    """Category model for market categorization."""

    id: str | None = Field(None, description="Category identifier")
    slug: str | None = Field(None, description="URL-friendly slug")
    name: str | None = Field(None, description="Category name")
    description: str | None = Field(None, description="Category description")


class OutcomePrice(BaseGammaModel):
    """Price information for market outcomes."""

    outcome: str = Field(..., description="Outcome name")
    price: float | str = Field(..., description="Current price")
    timestamp: datetime | None = Field(None, description="Price timestamp")


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
    end_date: datetime | None = Field(
        None, alias="endDate", description="When market ends"
    )

    # Contract information
    condition_id: str | None = Field(
        None, alias="conditionId", description="Smart contract condition ID"
    )

    # Trading data
    volume: str | None = Field(None, description="Trading volume")
    liquidity: str | None = Field(None, description="Available liquidity")
    outcomes: list[str] = Field(default_factory=list, description="Possible outcomes")

    # Categorical data
    categories: list[Category] = Field(
        default_factory=list, description="Associated categories"
    )
    tags: list[Tag] = Field(default_factory=list, description="Associated tags")

    # Additional metadata (based on full API response)
    icon: str | None = Field(None, description="Market icon URL")
    image: str | None = Field(None, description="Market image URL")
    resolution_title: str | None = Field(
        None, alias="resolutionTitle", description="Resolution title"
    )
    resolution_description: str | None = Field(
        None, alias="resolutionDescription", description="Resolution description"
    )

    # Timestamps
    created_at: datetime | None = Field(
        None, alias="createdAt", description="Creation date"
    )
    updated_at: datetime | None = Field(
        None, alias="updatedAt", description="Last update date"
    )

    # Additional fields that may be present
    starts_at: datetime | None = Field(
        None, alias="startsAt", description="When market starts"
    )
    answer_date: datetime | None = Field(
        None, alias="answerDate", description="Answer date"
    )

    # Boolean flags
    resolve_soon: bool | None = Field(
        None, alias="resolveSoon", description="Resolves soon"
    )
    resolved: bool | None = Field(None, description="Whether market is resolved")
    neg_risk: bool | None = Field(
        None, alias="negRisk", description="Negative risk market"
    )
    is_featured: bool | None = Field(
        None, alias="isFeatured", description="Featured market"
    )
    is_sorting_priority: bool | None = Field(
        None, alias="isSortingPriority", description="Sorting priority"
    )

    # Price data
    prices: list[OutcomePrice] | None = Field(
        None, description="Current outcome prices"
    )

    # Additional metadata
    question_id: str | None = Field(
        None, alias="questionId", description="Question identifier"
    )
    data_source_identifier: str | None = Field(
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
                # Fallback to simple parsing if dateutil is not available
                return None
        return None

    @model_validator(mode="before")
    @classmethod
    def parse_api_response(cls, data: dict[str, Any]) -> dict[str, Any]:
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
        return datetime.now(UTC) > self.end_date

    @property
    def outcome_count(self) -> int:
        """Get the number of possible outcomes."""
        return len(self.outcomes)

    def get_tag_by_label(self, label: str) -> Tag | None:
        """Find a tag by its label."""
        for tag in self.tags:
            if tag.label == label:
                return tag
        return None

    def get_category_by_name(self, name: str) -> Category | None:
        """Find a category by name."""
        for category in self.categories:
            if category.name == name:
                return category
        return None


class MarketList(BaseGammaModel):
    """Container for a list of markets."""

    markets: list[Market] = Field(default_factory=list, description="List of markets")
    total: int | None = Field(None, description="Total number of markets")
    limit: int | None = Field(None, description="Page size limit")
    offset: int | None = Field(None, description="Page offset")
    has_more: bool | None = Field(
        None, alias="hasMore", description="Whether more markets are available"
    )

    @property
    def count(self) -> int:
        """Get the number of markets in this list."""
        return len(self.markets)

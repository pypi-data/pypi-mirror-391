"""
Base Pydantic models for Gamma API data structures.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseGammaModel(BaseModel):
    """Base model for all Gamma API responses."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return self.model_dump(exclude_none=True)

    def to_json(self) -> str:
        """Convert model to JSON string."""
        return self.model_dump_json(exclude_none=True)


class TimestampedModel(BaseGammaModel):
    """Base model with timestamp fields."""

    created_at: datetime | None = Field(
        None, description="When the object was created", alias="createdAt"
    )
    updated_at: datetime | None = Field(
        None, description="When the object was last updated", alias="updatedAt"
    )


class PaginatedResponse(BaseGammaModel):
    """Base model for paginated API responses."""

    data: list[Any] = Field(default_factory=list, description="Response data")
    total: int | None = Field(None, description="Total number of items")
    limit: int | None = Field(None, description="Page size limit")
    offset: int | None = Field(None, description="Page offset")
    has_more: bool | None = Field(
        None, description="Whether more items are available"
    )


class APIError(BaseGammaModel):
    """Model for API error responses."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    status_code: int | None = Field(
        None, description="HTTP status code", alias="statusCode"
    )
    details: dict[str, Any] | None = Field(
        None, description="Additional error details"
    )

"""
Tag models for the Gamma API.
"""

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from .base import BaseGammaModel


class Tag(BaseGammaModel):
    """Tag model based on Gamma API documentation."""

    id: str | None = Field(None, description="Tag identifier")
    label: str | None = Field(None, description="Human-readable label for the tag")
    slug: str | None = Field(None, description="URL-friendly slug for the tag")
    force_show: bool | None = Field(
        None, alias="forceShow", description="Whether to force show this tag"
    )
    force_hide: bool | None = Field(
        None, alias="forceHide", description="Whether to force hide this tag"
    )
    is_carousel: bool | None = Field(
        None, alias="isCarousel", description="Whether this tag is a carousel tag"
    )
    published_at: str | None = Field(
        None, alias="publishedAt", description="When the tag was published"
    )
    created_by: int | None = Field(
        None, alias="createdBy", description="ID of user who created the tag"
    )
    updated_by: int | None = Field(
        None, alias="updatedBy", description="ID of user who last updated the tag"
    )
    created_at: str | None = Field(
        None, alias="createdAt", description="When the tag was created"
    )
    updated_at: str | None = Field(
        None, alias="updatedAt", description="When the tag was last updated"
    )

    @field_validator("published_at", "created_at", "updated_at", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> str | None:
        """Parse datetime from string or return None.

        Note: API documentation shows timestamps as strings, so we keep them as strings
        to maintain compatibility with the API response format.
        """
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v)

    def to_datetime(self, field_name: str) -> datetime | None:
        """Convert string datetime field to datetime object.

        Args:
            field_name: Name of the field to convert ('created_at', 'updated_at', 'published_at')

        Returns:
            datetime object or None if field is None/invalid
        """
        value = getattr(self, field_name, None)
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None

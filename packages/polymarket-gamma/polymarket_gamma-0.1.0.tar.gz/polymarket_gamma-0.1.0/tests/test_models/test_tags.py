"""
Tests for Tag models.
"""

import pytest
from datetime import datetime

from py_gamma.models.tags import Tag


class TestTag:
    """Test Tag model."""

    def test_tag_creation(self) -> None:
        """Test creating a Tag with valid data."""
        data = {
            "id": "1",
            "label": "Bitcoin",
            "slug": "bitcoin",
            "forceShow": False,
            "forceHide": False,
            "isCarousel": False,
            "publishedAt": "2024-01-01T00:00:00Z",
            "createdBy": 123,
            "updatedBy": 456,
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-02T00:00:00Z"
        }
        tag = Tag(**data)

        assert tag.id == "1"
        assert tag.label == "Bitcoin"
        assert tag.slug == "bitcoin"
        assert tag.force_show is False
        assert tag.force_hide is False
        assert tag.is_carousel is False
        assert tag.published_at == "2024-01-01T00:00:00Z"
        assert tag.created_by == 123
        assert tag.updated_by == 456
        assert tag.created_at == "2024-01-01T00:00:00Z"
        assert tag.updated_at == "2024-01-02T00:00:00Z"

    def test_tag_optional_fields(self) -> None:
        """Test creating a Tag with optional fields."""
        tag = Tag(label="Test")

        assert tag.id is None
        assert tag.label == "Test"
        assert tag.slug is None
        assert tag.force_show is None
        assert tag.force_hide is None
        assert tag.is_carousel is None
        assert tag.published_at is None
        assert tag.created_by is None
        assert tag.updated_by is None
        assert tag.created_at is None
        assert tag.updated_at is None

    def test_tag_datetime_validation(self) -> None:
        """Test datetime field validation."""
        # Test with datetime object
        dt = datetime(2024, 1, 1, 12, 0, 0)
        tag = Tag(published_at=dt)
        assert tag.published_at == dt.isoformat()

        # Test with None
        tag = Tag(published_at=None)
        assert tag.published_at is None

        # Test with string
        tag = Tag(published_at="2024-01-01T00:00:00Z")
        assert tag.published_at == "2024-01-01T00:00:00Z"

        # Test with other types
        tag = Tag(published_at=123)
        assert tag.published_at == "123"

    def test_tag_to_datetime(self) -> None:
        """Test converting string datetime fields to datetime objects."""
        tag = Tag(
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-02T12:30:45Z",
            published_at="2024-01-01T15:30:00Z"
        )

        # Test valid conversion
        created_dt = tag.to_datetime("created_at")
        assert created_dt == datetime(2024, 1, 1, 0, 0, 0, tzinfo=datetime.now().astimezone().tzinfo)

        updated_dt = tag.to_datetime("updated_at")
        assert updated_dt == datetime(2024, 1, 2, 12, 30, 45, tzinfo=datetime.now().astimezone().tzinfo)

        published_dt = tag.to_datetime("published_at")
        assert published_dt == datetime(2024, 1, 1, 15, 30, 0, tzinfo=datetime.now().astimezone().tzinfo)

        # Test None field
        none_dt = tag.to_datetime("non_existent_field")
        assert none_dt is None

        # Test invalid datetime string
        tag_invalid = Tag(created_at="invalid-date")
        invalid_dt = tag_invalid.to_datetime("created_at")
        assert invalid_dt is None

    def test_tag_field_aliases(self) -> None:
        """Test that field aliases work correctly."""
        data = {
            "id": "2",
            "label": "Sports",
            "slug": "sports",
            "forceShow": True,
            "forceHide": False,
            "isCarousel": True,
            "publishedAt": "2024-01-01T00:00:00Z",
            "createdBy": 789,
            "updatedBy": 101,
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-02T00:00:00Z"
        }
        tag = Tag(**data)

        assert tag.force_show is True
        assert tag.force_hide is False
        assert tag.is_carousel is True
        assert tag.created_by == 789
        assert tag.updated_by == 101

    def test_tag_minimal_data(self) -> None:
        """Test creating a Tag with minimal required data."""
        tag = Tag()

        assert tag.id is None
        assert tag.label is None
        assert tag.slug is None
        assert tag.force_show is None
        assert tag.force_hide is None
        assert tag.is_carousel is None
        assert tag.published_at is None
        assert tag.created_by is None
        assert tag.updated_by is None
        assert tag.created_at is None
        assert tag.updated_at is None

    def test_tag_carousel_properties(self) -> None:
        """Test carousel-related properties."""
        # Carousel tag
        carousel_data = {
            "id": "3",
            "label": "Featured",
            "slug": "featured",
            "isCarousel": True
        }
        carousel_tag = Tag(**carousel_data)
        assert carousel_tag.is_carousel is True

        # Non-carousel tag
        non_carousel_data = {
            "id": "4",
            "label": "Regular",
            "slug": "regular",
            "isCarousel": False
        }
        regular_tag = Tag(**non_carousel_data)
        assert regular_tag.is_carousel is False

    def test_tag_force_show_hide_properties(self) -> None:
        """Test force show/hide properties."""
        force_show_data = {
            "id": "5",
            "label": "Always Show",
            "slug": "always-show",
            "forceShow": True,
            "forceHide": False
        }
        force_show_tag = Tag(**force_show_data)
        assert force_show_tag.force_show is True
        assert force_show_tag.force_hide is False

        force_hide_data = {
            "id": "6",
            "label": "Always Hide",
            "slug": "always-hide",
            "forceShow": False,
            "forceHide": True
        }
        force_hide_tag = Tag(**force_hide_data)
        assert force_hide_tag.force_show is False
        assert force_hide_tag.force_hide is True
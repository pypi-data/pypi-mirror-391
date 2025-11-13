"""
Tests for Market models.
"""

import pytest
from datetime import datetime

from py_gamma.models.markets import Market, Category, Tag, OutcomePrice


class TestCategory:
    """Test Category model."""

    def test_category_creation(self) -> None:
        """Test creating a Category with valid data."""
        data = {
            "id": "crypto",
            "slug": "cryptocurrency",
            "name": "Cryptocurrency",
            "description": "Markets related to cryptocurrencies"
        }
        category = Category(**data)

        assert category.id == "crypto"
        assert category.slug == "cryptocurrency"
        assert category.name == "Cryptocurrency"
        assert category.description == "Markets related to cryptocurrencies"

    def test_category_optional_fields(self) -> None:
        """Test creating a Category with optional fields."""
        category = Category(name="Test")

        assert category.id is None
        assert category.slug is None
        assert category.name == "Test"
        assert category.description is None


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
        assert tag.published_at == datetime(2024, 1, 1, 0, 0, 0)
        assert tag.created_by == 123
        assert tag.updated_by == 456


class TestMarket:
    """Test Market model."""

    def test_market_creation(self, mock_market_data) -> None:
        """Test creating a Market with valid data."""
        market = Market(**mock_market_data)

        assert market.id == "0x1234567890abcdef1234567890abcdef12345678"
        assert market.question == "Will Bitcoin reach $100,000 by end of 2024?"
        assert market.description == "This market resolves to Yes if Bitcoin reaches $100,000 USD or higher at any point before December 31, 2024, 23:59:59 UTC."
        assert market.slug == "bitcoin-100k-2024"
        assert market.active is True
        assert market.closed is False
        assert market.condition_id == "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        assert market.outcomes == ["Yes", "No"]
        assert market.volume == "1000000.00"
        assert market.liquidity == "50000.00"

    def test_market_timestamps(self, mock_market_data) -> None:
        """Test market timestamp parsing."""
        market = Market(**mock_market_data)

        assert market.end_date == datetime(2024, 12, 31, 23, 59, 59)
        assert market.created_at == datetime(2024, 1, 1, 0, 0, 0)
        assert market.updated_at == datetime(2024, 1, 15, 12, 30, 0)

    def test_market_nested_objects(self, mock_market_data) -> None:
        """Test nested Category and Tag objects."""
        market = Market(**mock_market_data)

        # Check categories
        assert len(market.categories) == 1
        category = market.categories[0]
        assert isinstance(category, Category)
        assert category.id == "crypto"
        assert category.name == "Cryptocurrency"

        # Check tags
        assert len(market.tags) == 1
        tag = market.tags[0]
        assert isinstance(tag, Tag)
        assert tag.id == "1"
        assert tag.label == "Bitcoin"

    def test_market_is_expired(self) -> None:
        """Test market expiration check."""
        # Expired market
        expired_data = {
            "id": "expired",
            "question": "Expired market",
            "slug": "expired",
            "active": False,
            "closed": True,
            "endDate": "2020-01-01T00:00:00Z",
            "outcomes": ["Yes", "No"]
        }
        expired_market = Market(**expired_data)
        assert expired_market.is_expired is True

        # Active market
        active_data = {
            "id": "active",
            "question": "Active market",
            "slug": "active",
            "active": True,
            "closed": False,
            "endDate": "2030-01-01T00:00:00Z",
            "outcomes": ["Yes", "No"]
        }
        active_market = Market(**active_data)
        assert active_market.is_expired is False

    def test_market_outcome_count(self) -> None:
        """Test outcome count property."""
        binary_data = {
            "id": "binary",
            "question": "Binary market",
            "slug": "binary",
            "active": True,
            "closed": False,
            "outcomes": ["Yes", "No"]
        }
        binary_market = Market(**binary_data)
        assert binary_market.outcome_count == 2

        multi_data = {
            "id": "multi",
            "question": "Multiple choice market",
            "slug": "multi",
            "active": True,
            "closed": False,
            "outcomes": ["Option A", "Option B", "Option C", "Option D"]
        }
        multi_market = Market(**multi_data)
        assert multi_market.outcome_count == 4

    def test_market_get_tag_by_label(self, mock_market_data) -> None:
        """Test finding tags by label."""
        market = Market(**mock_market_data)

        # Existing tag
        bitcoin_tag = market.get_tag_by_label("Bitcoin")
        assert bitcoin_tag is not None
        assert bitcoin_tag.label == "Bitcoin"

        # Non-existing tag
        non_existing = market.get_tag_by_label("Ethereum")
        assert non_existing is None

    def test_market_get_category_by_name(self, mock_market_data) -> None:
        """Test finding categories by name."""
        market = Market(**mock_market_data)

        # Existing category
        crypto_category = market.get_category_by_name("Cryptocurrency")
        assert crypto_category is not None
        assert crypto_category.name == "Cryptocurrency"

        # Non-existing category
        non_existing = market.get_category_by_name("Sports")
        assert non_existing is None

    def test_market_to_dict(self, mock_market_data) -> None:
        """Test converting market to dictionary."""
        market = Market(**mock_market_data)
        market_dict = market.to_dict()

        assert market_dict["id"] == market.id
        assert market_dict["question"] == market.question
        assert market_dict["slug"] == market.slug
        assert "categories" in market_dict
        assert "tags" in market_dict

    def test_market_to_json(self, mock_market_data) -> None:
        """Test converting market to JSON."""
        market = Market(**mock_market_data)
        market_json = market.to_json()

        assert isinstance(market_json, str)
        assert market.id in market_json
        assert market.question in market_json
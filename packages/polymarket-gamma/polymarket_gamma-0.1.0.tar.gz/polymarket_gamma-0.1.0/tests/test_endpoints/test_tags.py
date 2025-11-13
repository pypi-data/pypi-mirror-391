"""
Tests for Tags API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

import httpx

from py_gamma.client import GammaClient, AsyncHTTPClient
from py_gamma.endpoints.tags import TagsEndpoint
from py_gamma.models.tags import Tag
from py_gamma.exceptions import TagNotFoundError, GammaAPIError


@pytest.fixture
def mock_http_client() -> AsyncMock:
    """Mock AsyncHTTPClient."""
    mock_client = AsyncMock(spec=AsyncHTTPClient)
    mock_client.config.debug = False
    return mock_client


@pytest.fixture
def tags_endpoint(mock_http_client: AsyncMock) -> TagsEndpoint:
    """Create TagsEndpoint with mocked HTTP client."""
    return TagsEndpoint(mock_http_client)


@pytest.fixture
def sample_tag_response() -> dict:
    """Sample tag API response."""
    return {
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


@pytest.fixture
def sample_tags_list_response() -> list:
    """Sample tags list API response."""
    return [
        {
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
        },
        {
            "id": "2",
            "label": "Ethereum",
            "slug": "ethereum",
            "forceShow": True,
            "forceHide": False,
            "isCarousel": True,
            "publishedAt": "2024-01-01T00:00:00Z",
            "createdBy": 789,
            "updatedBy": 101,
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-02T00:00:00Z"
        }
    ]


class TestTagsEndpoint:
    """Test TagsEndpoint."""

    async def test_get_tag_by_id_success(
        self, tags_endpoint: TagsEndpoint, mock_http_client: AsyncMock, sample_tag_response: dict
    ) -> None:
        """Test successful get_tag_by_id."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = sample_tag_response
        mock_http_client.request.return_value = mock_response

        # Call the method
        result = await tags_endpoint.get_tag_by_id("1")

        # Verify result
        assert isinstance(result, Tag)
        assert result.id == "1"
        assert result.label == "Bitcoin"
        assert result.slug == "bitcoin"

        # Verify HTTP client was called correctly
        mock_http_client.request.assert_called_once_with(
            "GET",
            "/tags/1",
            params={}
        )

    async def test_get_tag_by_id_with_include_template(
        self, tags_endpoint: TagsEndpoint, mock_http_client: AsyncMock, sample_tag_response: dict
    ) -> None:
        """Test get_tag_by_id with include_template parameter."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = sample_tag_response
        mock_http_client.request.return_value = mock_response

        # Call the method
        result = await tags_endpoint.get_tag_by_id("1", include_template=True)

        # Verify result
        assert isinstance(result, Tag)
        assert result.id == "1"

        # Verify HTTP client was called with correct params
        mock_http_client.request.assert_called_once_with(
            "GET",
            "/tags/1",
            params={"include_template": True}
        )

    async def test_get_tag_by_id_not_found(
        self, tags_endpoint: TagsEndpoint, mock_http_client: AsyncMock
    ) -> None:
        """Test get_tag_by_id when tag is not found."""
        # Setup mock response to raise 404 error
        mock_http_client.request.side_effect = httpx.HTTPStatusError(
            "Not Found", request=Mock(), response=Mock(status_code=404)
        )

        # Call the method and expect exception
        with pytest.raises(TagNotFoundError) as exc_info:
            await tags_endpoint.get_tag_by_id("nonexistent")

        assert exc_info.value.tag_id == "nonexistent"

    async def test_get_tag_by_id_api_error(
        self, tags_endpoint: TagsEndpoint, mock_http_client: AsyncMock
    ) -> None:
        """Test get_tag_by_id with API error."""
        # Setup mock response to raise 500 error
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.return_value = {"error": "Server error"}
        mock_http_client.request.side_effect = httpx.HTTPStatusError(
            "Internal Server Error", request=Mock(), response=mock_response
        )

        # Call the method and expect exception
        with pytest.raises(GammaAPIError) as exc_info:
            await tags_endpoint.get_tag_by_id("1")

        assert exc_info.value.status_code == 500
        assert "Failed to get tag 1" in str(exc_info.value)

    async def test_get_tags_success(
        self, tags_endpoint: TagsEndpoint, mock_http_client: AsyncMock, sample_tags_list_response: list
    ) -> None:
        """Test successful get_tags."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = sample_tags_list_response
        mock_http_client.request.return_value = mock_response

        # Call the method
        result = await tags_endpoint.get_tags()

        # Verify result
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(tag, Tag) for tag in result)
        assert result[0].id == "1"
        assert result[0].label == "Bitcoin"
        assert result[1].id == "2"
        assert result[1].label == "Ethereum"

        # Verify HTTP client was called correctly
        mock_http_client.request.assert_called_once_with(
            "GET",
            "/tags",
            params={"limit": 100, "offset": 0}
        )

    async def test_get_tags_with_filters(
        self, tags_endpoint: TagsEndpoint, mock_http_client: AsyncMock, sample_tags_list_response: list
    ) -> None:
        """Test get_tags with filter parameters."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = sample_tags_list_response
        mock_http_client.request.return_value = mock_response

        # Call the method with filters
        result = await tags_endpoint.get_tags(
            limit=50,
            offset=10,
            order="label",
            ascending=True,
            include_template=True,
            is_carousel=True
        )

        # Verify result
        assert isinstance(result, list)
        assert len(result) == 2

        # Verify HTTP client was called with correct params
        mock_http_client.request.assert_called_once_with(
            "GET",
            "/tags",
            params={
                "limit": 50,
                "offset": 10,
                "order": "label",
                "ascending": True,
                "include_template": True,
                "is_carousel": True
            }
        )

    async def test_get_tags_page_size_validation(
        self, tags_endpoint: TagsEndpoint, mock_http_client: AsyncMock, sample_tags_list_response: list
    ) -> None:
        """Test get_tags page size validation."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = sample_tags_list_response
        mock_http_client.request.return_value = mock_response

        # Test limit > max_size
        await tags_endpoint.get_tags(limit=2000)
        mock_http_client.request.assert_called_with(
            "GET",
            "/tags",
            params={"limit": 1000, "offset": 0}
        )

        # Test limit <= 0
        await tags_endpoint.get_tags(limit=0)
        mock_http_client.request.assert_called_with(
            "GET",
            "/tags",
            params={"limit": 100, "offset": 0}
        )

    async def test_search_tags(
        self, tags_endpoint: TagsEndpoint, mock_http_client: AsyncMock, sample_tags_list_response: list
    ) -> None:
        """Test search_tags functionality."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = sample_tags_list_response
        mock_http_client.request.return_value = mock_response

        # Call search method
        result = await tags_endpoint.search_tags("Bitcoin")

        # Verify result - should return matching tags
        assert isinstance(result, list)
        assert len(result) == 1  # Only Bitcoin should match
        assert result[0].label == "Bitcoin"

    async def test_search_tags_case_insensitive(
        self, tags_endpoint: TagsEndpoint, mock_http_client: AsyncMock, sample_tags_list_response: list
    ) -> None:
        """Test search_tags with case insensitive search."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = sample_tags_list_response
        mock_http_client.request.return_value = mock_response

        # Call search method with lowercase
        result = await tags_endpoint.search_tags("bitcoin")

        # Verify result - should find Bitcoin tag
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].label == "Bitcoin"

    async def test_get_carousel_tags(
        self, tags_endpoint: TagsEndpoint, mock_http_client: AsyncMock, sample_tags_list_response: list
    ) -> None:
        """Test get_carousel_tags functionality."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = sample_tags_list_response
        mock_http_client.request.return_value = mock_response

        # Call get_carousel_tags
        result = await tags_endpoint.get_carousel_tags()

        # Verify result
        assert isinstance(result, list)
        # Should filter by is_carousel=True in the API call
        mock_http_client.request.assert_called_once_with(
            "GET",
            "/tags",
            params={"limit": 100, "offset": 0, "is_carousel": True}
        )

    async def test_iter_all_tags(
        self, tags_endpoint: TagsEndpoint, mock_http_client: AsyncMock, sample_tags_list_response: list
    ) -> None:
        """Test iter_all_tags pagination."""
        # Setup mock response for first page
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = sample_tags_list_response
        mock_http_client.request.return_value = mock_response

        # Create async iterator
        tags_iter = tags_endpoint.iter_all_tags(page_size=2)

        # Collect all tags
        tags = []
        async for tag in tags_iter:
            tags.append(tag)

        # Verify results
        assert len(tags) == 2
        assert all(isinstance(tag, Tag) for tag in tags)

    async def test_sync_methods(self, tags_endpoint: TagsEndpoint) -> None:
        """Test synchronous convenience methods exist."""
        # These should exist but raise NotImplementedError when called without proper async setup
        assert hasattr(tags_endpoint, 'get_sync')
        assert hasattr(tags_endpoint, 'list_sync')

    def test_sync_wrapper_execution(self, tags_endpoint: TagsEndpoint, sample_tag_response: dict) -> None:
        """Test that sync methods work correctly."""
        with patch('asyncio.run') as mock_run:
            mock_run.return_value = Tag(**sample_tag_response)

            result = tags_endpoint.get_sync("1")
            assert isinstance(result, Tag)
            assert result.id == "1"

    @pytest.mark.asyncio
    async def test_debug_output(
        self, tags_endpoint: TagsEndpoint, mock_http_client: AsyncMock, sample_tag_response: dict
    ) -> None:
        """Test debug output when enabled."""
        # Enable debug mode
        mock_http_client.config.debug = True

        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = sample_tag_response
        mock_http_client.request.return_value = mock_response

        # Call the method and capture print output
        with patch('builtins.print') as mock_print:
            result = await tags_endpoint.get_tag_by_id("1")

        # Verify result and debug output
        assert isinstance(result, Tag)
        mock_print.assert_called_with("Successfully fetched tag: Bitcoin")
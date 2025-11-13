"""
Integration tests for Tags endpoint with GammaClient.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

import httpx

from py_gamma import GammaClient, Tag, TagNotFoundError
from py_gamma.config import GammaConfig


@pytest.mark.asyncio
class TestTagsIntegration:
    """Test Tags endpoint integration with GammaClient."""

    async def test_gamma_client_has_tags_endpoint(self) -> None:
        """Test that GammaClient has tags endpoint."""
        client = GammaClient()
        assert hasattr(client, 'tags')
        assert client.tags is not None

    async def test_gamma_client_tags_endpoint_type(self) -> None:
        """Test that tags endpoint is of correct type."""
        client = GammaClient()
        from py_gamma.endpoints.tags import TagsEndpoint
        assert isinstance(client.tags, TagsEndpoint)

    @patch('py_gamma.client.AsyncHTTPClient.request')
    async def test_get_tag_by_id_integration(self, mock_request: Mock) -> None:
        """Test get_tag_by_id through GammaClient."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = {
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
        mock_request.return_value = mock_response

        # Use client
        async with GammaClient() as client:
            tag = await client.tags.get_tag_by_id("1")

        # Verify result
        assert isinstance(tag, Tag)
        assert tag.id == "1"
        assert tag.label == "Bitcoin"

    @patch('py_gamma.client.AsyncHTTPClient.request')
    async def test_get_tags_integration(self, mock_request: Mock) -> None:
        """Test get_tags through GammaClient."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = [
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
        mock_request.return_value = mock_response

        # Use client
        async with GammaClient() as client:
            tags = await client.tags.get_tags()

        # Verify result
        assert isinstance(tags, list)
        assert len(tags) == 2
        assert all(isinstance(tag, Tag) for tag in tags)
        assert tags[0].label == "Bitcoin"
        assert tags[1].label == "Ethereum"

    @patch('py_gamma.client.AsyncHTTPClient.request')
    async def test_sync_wrapper_tags_integration(self, mock_request: Mock) -> None:
        """Test sync wrapper for tags endpoint."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = {
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
        mock_request.return_value = mock_response

        # Use client with sync wrapper
        client = GammaClient()
        tag = client.sync.tags.get_sync("1")

        # Verify result
        assert isinstance(tag, Tag)
        assert tag.id == "1"
        assert tag.label == "Bitcoin"

    @patch('py_gamma.client.AsyncHTTPClient.request')
    async def test_search_tags_integration(self, mock_request: Mock) -> None:
        """Test search_tags through GammaClient."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = [
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
            }
        ]
        mock_request.return_value = mock_response

        # Use client
        async with GammaClient() as client:
            tags = await client.tags.search_tags("Bitcoin")

        # Verify result
        assert isinstance(tags, list)
        assert len(tags) == 1
        assert tags[0].label == "Bitcoin"

    @patch('py_gamma.client.AsyncHTTPClient.request')
    async def test_get_carousel_tags_integration(self, mock_request: Mock) -> None:
        """Test get_carousel_tags through GammaClient."""
        # Setup mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = [
            {
                "id": "2",
                "label": "Featured",
                "slug": "featured",
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
        mock_request.return_value = mock_response

        # Use client
        async with GammaClient() as client:
            tags = await client.tags.get_carousel_tags()

        # Verify result
        assert isinstance(tags, list)
        assert len(tags) == 1
        assert tags[0].is_carousel is True

    @patch('py_gamma.client.AsyncHTTPClient.request')
    async def test_tag_error_handling_integration(self, mock_request: Mock) -> None:
        """Test tag error handling through GammaClient."""
        # Setup mock to raise 404 error
        mock_request.side_effect = httpx.HTTPStatusError(
            "Not Found", request=Mock(), response=Mock(status_code=404)
        )

        # Use client
        async with GammaClient() as client:
            with pytest.raises(TagNotFoundError) as exc_info:
                await client.tags.get_tag_by_id("nonexistent")

            assert exc_info.value.tag_id == "nonexistent"

    async def test_client_configuration_tags_endpoint(self) -> None:
        """Test that client configuration is passed to tags endpoint."""
        config = GammaConfig(debug=True, api_key="test-key")
        client = GammaClient(config)

        # Check that the tags endpoint has access to the config
        assert client.tags.client.config.debug is True
        assert client.tags.client.config.api_key == "test-key"
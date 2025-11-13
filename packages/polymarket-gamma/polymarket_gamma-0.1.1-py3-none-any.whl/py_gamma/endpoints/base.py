"""
Base endpoint class for all Gamma API endpoints.
"""

import logging
from typing import Any, Dict, Optional, AsyncIterator, TypeVar, Generic, Type

import httpx

from ..client import AsyncHTTPClient
from ..exceptions import GammaAPIError

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseEndpoint(Generic[T]):
    """Base class for all API endpoints."""

    def __init__(self, client: AsyncHTTPClient) -> None:
        self.client = client

    async def _make_request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
        cache_ttl: Optional[int] = None,
    ) -> httpx.Response:
        """Make HTTP request and handle common errors."""
        try:
            response = await self.client.request(
                method,
                path,
                params=params,
                json_data=json_data,
                use_cache=use_cache,
                cache_ttl=cache_ttl,
            )
            return response

        except httpx.HTTPStatusError as e:
            # Handle specific HTTP errors that subclasses may want to customize
            if e.response.status_code == 404:
                raise GammaAPIError(
                    f"Resource not found: {path}",
                    status_code=404,
                    response_data=e.response.json() if e.response.content else None,
                )
            elif e.response.status_code == 400:
                raise GammaAPIError(
                    f"Bad request: {e.response.text}",
                    status_code=400,
                    response_data=e.response.json() if e.response.content else None,
                )
            else:
                raise GammaAPIError(
                    f"HTTP error {e.response.status_code}: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=e.response.json() if e.response.content else None,
                )

    async def _get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
        cache_ttl: Optional[int] = None,
    ) -> httpx.Response:
        """Make GET request."""
        return await self._make_request(
            "GET", path, params=params, use_cache=use_cache, cache_ttl=cache_ttl
        )

    async def _post(
        self,
        path: str,
        *,
        json_data: Optional[Dict[str, Any]] = None,
        use_cache: bool = False,
        cache_ttl: Optional[int] = None,
    ) -> httpx.Response:
        """Make POST request."""
        return await self._make_request(
            "POST", path, json_data=json_data, use_cache=use_cache, cache_ttl=cache_ttl
        )

    async def _parse_response(
        self,
        response: httpx.Response,
        model_class: Type[T],
    ) -> T:
        """Parse HTTP response into Pydantic model."""
        try:
            # Use the safe JSON parsing method
            data = await self._safe_json_parse(response)
            return model_class.model_validate(data)  # type: ignore[attr-defined]
        except Exception as e:
            # Re-raise GammaAPIError as-is
            if isinstance(e, GammaAPIError):
                raise
            # Handle other unexpected errors
            content_preview = response.text[:200] if hasattr(response, 'text') and response.text else "No content"
            raise GammaAPIError(
                f"Failed to parse response: {e}. "
                f"Response content: {content_preview}"
            )

    async def _parse_response_list(
        self,
        response: httpx.Response,
        model_class: Type[T],
    ) -> list[T]:
        """Parse HTTP response into list of Pydantic models."""
        try:
            # Use the safe JSON parsing method
            data = await self._safe_json_parse(response)
            if isinstance(data, list):
                return [model_class.model_validate(item) for item in data]  # type: ignore[attr-defined]
            elif isinstance(data, dict) and "data" in data:
                return [model_class.model_validate(item) for item in data["data"]]  # type: ignore[attr-defined]
            else:
                raise GammaAPIError(f"Unexpected response format: {type(data)}")
        except Exception as e:
            # Re-raise GammaAPIError as-is
            if isinstance(e, GammaAPIError):
                raise
            # Handle other unexpected errors
            raise GammaAPIError(f"Failed to parse response list: {e}")

    def _build_params(
        self,
        exclude_none: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Build query parameters dict, excluding None values by default."""
        if exclude_none:
            return {k: v for k, v in kwargs.items() if v is not None}
        return kwargs

    async def _paginate(
        self,
        endpoint_path: str,
        model_class: Type[T],
        *,
        limit: int = 100,
        offset: int = 0,
        max_pages: Optional[int] = None,
        **params: Any,
    ) -> AsyncIterator[T]:
        """Generic pagination helper."""
        page = 0
        current_offset = offset

        while max_pages is None or page < max_pages:
            # Make request
            response = await self._get(
                endpoint_path,
                params=self._build_params(limit=limit, offset=current_offset, **params),
            )

            # Parse response
            items = await self._parse_response_list(response, model_class)

            # Yield items
            for item in items:
                yield item

            # Check if we got fewer items than requested (last page)
            if len(items) < limit:
                break

            # Prepare for next page
            current_offset += limit
            page += 1

    def _normalize_id(self, id_value: object) -> str:
        """Normalize ID value to string."""
        return str(id_value)

    async def _safe_json_parse(self, response: httpx.Response) -> Any:
        """Safely parse JSON response with proper error handling."""
        # Check if response content type is JSON
        content_type = response.headers.get("content-type", "").lower()
        if "application/json" not in content_type:
            # Log the actual content for debugging
            content_preview = response.text[:200] if response.text else "Empty response"
            raise GammaAPIError(
                f"Expected JSON response but got {content_type}. "
                f"Content preview: {content_preview}"
            )

        try:
            return response.json()
        except Exception as e:
            # Handle specific JSON parsing errors
            import json

            if hasattr(response, 'text') and response.text:
                response_text = response.text
                content_preview = response_text[:200]

                # Check for "Extra data" error specifically
                if "Extra data" in str(e):
                    # Try to handle common issues with JSON responses
                    clean_text = response_text.strip()

                    # Remove BOM (Byte Order Mark) if present
                    if clean_text.startswith('\ufeff'):
                        clean_text = clean_text[1:]

                    # Try parsing the cleaned text
                    try:
                        return json.loads(clean_text)
                    except json.JSONDecodeError:
                        # If still fails, provide detailed error
                        raise GammaAPIError(
                            f"JSON parsing error with extra data: {e}. "
                            f"Response starts with: {repr(response_text[:50])}..."
                        )

                # Other JSON errors
                raise GammaAPIError(
                    f"Failed to parse JSON response: {e}. "
                    f"Response content: {content_preview}"
                )
            else:
                raise GammaAPIError(f"Failed to parse JSON response: {e}")

    def _validate_page_size(self, page_size: int, max_size: int = 1000) -> int:
        """Validate and adjust page size."""
        if page_size <= 0:
            return 100
        elif page_size > max_size:
            return max_size
        return page_size

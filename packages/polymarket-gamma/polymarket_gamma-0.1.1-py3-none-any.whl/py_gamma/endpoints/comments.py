"""
Comments API endpoints for the Gamma SDK.
"""

from typing import Optional, AsyncIterator, List, Any, Union

import httpx

from .base import BaseEndpoint
from ..models.comments import Comment
from ..exceptions import CommentNotFoundError, GammaAPIError


class CommentsEndpoint(BaseEndpoint[Comment]):
    """Comments API endpoints."""

    async def get_comment_by_id(
        self,
        comment_id: Union[str, int],
        get_positions: bool = False,
    ) -> Comment:
        """Get comment by ID.

        Based on API documentation:
        GET /comments/{id}

        Args:
            comment_id: Comment identifier (string or integer)
            get_positions: Include user positions in the response

        Returns:
            Comment object

        Raises:
            CommentNotFoundError: If comment not found
            GammaAPIError: For other API errors
        """
        # Normalize comment ID to string for the path
        comment_id_str = self._normalize_id(comment_id)

        # Build query parameters
        params = {"get_positions": get_positions} if get_positions else {}

        try:
            response = await self._get(f"/comments/{comment_id_str}", params=params)
            # API returns an array even when querying by ID
            comments = await self._parse_response_list(response, Comment)

            if not comments:
                raise CommentNotFoundError(comment_id_str)

            comment = comments[0]

            if self.client.config.debug:
                print(f"Successfully fetched comment: {comment.id[:8]}...")

            return comment

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise CommentNotFoundError(comment_id_str)
            else:
                raise GammaAPIError(
                    f"Failed to get comment {comment_id_str}: {e.response.text}",
                    status_code=e.response.status_code,
                    response_data=e.response.json() if e.response.content else None,
                )

    async def get_comments(
        self,
        limit: int = 100,
        offset: int = 0,
        order: Optional[str] = None,
        ascending: Optional[bool] = None,
        parent_entity_type: Optional[str] = None,
        parent_entity_id: Optional[Union[str, int]] = None,
        get_positions: bool = False,
        holders_only: bool = False,
        **kwargs: Any,
    ) -> List[Comment]:
        """List comments.

        Based on API documentation:
        GET /comments

        Args:
            limit: Number of comments to return (max 1000)
            offset: Number of comments to skip
            order: Fields to sort by (comma-separated)
            ascending: Sort direction (true = ascending, false = descending)
            parent_entity_type: Type of parent entity ("Event", "Series", "market")
            parent_entity_id: ID of the parent entity
            get_positions: Include user positions in the response
            holders_only: Filter to only include comments from token holders
            **kwargs: Additional query parameters

        Returns:
            List of Comment objects

        Raises:
            GammaAPIError: For API errors
        """
        # Validate page size
        limit = self._validate_page_size(limit, max_size=1000)

        # Validate parent_entity_type
        if parent_entity_type is not None:
            valid_types = ["Event", "Series", "market"]
            if parent_entity_type not in valid_types:
                raise GammaAPIError(
                    f"Invalid parent_entity_type '{parent_entity_type}'. "
                    f"Valid types are: {', '.join(valid_types)}"
                )

        # Build query parameters
        params = self._build_params(
            limit=limit,
            offset=offset,
            order=order,
            ascending=ascending,
            parent_entity_type=parent_entity_type,
            parent_entity_id=parent_entity_id,
            get_positions=get_positions,
            holders_only=holders_only,
            **kwargs,
        )

        try:
            response = await self._get("/comments", params=params)
            comments = await self._parse_response_list(response, Comment)

            if self.client.config.debug:
                print(f"Successfully fetched {len(comments)} comments")

            return comments

        except httpx.HTTPStatusError as e:
            raise GammaAPIError(
                f"Failed to get comments: {e.response.text}",
                status_code=e.response.status_code,
                response_data=e.response.json() if e.response.content else None,
            )

    async def get_comments_by_user_address(
        self,
        user_address: str,
        limit: int = 100,
        offset: int = 0,
        get_positions: bool = False,
        **kwargs: Any,
    ) -> List[Comment]:
        """Get comments by user address.

        Based on API documentation:
        GET /comments (filtered by userAddress)

        Args:
            user_address: User's wallet address
            limit: Number of comments to return (max 1000)
            offset: Number of comments to skip
            get_positions: Include user positions in the response
            **kwargs: Additional query parameters

        Returns:
            List of Comment objects

        Raises:
            GammaAPIError: For API errors
        """
        # Validate address format (basic check)
        if not user_address.startswith(("0x", "0X")) or len(user_address) != 42:
            raise GammaAPIError(f"Invalid user address format: {user_address}")

        # Validate page size
        limit = self._validate_page_size(limit, max_size=1000)

        # Build query parameters
        params = self._build_params(
            userAddress=user_address,
            limit=limit,
            offset=offset,
            get_positions=get_positions,
            **kwargs,
        )

        try:
            response = await self._get("/comments", params=params)
            comments = await self._parse_response_list(response, Comment)

            if self.client.config.debug:
                print(
                    f"Successfully fetched {len(comments)} comments for user {user_address[:10]}..."
                )

            return comments

        except httpx.HTTPStatusError as e:
            raise GammaAPIError(
                f"Failed to get comments for user {user_address}: {e.response.text}",
                status_code=e.response.status_code,
                response_data=e.response.json() if e.response.content else None,
            )

    async def get_market_comments(
        self,
        market_id: Union[str, int],
        limit: int = 100,
        offset: int = 0,
        get_positions: bool = False,
        **kwargs: Any,
    ) -> List[Comment]:
        """Get comments for a specific market.

        Convenience method for getting market comments.

        Args:
            market_id: Market identifier
            limit: Number of comments to return (max 1000)
            offset: Number of comments to skip
            get_positions: Include user positions in the response
            **kwargs: Additional query parameters

        Returns:
            List of Comment objects

        Raises:
            GammaAPIError: For API errors
        """
        return await self.get_comments(
            limit=limit,
            offset=offset,
            parent_entity_type="market",
            parent_entity_id=market_id,
            get_positions=get_positions,
            **kwargs,
        )

    async def get_event_comments(
        self,
        event_id: Union[str, int],
        limit: int = 100,
        offset: int = 0,
        get_positions: bool = False,
        **kwargs: Any,
    ) -> List[Comment]:
        """Get comments for a specific event.

        Convenience method for getting event comments.

        Args:
            event_id: Event identifier
            limit: Number of comments to return (max 1000)
            offset: Number of comments to skip
            get_positions: Include user positions in the response
            **kwargs: Additional query parameters

        Returns:
            List of Comment objects

        Raises:
            GammaAPIError: For API errors
        """
        return await self.get_comments(
            limit=limit,
            offset=offset,
            parent_entity_type="Event",
            parent_entity_id=event_id,
            get_positions=get_positions,
            **kwargs,
        )

    async def get_series_comments(
        self,
        series_id: Union[str, int],
        limit: int = 100,
        offset: int = 0,
        get_positions: bool = False,
        **kwargs: Any,
    ) -> List[Comment]:
        """Get comments for a specific series.

        Convenience method for getting series comments.

        Args:
            series_id: Series identifier
            limit: Number of comments to return (max 1000)
            offset: Number of comments to skip
            get_positions: Include user positions in the response
            **kwargs: Additional query parameters

        Returns:
            List of Comment objects

        Raises:
            GammaAPIError: For API errors
        """
        return await self.get_comments(
            limit=limit,
            offset=offset,
            parent_entity_type="Series",
            parent_entity_id=series_id,
            get_positions=get_positions,
            **kwargs,
        )

    async def iter_all_comments(
        self,
        page_size: int = 100,
        **filters: Any,
    ) -> AsyncIterator[Comment]:
        """Iterate through all comments using pagination.

        Args:
            page_size: Number of comments per page
            **filters: Filter parameters from get_comments()

        Yields:
            Comment objects

        Raises:
            GammaAPIError: For API errors
        """
        page_size = self._validate_page_size(page_size, max_size=1000)

        if self.client.config.debug:
            print(f"Starting pagination through comments with page_size={page_size}")

        async for comment in self._paginate(
            "/comments",
            Comment,
            limit=page_size,
            **filters,
        ):
            yield comment

    async def search_comments(
        self,
        query: str,
        limit: int = 50,
        **filters: Any,
    ) -> List[Comment]:
        """Search comments by query string.

        Note: The API doesn't have a dedicated search endpoint for comments,
        so this will filter comments by body content after fetching them.

        Args:
            query: Search query
            limit: Maximum number of results
            **filters: Additional filter parameters

        Returns:
            List of matching Comment objects

        Raises:
            GammaAPIError: For API errors
        """
        all_comments = await self.get_comments(
            limit=limit * 2,  # Fetch more to allow for filtering
            **filters,
        )

        # Filter comments that contain the query in the body
        matching_comments = [
            comment
            for comment in all_comments
            if comment.body and query.lower() in comment.body.lower()
        ]

        # Limit results
        return matching_comments[:limit]

    async def get_comment_replies(
        self,
        parent_comment_id: Union[str, int],
        limit: int = 100,
        offset: int = 0,
        **kwargs: Any,
    ) -> List[Comment]:
        """Get replies to a specific comment.

        Args:
            parent_comment_id: Parent comment ID
            limit: Number of comments to return (max 1000)
            offset: Number of comments to skip
            **kwargs: Additional query parameters

        Returns:
            List of reply Comment objects

        Raises:
            GammaAPIError: For API errors
        """
        # First verify the parent comment exists
        try:
            await self.get_comment_by_id(parent_comment_id)
        except CommentNotFoundError:
            raise CommentNotFoundError(f"Parent comment {parent_comment_id} not found")

        # Get comments filtered by parent comment ID
        # Note: The API doesn't directly support filtering by parent_comment_id,
        # so we'll need to fetch more comments and filter client-side
        comments = await self.get_comments(
            limit=limit * 5,  # Fetch more to allow for filtering
            offset=offset,
            **kwargs,
        )

        # Filter for replies to the specified comment
        replies = [
            comment
            for comment in comments
            if comment.parent_comment_id == str(parent_comment_id)
        ]

        # Limit results
        return replies[:limit]

    def get_sync(
        self, comment_id: Union[str, int], get_positions: bool = False
    ) -> Comment:
        """Synchronous version of get_comment_by_id for convenience."""
        import asyncio

        return asyncio.run(self.get_comment_by_id(comment_id, get_positions))

    def get_comments_sync(
        self,
        limit: int = 100,
        offset: int = 0,
        **kwargs: Any,
    ) -> List[Comment]:
        """Synchronous version of get_comments for convenience."""
        import asyncio

        return asyncio.run(self.get_comments(limit=limit, offset=offset, **kwargs))

"""
Comment models for the Gamma API.
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import Field, field_validator, model_validator

from .base import BaseGammaModel


class CommentProfile(BaseGammaModel):
    """Profile information for comment authors."""

    name: str | None = Field(None, description="User's display name")
    pseudonym: str | None = Field(None, description="User's username")
    display_username_public: bool | None = Field(
        None,
        alias="displayUsernamePublic",
        description="Whether username is displayed publicly",
    )
    profile_image_url: str | None = Field(
        None, alias="profileImageUrl", description="Profile image URL"
    )
    cover_image_url: str | None = Field(
        None, alias="coverImageUrl", description="Cover image URL"
    )
    bio: str | None = Field(None, description="User biography")
    website: str | None = Field(None, description="User website")
    twitter_handle: str | None = Field(
        None, alias="twitterHandle", description="Twitter handle"
    )
    discord_handle: str | None = Field(
        None, alias="discordHandle", description="Discord handle"
    )
    telegram_handle: str | None = Field(
        None, alias="telegramHandle", description="Telegram handle"
    )

    # Position and portfolio data (when get_positions=true)
    positions: list[dict[str, Any]] | None = Field(
        default_factory=list, description="User's positions"
    )
    volume: str | None = Field(None, description="User's trading volume")
    winnings: str | None = Field(None, description="User's winnings")
    win_rate: float | None = Field(
        None, alias="winRate", description="User's win rate"
    )
    bio_flair: str | None = Field(
        None, alias="bioFlair", description="Bio flair text"
    )
    bio_flair_color: str | None = Field(
        None, alias="bioFlairColor", description="Bio flair color"
    )
    custom_image_url: str | None = Field(
        None, alias="customImageUrl", description="Custom image URL"
    )


class Reaction(BaseGammaModel):
    """Reaction information for comments."""

    id: str | None = Field(None, description="Reaction identifier")
    reaction: str | None = Field(None, description="Reaction type/emoji")
    count: int | None = Field(None, description="Number of this reaction type")
    icon: str | None = Field(None, description="Reaction icon URL")
    color: str | None = Field(None, description="Reaction color")

    # User information for reactions (when applicable)
    user: dict[str, Any] | None = Field(
        None, description="User who made this reaction"
    )
    user_address: str | None = Field(
        None, alias="userAddress", description="Reacting user's wallet address"
    )
    created_at: datetime | None = Field(
        None, alias="createdAt", description="Reaction timestamp"
    )

    @field_validator("created_at", mode="before")
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
                return None
        return None


class Comment(BaseGammaModel):
    """Comment model based on Gamma API documentation."""

    # Core fields
    id: str = Field(..., description="Comment identifier")
    body: str | None = Field(None, description="Comment content/text")

    # Parent entity information
    parent_entity_type: str | None = Field(
        None,
        alias="parentEntityType",
        description="Entity type commented on (Event/Series/market)",
    )
    parent_entity_id: int | None = Field(
        None, alias="parentEntityID", description="Entity ID the comment belongs to"
    )
    parent_comment_id: str | None = Field(
        None,
        alias="parentCommentID",
        description="Parent comment ID for threaded replies",
    )

    # User information
    user_address: str | None = Field(
        None, alias="userAddress", description="Author's wallet address"
    )
    reply_address: str | None = Field(
        None, alias="replyAddress", description="Reply target address"
    )

    # Timestamps
    created_at: datetime | None = Field(
        None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: datetime | None = Field(
        None, alias="updatedAt", description="Last update timestamp"
    )

    # Interaction data
    profile: CommentProfile | None = Field(
        None, description="User profile information"
    )
    reactions: list[Reaction] | None = Field(
        default_factory=list, description="List of reactions to the comment"
    )
    report_count: int | None = Field(
        None,
        alias="reportCount",
        description="Number of reports the comment has received",
    )
    reaction_count: int | None = Field(
        None,
        alias="reactionCount",
        description="Total number of reactions to the comment",
    )

    @field_validator("created_at", "updated_at", mode="before")
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
                return None
        return None

    @model_validator(mode="before")
    @classmethod
    def parse_api_response(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Parse API response data and handle field conversions."""

        # Handle nested objects
        if "profile" in data and isinstance(data["profile"], dict):
            data["profile"] = CommentProfile(**data["profile"])

        if "reactions" in data and isinstance(data["reactions"], list):
            data["reactions"] = [
                Reaction(**reaction) if isinstance(reaction, dict) else reaction
                for reaction in data["reactions"]
            ]

        # Ensure reaction_count is properly calculated if not provided
        if (
            "reactionCount" not in data
            and "reactions" in data
            and isinstance(data["reactions"], list)
        ):
            # Sum up reaction counts if available
            total_count = 0
            for reaction in data["reactions"]:
                if isinstance(reaction, dict) and "count" in reaction:
                    total_count += int(reaction.get("count", 0))
                elif isinstance(reaction, Reaction) and reaction.count:
                    total_count += reaction.count
            data["reactionCount"] = total_count

        # Ensure report_count has a default
        if "reportCount" not in data:
            data["reportCount"] = 0

        return data

    @property
    def is_reply(self) -> bool:
        """Check if this comment is a reply to another comment."""
        return self.parent_comment_id is not None

    @property
    def is_edited(self) -> bool:
        """Check if this comment has been edited."""
        if self.created_at is None or self.updated_at is None:
            return False
        return self.created_at != self.updated_at

    @property
    def reaction_summary(self) -> dict[str, int]:
        """Get a summary of reactions by type."""
        summary: dict[str, int] = {}
        if self.reactions:
            for reaction in self.reactions:
                if reaction.reaction:
                    reaction_type = reaction.reaction
                    count = reaction.count or 1
                    summary[reaction_type] = summary.get(reaction_type, 0) + count
        return summary

    def get_reaction_by_type(self, reaction_type: str) -> Reaction | None:
        """Find a reaction by its type."""
        if not self.reactions:
            return None
        for reaction in self.reactions:
            if reaction.reaction == reaction_type:
                return reaction
        return None

    def get_top_reactions(self, limit: int = 3) -> list[Reaction]:
        """Get the top reactions by count."""
        if not self.reactions:
            return []

        # Sort reactions by count (descending)
        sorted_reactions = sorted(
            [r for r in self.reactions if r.count is not None],
            key=lambda x: x.count or 0,
            reverse=True,
        )

        return sorted_reactions[:limit]


class CommentList(BaseGammaModel):
    """Container for a list of comments."""

    comments: list[Comment] = Field(
        default_factory=list, description="List of comments"
    )
    total: int | None = Field(None, description="Total number of comments")
    limit: int | None = Field(None, description="Page size limit")
    offset: int | None = Field(None, description="Page offset")
    has_more: bool | None = Field(
        None, alias="hasMore", description="Whether more comments are available"
    )

    @property
    def count(self) -> int:
        """Get the number of comments in this list."""
        return len(self.comments)

    def get_replies(self, comment_id: str) -> list[Comment]:
        """Get all replies to a specific comment."""
        return [
            comment
            for comment in self.comments
            if comment.parent_comment_id == comment_id
        ]

    def get_top_level_comments(self) -> list[Comment]:
        """Get only top-level comments (not replies)."""
        return [
            comment for comment in self.comments if comment.parent_comment_id is None
        ]

    def sort_by_reactions(self, descending: bool = True) -> "CommentList":
        """Return a new CommentList sorted by reaction count."""
        sorted_comments = sorted(
            self.comments, key=lambda c: c.reaction_count or 0, reverse=descending
        )

        return CommentList(
            comments=sorted_comments,
            total=self.total,
            limit=self.limit,
            offset=self.offset,
            hasMore=self.has_more,
        )

    def sort_by_date(self, descending: bool = True) -> "CommentList":
        """Return a new CommentList sorted by creation date."""
        sorted_comments = sorted(
            self.comments,
            key=lambda c: c.created_at or datetime.min.replace(tzinfo=UTC),
            reverse=descending,
        )

        return CommentList(
            comments=sorted_comments,
            total=self.total,
            limit=self.limit,
            offset=self.offset,
            hasMore=self.has_more,
        )

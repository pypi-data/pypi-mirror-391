"""
User models for the Gamma API.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Union
from decimal import Decimal
from enum import Enum

from pydantic import Field, model_validator, field_validator

from .base import BaseGammaModel


class ProfileVisibility(str, Enum):
    """Profile visibility enumeration."""

    PUBLIC = "public"
    FRIENDS = "friends"
    PRIVATE = "private"


class UserSettings(BaseGammaModel):
    """User settings model."""

    email_notifications: bool = Field(
        default=True, description="Email notifications enabled"
    )
    push_notifications: bool = Field(
        default=True, description="Push notifications enabled"
    )
    profile_visibility: ProfileVisibility = Field(
        default=ProfileVisibility.PUBLIC, description="Profile visibility setting"
    )
    show_activity: bool = Field(default=True, description="Show user activity publicly")
    allow_messages: bool = Field(
        default=True, description="Allow messages from other users"
    )


class PrivacySettings(BaseGammaModel):
    """Privacy settings for user profile."""

    profile_visibility: ProfileVisibility = Field(
        default=ProfileVisibility.PUBLIC, description="Profile visibility"
    )
    show_activity: bool = Field(default=True, description="Show activity status")
    allow_messages: bool = Field(
        default=True, description="Allow messages from other users"
    )


class Position(BaseGammaModel):
    """User position model representing holdings in a market."""

    id: Optional[str] = Field(None, description="Position identifier")
    market_id: str = Field(..., alias="marketId", description="Market ID")
    market_question: Optional[str] = Field(
        None, alias="marketQuestion", description="Market question"
    )
    outcome: str = Field(..., description="Outcome name")
    outcome_price: Optional[Union[float, str, Decimal]] = Field(
        None, alias="outcomePrice", description="Price when position was opened"
    )
    shares: Optional[Union[float, str, Decimal]] = Field(
        ..., description="Number of shares held"
    )
    value: Optional[Union[float, str, Decimal]] = Field(
        None, description="Current position value"
    )
    cost_basis: Optional[Union[float, str, Decimal]] = Field(
        None, alias="costBasis", description="Total cost of position"
    )
    profit_loss: Optional[Union[float, str, Decimal]] = Field(
        None, alias="profitLoss", description="Realized/unrealized profit/loss"
    )
    realized: Optional[bool] = Field(
        None, description="Whether position has been realized"
    )
    market_closed: Optional[bool] = Field(
        None, alias="marketClosed", description="If the market is closed"
    )
    created_at: Optional[datetime] = Field(
        None, alias="createdAt", description="Position creation date"
    )
    updated_at: Optional[datetime] = Field(
        None, alias="updatedAt", description="Last update date"
    )

    @field_validator(
        "outcome_price", "shares", "value", "cost_basis", "profit_loss", mode="before"
    )
    @classmethod
    def parse_decimal_fields(cls, v: Any) -> Optional[Decimal]:
        """Parse decimal fields from various formats."""
        if v is None:
            return None
        if isinstance(v, Decimal):
            return v
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            try:
                return Decimal(v)
            except (ValueError, TypeError):
                return None
        return None

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Optional[datetime]:
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

    @property
    def is_profitable(self) -> bool:
        """Check if position is profitable."""
        if self.profit_loss is None:
            return False
        return float(self.profit_loss) > 0

    @property
    def is_long(self) -> bool:
        """Check if this is a long position (positive shares)."""
        if self.shares is None:
            return False
        return float(self.shares) > 0


class UserStats(BaseGammaModel):
    """User statistics and performance metrics."""

    total_positions: Optional[int] = Field(
        None, alias="totalPositions", description="Total number of positions"
    )
    active_positions: Optional[int] = Field(
        None, alias="activePositions", description="Number of active positions"
    )
    closed_positions: Optional[int] = Field(
        None, alias="closedPositions", description="Number of closed positions"
    )
    total_volume: Optional[Union[float, str, Decimal]] = Field(
        None, alias="totalVolume", description="Total trading volume"
    )
    total_profit_loss: Optional[Union[float, str, Decimal]] = Field(
        None, alias="totalProfitLoss", description="Total profit/loss"
    )
    win_rate: Optional[float] = Field(
        None, alias="winRate", description="Win rate percentage"
    )
    average_return: Optional[float] = Field(
        None, alias="averageReturn", description="Average return percentage"
    )
    total_winnings: Optional[Union[float, str, Decimal]] = Field(
        None, alias="totalWinnings", description="Total winnings from successful bets"
    )
    total_losses: Optional[Union[float, str, Decimal]] = Field(
        None, alias="totalLosses", description="Total losses from unsuccessful bets"
    )
    net_profit: Optional[Union[float, str, Decimal]] = Field(
        None, alias="netProfit", description="Net profit after all positions"
    )
    roi: Optional[float] = Field(None, description="Return on investment percentage")
    sharpe_ratio: Optional[float] = Field(
        None, alias="sharpeRatio", description="Sharpe ratio"
    )
    max_drawdown: Optional[float] = Field(
        None, alias="maxDrawdown", description="Maximum drawdown percentage"
    )
    markets_created: Optional[int] = Field(
        None, alias="marketsCreated", description="Number of markets created"
    )
    prediction_accuracy: Optional[float] = Field(
        None, alias="predictionAccuracy", description="Prediction accuracy percentage"
    )
    last_active: Optional[datetime] = Field(
        None, alias="lastActive", description="Last activity timestamp"
    )
    member_since: Optional[datetime] = Field(
        None, alias="memberSince", description="Account creation date"
    )

    @field_validator(
        "total_volume",
        "total_profit_loss",
        "total_winnings",
        "total_losses",
        "net_profit",
        mode="before",
    )
    @classmethod
    def parse_decimal_fields(cls, v: Any) -> Optional[Decimal]:
        """Parse decimal fields from various formats."""
        if v is None:
            return None
        if isinstance(v, Decimal):
            return v
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            try:
                return Decimal(v)
            except (ValueError, TypeError):
                return None
        return None

    @field_validator("last_active", "member_since", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Optional[datetime]:
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

    @property
    def is_profitable_trader(self) -> bool:
        """Check if user is profitable overall."""
        if self.net_profit is None:
            return False
        return float(self.net_profit) > 0

    @property
    def experience_level(self) -> str:
        """Determine experience level based on activity."""
        if self.total_positions is None:
            return "Unknown"
        if self.total_positions < 10:
            return "Beginner"
        elif self.total_positions < 50:
            return "Intermediate"
        elif self.total_positions < 200:
            return "Advanced"
        else:
            return "Expert"


class UserHistory(BaseGammaModel):
    """User historical activity and transactions."""

    id: Optional[str] = Field(None, description="History entry ID")
    transaction_type: Optional[str] = Field(
        None, alias="transactionType", description="Type of transaction"
    )
    market_id: Optional[str] = Field(None, alias="marketId", description="Market ID")
    market_question: Optional[str] = Field(
        None, alias="marketQuestion", description="Market question"
    )
    outcome: Optional[str] = Field(None, description="Outcome traded")
    amount: Optional[Union[float, str, Decimal]] = Field(
        None, description="Transaction amount"
    )
    price: Optional[Union[float, str, Decimal]] = Field(
        None, description="Price per share"
    )
    shares: Optional[Union[float, str, Decimal]] = Field(
        None, description="Number of shares"
    )
    fee: Optional[Union[float, str, Decimal]] = Field(
        None, description="Transaction fee"
    )
    timestamp: Optional[datetime] = Field(None, description="Transaction timestamp")
    created_at: Optional[datetime] = Field(
        None, alias="createdAt", description="Entry creation date"
    )

    @field_validator("amount", "price", "shares", "fee", mode="before")
    @classmethod
    def parse_decimal_fields(cls, v: Any) -> Optional[Decimal]:
        """Parse decimal fields from various formats."""
        if v is None:
            return None
        if isinstance(v, Decimal):
            return v
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            try:
                return Decimal(v)
            except (ValueError, TypeError):
                return None
        return None

    @field_validator("timestamp", "created_at", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Optional[datetime]:
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


class Profile(BaseGammaModel):
    """User profile model based on Gamma API documentation."""

    # Core user fields
    id: str = Field(..., description="User identifier")
    username: str = Field(..., description="Username")
    display_name: Optional[str] = Field(
        None, alias="displayName", description="Display name"
    )
    email: Optional[str] = Field(None, description="Email address")
    avatar: Optional[str] = Field(None, description="Avatar URL")
    bio: Optional[str] = Field(None, description="User biography")

    # Profile information
    location: Optional[str] = Field(None, description="User location")
    website: Optional[str] = Field(None, description="Personal website")
    twitter_handle: Optional[str] = Field(
        None, alias="twitterHandle", description="Twitter username"
    )
    discord_username: Optional[str] = Field(
        None, alias="discordUsername", description="Discord username"
    )

    # Account information
    verified: Optional[bool] = Field(None, description="Account verification status")
    follower_count: Optional[int] = Field(
        None, alias="followerCount", description="Number of followers"
    )
    following_count: Optional[int] = Field(
        None, alias="followingCount", description="Number of following"
    )
    reputation_score: Optional[float] = Field(
        None, alias="reputationScore", description="Reputation score"
    )

    # Settings
    settings: Optional[UserSettings] = Field(None, description="User settings")

    # Timestamps
    created_at: Optional[datetime] = Field(
        None, alias="createdAt", description="Account creation date"
    )
    updated_at: Optional[datetime] = Field(
        None, alias="updatedAt", description="Last profile update"
    )
    last_login: Optional[datetime] = Field(
        None, alias="lastLogin", description="Last login timestamp"
    )

    # Privacy and visibility
    profile_visibility: Optional[ProfileVisibility] = Field(
        None, alias="profileVisibility", description="Profile visibility setting"
    )
    show_activity: Optional[bool] = Field(
        None, alias="showActivity", description="Show activity publicly"
    )
    allow_messages: Optional[bool] = Field(
        None, alias="allowMessages", description="Allow messages"
    )

    # Additional metadata
    is_active: Optional[bool] = Field(
        None, alias="isActive", description="Account active status"
    )
    is_premium: Optional[bool] = Field(
        None, alias="isPremium", description="Premium membership status"
    )
    badges: Optional[List[str]] = Field(None, description="User badges/achievements")

    @field_validator("created_at", "updated_at", "last_login", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Optional[datetime]:
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

    @field_validator("settings", mode="before")
    @classmethod
    def parse_settings(cls, v: Any) -> Optional[UserSettings]:
        """Parse settings from dict or create default."""
        if v is None:
            return UserSettings()
        if isinstance(v, dict):
            return UserSettings(**v)
        if isinstance(v, UserSettings):
            return v
        return None

    @model_validator(mode="before")
    @classmethod
    def parse_api_response(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse API response data and handle field conversions."""
        # Handle nested settings object
        if "settings" in data and isinstance(data["settings"], dict):
            # Ensure proper enum conversion for profile visibility
            if "profileVisibility" in data["settings"]:
                visibility = data["settings"]["profileVisibility"]
                if isinstance(visibility, str):
                    # Convert to lowercase for enum compatibility
                    data["settings"]["profileVisibility"] = visibility.lower()

        # Handle profile visibility at root level if present
        if "profileVisibility" in data:
            visibility = data["profileVisibility"]
            if isinstance(visibility, str):
                data["profileVisibility"] = visibility.lower()

        return data

    @property
    def account_age(self) -> Optional[int]:
        """Get account age in days."""
        if self.created_at is None:
            return None
        now = datetime.now(timezone.utc)
        delta = now - self.created_at
        return delta.days

    @property
    def is_new_user(self) -> bool:
        """Check if user is new (less than 30 days)."""
        age = self.account_age
        return age is not None and age < 30

    @property
    def display_name_fallback(self) -> str:
        """Get display name with fallback to username."""
        return self.display_name if self.display_name else self.username


class User(BaseGammaModel):
    """Complete user model with profile and additional data."""

    profile: Profile = Field(..., description="User profile information")
    stats: Optional[UserStats] = Field(None, description="User statistics")
    positions: Optional[List[Position]] = Field(None, description="User positions")
    history: Optional[List[UserHistory]] = Field(
        None, description="User transaction history"
    )

    @model_validator(mode="before")
    @classmethod
    def parse_user_response(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse user API response and separate into components."""
        # If the data already has a profile field, use it as-is
        if "profile" in data:
            return data

        # Otherwise, treat the entire data as the profile
        return {"profile": data, "stats": None, "positions": None, "history": None}

    @property
    def id(self) -> str:
        """Get user ID from profile."""
        return self.profile.id

    @property
    def username(self) -> str:
        """Get username from profile."""
        return self.profile.username


class UserList(BaseGammaModel):
    """Container for a list of user profiles."""

    users: List[Profile] = Field(
        default_factory=list, description="List of user profiles"
    )
    total: Optional[int] = Field(None, description="Total number of users")
    limit: Optional[int] = Field(None, description="Page size limit")
    offset: Optional[int] = Field(None, description="Page offset")
    has_more: Optional[bool] = Field(
        None, alias="hasMore", description="Whether more users are available"
    )

    @property
    def count(self) -> int:
        """Get the number of users in this list."""
        return len(self.users)


class PositionList(BaseGammaModel):
    """Container for a list of user positions."""

    positions: List[Position] = Field(
        default_factory=list, description="List of positions"
    )
    total: Optional[int] = Field(None, description="Total number of positions")
    limit: Optional[int] = Field(None, description="Page size limit")
    offset: Optional[int] = Field(None, description="Page offset")
    has_more: Optional[bool] = Field(
        None, alias="hasMore", description="Whether more positions are available"
    )

    @property
    def count(self) -> int:
        """Get the number of positions in this list."""
        return len(self.positions)

    @property
    def total_value(self) -> Optional[Decimal]:
        """Calculate total value of all positions."""
        if not self.positions:
            return Decimal("0")

        total = Decimal("0")
        for position in self.positions:
            if position.value is not None:
                # Ensure position.value is a Decimal before adding
                if isinstance(position.value, Decimal):
                    total += position.value
                else:
                    # Convert to Decimal if it's a different type
                    total += Decimal(str(position.value))
        return total

    @property
    def profitable_positions(self) -> List[Position]:
        """Get list of profitable positions."""
        return [pos for pos in self.positions if pos.is_profitable]

    @property
    def losing_positions(self) -> List[Position]:
        """Get list of losing positions."""
        return [pos for pos in self.positions if not pos.is_profitable]


class UserHistoryList(BaseGammaModel):
    """Container for a list of user history entries."""

    history: List[UserHistory] = Field(
        default_factory=list, description="List of history entries"
    )
    total: Optional[int] = Field(None, description="Total number of entries")
    limit: Optional[int] = Field(None, description="Page size limit")
    offset: Optional[int] = Field(None, description="Page offset")
    has_more: Optional[bool] = Field(
        None, alias="hasMore", description="Whether more entries are available"
    )

    @property
    def count(self) -> int:
        """Get the number of history entries in this list."""
        return len(self.history)

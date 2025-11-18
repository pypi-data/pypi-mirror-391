"""
Configuration management for the Py-Gamma SDK.
"""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator


class GammaConfig(BaseModel):
    """Configuration for the Gamma API client."""

    # API Configuration
    base_url: str = Field(
        default="https://gamma-api.polymarket.com",
        description="Base URL for the Gamma API",
    )
    api_key: str | None = Field(
        default=None, description="API key for authentication (if required)"
    )

    # Timeout Configuration
    request_timeout: float = Field(
        default=30.0, description="Request timeout in seconds"
    )
    connect_timeout: float = Field(
        default=10.0, description="Connection timeout in seconds"
    )

    # Retry Configuration
    max_retries: int = Field(
        default=3, description="Maximum number of retries for failed requests"
    )
    retry_delay: float = Field(
        default=1.0, description="Initial delay between retries in seconds"
    )
    retry_backoff_factor: float = Field(
        default=2.0, description="Backoff factor for retry delays"
    )

    # Cache Configuration
    enable_cache: bool = Field(default=True, description="Enable caching")
    cache_ttl: int = Field(
        default=300,  # 5 minutes
        description="Cache time-to-live in seconds",
    )
    cache_dir: Path = Field(
        default=Path(".gamma_cache"), description="Directory for disk cache"
    )
    memory_cache_size: int = Field(
        default=1000, description="Maximum number of items in memory cache"
    )

    # Pagination Configuration
    default_page_size: int = Field(
        default=100, description="Default page size for paginated requests"
    )
    max_page_size: int = Field(default=1000, description="Maximum allowed page size")

    # Debug Configuration
    debug: bool = Field(default=False, description="Enable debug logging")
    trace_requests: bool = Field(
        default=False, description="Enable HTTP request/response tracing"
    )

    class Config:
        """Pydantic configuration."""

        env_prefix = "GAMMA_"
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def from_env(cls, env_file: str | None = None) -> "GammaConfig":
        """Load configuration from environment variables."""
        # Load environment variables from .env file if it exists
        if env_file:
            _ = load_dotenv(env_file)
        else:
            # Try to load from common locations
            for env_path in [".env", "~/.gamma.env"]:
                if os.path.exists(os.path.expanduser(env_path)):
                    _ = load_dotenv(os.path.expanduser(env_path))
                    break

        return cls()

    @field_validator("cache_dir", mode="before")
    @classmethod
    def expand_cache_dir(cls, v: Any) -> Path:
        """Expand user home directory in cache path."""
        if isinstance(v, str):
            return Path(v).expanduser()
        return v

    @field_validator("base_url")
    @classmethod
    def normalize_base_url(cls, v: str) -> str:
        """Normalize base URL by removing trailing slash."""
        return v.rstrip("/")

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump(exclude_none=True)

    def __str__(self) -> str:  # noqa: A003
        """String representation of configuration."""
        return (
            f"GammaConfig(base_url={self.base_url}, "
            f"timeout={self.request_timeout}s, "
            f"retries={self.max_retries}, "
            f"cache={'enabled' if self.enable_cache else 'disabled'})"
        )

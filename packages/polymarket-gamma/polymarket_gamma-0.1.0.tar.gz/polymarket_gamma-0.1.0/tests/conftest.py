"""
pytest configuration and fixtures for the Py-Gamma SDK.
"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator

from py_gamma import GammaClient, GammaConfig


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def gamma_client() -> AsyncGenerator[GammaClient, None]:
    """Create a GammaClient instance for testing."""
    config = GammaConfig(
        debug=True,
        enable_cache=False,  # Disable cache for tests to ensure fresh data
        max_retries=1,  # Reduce retries for faster tests
        request_timeout=10.0,  # Shorter timeout for tests
    )

    client = GammaClient(config=config)
    yield client
    await client.close()


@pytest.fixture
def gamma_config() -> GammaConfig:
    """Create a GammaConfig instance for testing."""
    return GammaConfig(
        debug=True,
        enable_cache=False,
        max_retries=1,
        request_timeout=10.0,
    )


@pytest.fixture
def mock_market_data() -> dict:
    """Mock market data for testing."""
    return {
        "id": "0x1234567890abcdef1234567890abcdef12345678",
        "question": "Will Bitcoin reach $100,000 by end of 2024?",
        "description": "This market resolves to Yes if Bitcoin reaches $100,000 USD or higher at any point before December 31, 2024, 23:59:59 UTC.",
        "slug": "bitcoin-100k-2024",
        "active": True,
        "closed": False,
        "endDate": "2024-12-31T23:59:59Z",
        "conditionId": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "outcomes": ["Yes", "No"],
        "volume": "1000000.00",
        "liquidity": "50000.00",
        "categories": [
            {
                "id": "crypto",
                "slug": "cryptocurrency",
                "name": "Cryptocurrency",
                "description": "Markets related to cryptocurrencies"
            }
        ],
        "tags": [
            {
                "id": "1",
                "label": "Bitcoin",
                "slug": "bitcoin",
                "forceShow": False,
                "forceHide": False,
                "isCarousel": False
            }
        ],
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-15T12:30:00Z"
    }
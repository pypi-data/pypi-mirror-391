# Polymarket Gamma

Modern Python SDK for the Polymarket Gamma API.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-beta-orange.svg)
![PyPI](https://img.shields.io/badge/pypi-polymarket--gamma-blue.svg)

**Note**: Install as `polymarket-gamma`, but import as `py_gamma`.

## Features

- **Async-first design** with sync convenience wrappers
- **Strict type safety** with Pydantic v2 validation
- **Hybrid caching** (memory + disk) with TTL support
- **Comprehensive error handling** with custom exceptions
- **Automatic retry logic** with exponential backoff
- **Pagination support** with iterator-based helpers
- **Full API coverage** of all Polymarket Gamma endpoints

## Installation

```bash
# Install the package
pip install polymarket-gamma

# Or with uv
uv add polymarket-gamma
```

**Important**:
- **Package name**: `polymarket-gamma` (for installation)
- **Module name**: `py_gamma` (for import)

## Quick Start

```python
import asyncio
from py_gamma import GammaClient

async def main():
    async with GammaClient() as client:
        # List markets
        markets = await client.markets.get_markets(limit=10)
        print(f"Found {len(markets)} markets")

        # Get market by ID
        market = await client.markets.get_market_by_id(markets[0].id)
        print(f"Market: {market.question}")

# Sync version is also available
client = GammaClient()
markets = client.sync.markets.get_markets(limit=10)
```

## API Endpoints

### 🏪 Markets
Get market data and information.

```python
# Get market by ID
market = await client.markets.get_market_by_id("market_id")

# Get market by slug
market = await client.markets.get_market_by_slug("market-slug")

# List markets with filters
markets = await client.markets.get_markets(
    limit=100,
    active=True,
    categories=["crypto"],
    tags=["bitcoin"]
)

# Iterate through all markets
async for market in client.markets.iter_all_markets(page_size=50):
    print(market.question)
```

### 🏷️ Tags
Browse and search market tags.

```python
# Get tag by ID
tag = await client.tags.get_tag_by_id("tag_id")

# List all tags
tags = await client.tags.get_tags(limit=100)

# Get carousel tags
carousel_tags = await client.tags.get_carousel_tags()

# Search tags
bitcoin_tags = await client.tags.search_tags("bitcoin")

# Sync version
tags = client.sync.tags.list_sync(limit=50)
```

### 🔍 Search
Search across markets, events, and profiles.

```python
# General search
result = await client.search.search("bitcoin", limit_per_type=10)

# Search markets only
markets = await client.search.search_markets("election")

# Search events only
events = await client.search.search_events("sports")

# Search profiles
profiles = await client.search.search_profiles("trader")

# Get trending tags
trending = await client.search.get_trending_tags()
```

### 📅 Events
Get event information and related markets.

```python
# Get event by ID
event = await client.events.get_event_by_id("event_id")

# Get event by slug
event = await client.events.get_event_by_slug("event-slug")

# List events with filters
events = await client.events.get_events(
    active=True,
    limit=100
)

# Get featured events
featured = await client.events.get_featured_events()

# Iterate through all events
async for event in client.events.iter_all_events():
    print(event.title)
```

### 📚 Series
Browse market series and collections.

```python
# Get series by ID
series = await client.series.get_series_by_id("series_id")

# Get series by slug
series = await client.series.get_series_by_slug("series-slug")

# List all series
all_series = await client.series.get_series(limit=100)

# Search series
election_series = await client.series.search_series("election")

# Get markets for a series
markets = await client.series.get_markets_for_series("series_id")

# Iterate through all series
async for series in client.series.iter_all_series():
    print(series.title)
```

### ⚽ Sports
Access sports betting markets and leagues.

```python
# List all sports
sports = await client.sports.get_sports()

# Get sport by identifier
sport = await client.sports.get_sport_by_identifier("nfl")

# Get leagues for a sport
leagues = await client.sports.get_leagues_for_sport("nfl")

# Get league by ID
league = await client.sports.get_league_by_id("league_id")

# Get events for a league
events = await client.sports.get_events_for_league("league_id")

# Search leagues
crypto_leagues = await client.sports.search_leagues("crypto")
```

### 💬 Comments
Access market comments and discussions.

```python
# Get comment by ID
comment = await client.comments.get_comment_by_id("comment_id")

# Get comments for a market
comments = await client.comments.get_comments(
    parent_entity_type="market",
    parent_entity_id="market_id",
    limit=50
)

# Get comments by user
user_comments = await client.comments.get_comments_by_user_address(
    user_address,
    limit=100
)

# Get comment replies
replies = await client.comments.get_comment_replies("comment_id")

# Search comments
election_comments = await client.comments.search_comments("election")
```

### 👤 User
Access user profiles and trading data (requires authentication).

```python
# Get current user profile
profile = await client.user.get_profile()

# Get user by ID
user_profile = await client.user.get_profile_by_id("user_id")

# Get user statistics
stats = await client.user.get_stats()

# Get user positions
positions = await client.user.get_positions(
    active_only=True,
    limit=100
)

# Get user history
history = await client.user.get_history(limit=100)

# Get complete user data
user = await client.user.get_user(
    user_id="user_id",
    include_stats=True,
    include_positions=True,
    include_history=True
)

# Iterate through positions
async for position in client.user.iter_all_positions():
    print(f"{position.market_question}: {position.outcome}")
```

## Configuration

```python
from py_gamma import GammaClient, GammaConfig

config = GammaConfig(
    api_key="your-api-key",           # Optional: for authenticated endpoints
    base_url="https://gamma-api.polymarket.com",
    enable_cache=True,                # Enable hybrid caching
    cache_ttl=300,                   # Cache TTL in seconds
    max_retries=3,                   # Max retry attempts
    request_timeout=30.0,            # Request timeout in seconds
    debug=True,                      # Enable debug logging
    trace_requests=False             # Enable HTTP request tracing
)

client = GammaClient(config)
```

## Sync Convenience Wrappers

Every async endpoint has a synchronous equivalent:

```python
# Async version
markets = await client.markets.get_markets(limit=10)

# Sync version
markets = client.sync.markets.get_markets(limit=10)

# Available sync endpoints:
client.sync.markets.get_market_by_id()
client.sync.markets.get_market_by_slug()
client.sync.markets.get_markets()

client.sync.tags.get_tag_by_id()
client.sync.tags.get_tags()
client.sync.tags.list_sync()

client.sync.search.search()
client.sync.search.search_markets()
client.sync.search.get_trending_tags()

# ... and many more
```

## Error Handling

```python
from py_gamma import (
    MarketNotFoundError,
    TagNotFoundError,
    SeriesNotFoundError,
    SportNotFoundError,
    EventNotFoundError,
    CommentNotFoundError,
    UserNotFoundError,
    AuthenticationError,
    RateLimitError,
    GammaAPIError
)

try:
    market = await client.markets.get_market_by_id("invalid-id")
except MarketNotFoundError:
    print("Market not found")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except GammaAPIError as e:
    print(f"API error: {e}")
```

## Models

All responses are validated Pydantic models:

```python
from py_gamma import Market, Tag, Event, Series, Sport

# Market model
market: Market = await client.markets.get_market_by_id("id")
print(market.question)        # str
print(market.outcomes)        # List[str]
print(market.active)          # bool
print(market.end_date)        # Optional[datetime]

# Tag model
tag: Tag = await client.tags.get_tag_by_id("id")
print(tag.label)              # str
print(tag.slug)               # str
print(tag.is_carousel)        # Optional[bool]

# All models have helpful methods
market.is_expired            # bool
market.outcome_count         # int
market.get_tag_by_label("crypto")  # Optional[Tag]
```

## Development

```bash
# Clone repository
git clone https://github.com/Unipredict/py-gamma.git
cd py-gamma

# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check src/
uv run ruff format src/

# Run type checking
uv run basedpyright src/
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

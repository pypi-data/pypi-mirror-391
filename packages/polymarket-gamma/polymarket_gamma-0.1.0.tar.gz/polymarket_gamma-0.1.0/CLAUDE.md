# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Py-Gamma is a modern Python SDK for the Polymarket Gamma API, built with async-first design, strict type safety, and comprehensive caching.

## Development Commands

```bash
# Install dependencies
uv sync --dev

# Run linting and formatting
uv run ruff check src/
uv run ruff format src/

# Run type checking
uv run basedpyright src/

# Run tests
uv run pytest
uv run pytest tests/test_models/test_markets.py::TestMarket::test_market_creation  # Single test

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Build package
uv build
```

## Architecture

### Core Components
- **Client (`client.py`)**: Main SDK client with async-first design and sync convenience wrappers
- **Models (`models/`)**: Pydantic v2 models for data validation and serialization
- **Endpoints (`endpoints/`)**: HTTP clients for each API category
- **Cache (`cache.py`)**: Hybrid memory (LRU) + disk caching system with TTL support
- **Config (`config.py`)**: Environment-based configuration management
- **Exceptions (`exceptions.py`)**: Custom exception hierarchy for different error types

### Key Design Patterns

**Async-First with Sync Convenience:**
```python
# Primary async API
client = GammaClient()
market = await client.markets.get_market_by_id("123")

# Sync convenience wrapper
market = client.sync.markets.get_market_by_id("123")
```

**BaseEndpoint Generic Pattern:**
All endpoints inherit from `BaseEndpoint[T]` where T is the primary model type. The base class provides:
- `self.client` for HTTP requests
- `_parse_response()` and `_parse_response_list()` for Pydantic model validation
- `_paginate()` for iterator-based pagination
- `_build_params()` for query parameter construction

**Hybrid Caching Architecture:**
- Memory LRU cache for frequently accessed data
- Disk cache persistence for cross-session storage
- Cache keys generated from HTTP method, URL, and parameters
- TTL-based expiration with configurable cache times

## Project Structure

```
py-gamma/
├── src/py_gamma/
│   ├── client.py              # Main async HTTP client and GammaClient
│   ├── config.py              # Pydantic-based configuration with env vars
│   ├── cache.py               # Hybrid caching system
│   ├── exceptions.py          # Custom exception hierarchy
│   ├── models/                # Pydantic models
│   │   ├── base.py            # BaseGammaModel, TimestampedModel
│   │   └── markets.py         # Market, Category, Tag models with validation
│   └── endpoints/             # API endpoint implementations
│       ├── base.py            # BaseEndpoint[T] generic class
│       └── markets.py         # MarketsEndpoint implementation
├── tests/
│   ├── conftest.py            # pytest fixtures and configuration
│   └── test_models/           # Model validation tests
└── examples/                  # Working examples and test scripts
```

## Implementation Lessons Learned (Markets Endpoint)

### Model Validation Challenges
When implementing the Market model from API documentation, encountered several validation issues that required custom field validators:

**String Array Parsing:** API returns JSON strings instead of arrays for some fields:
```python
# API returns: "outcomes": "[\"Yes\", \"No\"]"
# Validator handles conversion:
if "outcomes" in data and isinstance(data["outcomes"], str):
    data["outcomes"] = json.loads(data["outcomes"])
```

**DateTime Parsing:** Multiple datetime formats in API responses:
```python
@field_validator("end_date", "created_at", "updated_at", mode="before")
@classmethod
def parse_datetime(cls, v) -> Optional[datetime]:
    if isinstance(v, str):
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            return None  # Fallback for unparseable dates
```

**Nested Object Construction:** Categories and Tags need proper instantiation:
```python
if "categories" in data and isinstance(data["categories"], list):
    data["categories"] = [
        Category(**cat) if isinstance(cat, dict) else cat
        for cat in data["categories"]
    ]
```

### HTTP Client Implementation Details
**Retry Logic:** Exponential backoff for network errors with smart error classification:
- Temporary errors (5xx): retry with exponential backoff
- Client errors (4xx): raise immediately
- Network errors: retry up to configured limit

**Proxy Environment Handling:** Automatic proxy detection causes SOCKS errors; disabled by default in client initialization.

### Type Safety Challenges
**Generic Type Constraints:** `BaseEndpoint[T]` requires careful type annotations for Pydantic model methods:
```python
async def _parse_response(self, response: httpx.Response, model_class: Type[T]) -> T:
    return model_class.model_validate(data)  # type: ignore[attr-defined]
```

**Cache Type Safety:** Hybrid cache needs proper type annotations for different storage backends while handling dynamic third-party library types.

## Adding New Endpoints Workflow

### 1. Create Pydantic Models (`models/category.py`)
```python
class Category(BaseGammaModel):
    id: Optional[str] = Field(None, description="Category identifier")
    name: Optional[str] = Field(None, description="Category name")
    # Add field validators for parsing challenges
```

### 2. Implement Endpoint (`endpoints/categories.py`)
```python
class CategoriesEndpoint(BaseEndpoint[Category]):
    async def get_category_by_id(self, category_id: str) -> Category:
        response = await self._get(f"/categories/{category_id}")
        return await self._parse_response(response, Category)
```

### 3. Add Exception Classes (`exceptions.py`)
```python
class CategoryNotFoundError(GammaAPIError):
    def __init__(self, category_id: str):
        super().__init__(f"Category {category_id} not found", status_code=404)
```

### 4. Update Client (`client.py`)
```python
from .endpoints.categories import CategoriesEndpoint

class GammaClient:
    def __init__(self, config: Optional[GammaConfig] = None):
        # ... existing init ...
        self.categories = CategoriesEndpoint(self.http_client)
```

### 5. Update Exports (`__init__.py`)
```python
from .endpoints import CategoriesEndpoint
from .models import Category
__all__.extend(["CategoriesEndpoint", "Category"])
```

### 6. Add Tests
```python
class TestCategoriesEndpoint:
    @pytest.mark.asyncio
    async def test_get_category_by_id(self, gamma_client):
        category = await gamma_client.categories.get_category_by_id("test")
        assert isinstance(category, Category)
```

## Type Checking Configuration

Uses basedpyright in strict mode with careful configuration:
- **Strict mode** for maximum type safety
- **Third-party library stubs disabled** (diskcache, cachetools) due to missing type definitions
- **Unknown type warnings disabled** only for unavoidable dynamic third-party APIs
- **Strict checking** for all application code

## Strict Mode Type Checking Experience

### Common Challenges and Solutions

**1. Dynamic Third-Party Library Types**
```python
# Challenge: diskcache and cachetools lack type stubs
# Solution: Runtime type assertions for critical code paths
assert self._client is not None, "HTTP client must be initialized"
```

**2. Protected Method Access**
```python
# Challenge: Accessing private methods from wrapper classes
# Solution: Create public interface methods
class AsyncHTTPClient:
    async def initialize(self) -> None:  # Public method
        await self._ensure_client()

    async def _ensure_client(self) -> None:  # Private implementation
        # implementation
```

**3. Parameter Type Safety**
```python
# Challenge: **kwargs in API methods needs proper typing
# Solution: Explicit Any type annotation for dynamic parameters
async def get_markets(self, **kwargs: Any) -> List[Market]:
```

**4. Cache Type Safety**
```python
# Challenge: Cache values can have multiple types from disk cache
# Solution: Runtime type validation with warnings
if cached_value is not None:
    if not isinstance(cached_value, dict):
        logger.warning(f"Unexpected cache value type: {type(cached_value)}")
        return None
```

**5. Pydantic Field Validators**
```python
# Challenge: Field validators need explicit parameter types
# Solution: Type hints for validator parameters
@field_validator("created_at", mode="before")
@classmethod
def parse_datetime(cls, v: Any) -> Optional[datetime]:
```

### Key Principles for Strict Mode Compliance

1. **No type: ignore** unless absolutely necessary (third-party library limitations)
2. **Runtime assertions** for critical type safety checks
3. **Explicit Any types** for dynamic parameters instead of omitting types
4. **Public interface methods** to avoid accessing protected members from other classes
5. **Runtime validation** for external data sources with proper error handling

All code must pass both ruff linting and basedpyright strict mode type checking before commits.

## Configuration

Use environment variables for configuration:

```bash
# .env file
GAMMA_API_BASE_URL=https://gamma-api.polymarket.com
GAMMA_API_KEY=your_api_key
GAMMA_CACHE_TTL=300
GAMMA_MAX_RETRIES=3
GAMMA_REQUEST_TIMEOUT=30
```

## Testing Strategy

### Unit Tests
- Test model validation with both valid and invalid data
- Test endpoint logic with mocked HTTP responses
- Test error conditions and exception handling

### Integration Tests
- Test against real API endpoints
- Test pagination and iterator functionality
- Test caching behavior

## Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
client = GammaClient(config=GammaConfig(debug=True))
```

Use HTTP tracing to see request/response details:

```python
client = GammaClient(config=GammaConfig(trace_requests=True))
```

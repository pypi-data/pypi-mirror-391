# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive API coverage for all Polymarket Gamma endpoints
- Async-first design with sync convenience wrappers
- Hybrid caching system (memory + disk) with TTL support
- Strict type safety with Pydantic v2 validation
- Automatic retry logic with exponential backoff
- Iterator-based pagination support
- Custom exception hierarchy for better error handling

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [0.1.0] - 2025-01-12

### Added
- Initial release of Py-Gamma SDK
- **Markets API** - Complete market data access with filtering and pagination
- **Tags API** - Tag browsing, carousel tags, and search functionality
- **Search API** - Cross-entity search across markets, events, and profiles
- **Events API** - Event information and related market data
- **Series API** - Market series and collections management
- **Sports API** - Sports betting markets and leagues data
- **Comments API** - Market comments and discussions access
- **User API** - User profiles, positions, statistics, and trading history
- **HTTP Client** - Robust async HTTP client with retry logic and caching
- **Configuration** - Environment-based configuration management
- **Error Handling** - Comprehensive exception hierarchy with custom error types
- **Documentation** - Complete API documentation and example scripts
- **Type Safety** - Full type annotations with strict mode compliance
- **Testing** - Example scripts and integration tests

### Features
- **Async-first Architecture**: Primary async API with sync convenience wrappers
- **Hybrid Caching**: Memory LRU cache with disk persistence
- **Robust Validation**: Pydantic v2 models with field validators
- **Pagination Support**: Both offset-based and iterator-based pagination
- **Authentication Support**: API key authentication for protected endpoints
- **Development Tools**: Comprehensive linting, formatting, and type checking

### Documentation
- README with complete API examples and usage patterns
- Contributing guidelines for developers
- CLAUDE.md with AI assistant development guidance
- Example scripts demonstrating all major functionality
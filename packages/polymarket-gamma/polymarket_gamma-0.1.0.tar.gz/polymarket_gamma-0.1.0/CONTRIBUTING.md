# Contributing to Py-Gamma

We welcome contributions to the Py-Gamma SDK! This guide will help you get started.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Unipredict/py-gamma.git
   cd py-gamma
   ```

2. **Install dependencies:**
   ```bash
   uv sync --dev
   ```

3. **Set up your environment:**
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_models/test_markets.py

# Run with verbose output
uv run pytest -v
```

## Code Quality

We use the following tools to maintain code quality:

```bash
# Run linting (will fix issues automatically)
uv run ruff check src/ --fix

# Run formatting
uv run ruff format src/

# Run type checking
uv run basedpyright src/
```

## Project Structure

```
py-gamma/
├── src/py_gamma/
│   ├── client.py              # Main HTTP client
│   ├── config.py              # Configuration management
│   ├── cache.py               # Caching system
│   ├── exceptions.py          # Custom exceptions
│   ├── models/                # Pydantic models
│   │   ├── base.py           # Base model classes
│   │   ├── markets.py        # Market models
│   │   ├── tags.py           # Tag models
│   │   ├── events.py         # Event models
│   │   ├── series.py         # Series models
│   │   ├── sports.py         # Sports models
│   │   ├── search.py         # Search models
│   │   ├── user.py           # User models
│   │   └── comments.py       # Comment models
│   └── endpoints/             # API endpoint implementations
│       ├── base.py           # Base endpoint class
│       ├── markets.py        # Markets endpoint
│       ├── tags.py           # Tags endpoint
│       ├── search.py         # Search endpoint
│       ├── events.py         # Events endpoint
│       ├── series.py         # Series endpoint
│       ├── sports.py         # Sports endpoint
│       ├── user.py           # User endpoint
│       └── comments.py       # Comments endpoint
├── tests/                     # Test files
├── examples/                  # Example scripts
└── docs/                      # Documentation
```

## Adding New Endpoints

1. **Create Pydantic models** in `src/py_gamma/models/`
   - Follow existing patterns
   - Include proper field validation
   - Add helper methods and properties

2. **Create endpoint implementation** in `src/py_gamma/endpoints/`
   - Inherit from `BaseEndpoint[T]`
   - Implement async-first design
   - Add sync convenience wrappers
   - Include comprehensive error handling

3. **Update the client** in `src/py_gamma/client.py`
   - Import and initialize the new endpoint
   - Add to the `__init__` method

4. **Update exports** in `src/py_gamma/__init__.py`
   - Export new models, endpoints, and exceptions

5. **Add tests** in `tests/`
   - Test model validation
   - Test endpoint functionality
   - Test error conditions

## Coding Standards

- **Type Safety**: All code must pass `basedpyright` strict mode
- **Style**: Follow `ruff` formatting and linting rules
- **Async-First**: Primary methods should be async with sync convenience wrappers
- **Error Handling**: Use custom exception classes with helpful messages
- **Documentation**: Include docstrings for all public methods and classes

## Submitting Changes

1. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and ensure all tests pass:
   ```bash
   uv run ruff check src/ --fix
   uv run ruff format src/
   uv run basedpyright src/
   uv run pytest
   ```

3. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

4. **Push and create a pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Issue Reporting

- Use the [issue tracker](https://github.com/Unipredict/py-gamma/issues) for bug reports
- Provide clear reproduction steps
- Include error messages and logs
- Specify your Python version and environment

## Feature Requests

- Open an issue with the "enhancement" label
- Describe the use case and proposed implementation
- Consider if it fits the SDK's scope and design

## Questions

- Use GitHub [Discussions](https://github.com/Unipredict/py-gamma/discussions) for questions
- Check existing issues and discussions first
- Provide context and examples when asking questions

Thank you for contributing to Py-Gamma! 🚀

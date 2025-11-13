# Publishing Py-Gamma with uv

This guide explains how to publish the Py-Gamma SDK to PyPI using `uv`.

## Prerequisites

1. **Install uv**: If not already installed
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # or with brew: brew install uv
   ```

2. **PyPI Account**: Create an account at [PyPI](https://pypi.org/account/register/)

3. **API Token**: Generate an API token at [PyPI Account Settings](https://pypi.org/manage/account/token/)

4. **Configure Authentication**:
   ```bash
   # Option 1: Set environment variable
   export UV_PUBLISH_TOKEN="your-pypi-token"

   # Option 2: Use keyring (recommended)
   uv publish --publish-url https://upload.pypi.org/legacy/ --token __token__
   ```

## Publishing Steps

### 1. Prepare the Package

```bash
# Ensure all dependencies are synced
uv sync --dev

# Run quality checks
uv run ruff check src/ --fix
uv run ruff format src/
uv run basedpyright src/

# Run tests
uv run pytest
```

### 2. Build the Package

```bash
# Build the distribution files
uv build
```

This will create:
- `dist/py_gamma-0.1.0-py3-none-any.whl` (wheel)
- `dist/py_gamma-0.1.0.tar.gz` (source distribution)

### 3. Check the Package

```bash
# Check the built package for common issues
uv run twine check dist/*
```

### 4. Publish to Test PyPI (Optional but Recommended)

```bash
# First, publish to Test PyPI to verify everything works
uv publish --publish-url https://test.pypi.org/legacy/ dist/*

# Install from Test PyPI to verify
uv add --index-url https://test.pypi.org/simple/ py-gamma
```

### 5. Publish to PyPI

```bash
# Publish to the official PyPI repository
uv publish dist/*
```

## Version Management

### Bumping Version

Edit `pyproject.toml` to update the version:

```toml
[project]
name = "py-gamma"
version = "0.1.1"  # Update this
```

### Semantic Versioning

- **Major (X.0.0)**: Breaking changes
- **Minor (X.Y.0)**: New features, backward compatible
- **Patch (X.Y.Z)**: Bug fixes, backward compatible

### Pre-release Versions

```toml
version = "0.1.1rc1"  # Release candidate
version = "0.1.1a1"   # Alpha
version = "0.1.1b1"   # Beta
```

## Common Publishing Commands

### Quick Publish (Development)

```bash
# For quick development releases to Test PyPI
uv build && uv publish --publish-url https://test.pypi.org/legacy/ dist/*
```

### Production Publish

```bash
# Complete production release workflow
uv sync --dev
uv run ruff check src/ --fix
uv run ruff format src/
uv run basedpyright src/
uv run pytest
uv build
uv run twine check dist/*
uv publish dist/*
```

### Publish with Custom Token

```bash
# Publish with explicit token
uv publish --token __token__ dist/*
```

## Troubleshooting

### Common Issues

1. **Authentication Error**:
   ```bash
   export UV_PUBLISH_TOKEN="your-token"
   # Or use keyring
   uv publish --token __token__
   ```

2. **Version Already Exists**:
   - Bump the version in `pyproject.toml`
   - Delete old distribution files: `rm -rf dist/`

3. **Upload Size Limit**:
   - Check for unnecessary files in your package
   - Use `.gitignore` to exclude large files

4. **Build Errors**:
   ```bash
   # Clean build
   rm -rf dist/ build/
   uv build --verbose
   ```

### Verification Commands

```bash
# Check package metadata
uv run python -c "
import py_gamma
print(f'Version: {py_gamma.__version__}')
print(f'Author: {py_gamma.__author__}')
"

# Test installation from PyPI
uvx --from py-gamma python -c "
import py_gamma
client = py_gamma.GammaClient()
print('Package works correctly!')
"
```

## Publishing Checklist

Before publishing, ensure:

- [ ] All tests pass: `uv run pytest`
- [ ] Code is formatted: `uv run ruff format src/`
- [ ] Linting passes: `uv run ruff check src/`
- [ ] Type checking passes: `uv run basedpyright src/`
- [ ] Documentation is updated: README.md, CHANGELOG.md
- [ ] Version is bumped appropriately
- [ ] CHANGELOG.md is updated with changes
- [ ] Package builds successfully: `uv build`
- [ ] Package passes checks: `uv run twine check dist/*`
- [ ] Tested on Test PyPI (recommended)
- [ ] License is correct and included
- [ ] All dependencies are specified correctly

## Post-Publishing

1. **Create GitHub Release**: Tag the release with version number
2. **Update Documentation**: Ensure docs reflect new features
3. **Announce**: Share with users and community
4. **Monitor**: Check for any issues or feedback

## Automated Publishing (Optional)

For automated publishing via GitHub Actions:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install uv
      uses: astral-sh/setup-uv@v3
    - name: Build package
      run: uv build
    - name: Publish to PyPI
      uses: astral-sh/setup-uv@v3
      with:
        version: "latest"
      env:
        UV_PUBLISH_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
      run: uv publish dist/*
```

Remember to add `PYPI_API_TOKEN` to your GitHub repository secrets.
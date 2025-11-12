# GitHub Actions Workflows

This directory contains the CI/CD workflows for pytest-semantic.

## Workflows

### `test.yml` - Continuous Integration
- **Triggers**: Push to main/master, pull requests
- **Purpose**: Run tests on every change
- **Matrix**: Tests across Python 3.9, 3.10, 3.11, 3.12
- **Steps**:
  1. Checkout code
  2. Set up Python with pip caching
  3. Install package with test dependencies
  4. Run pytest

### `publish.yml` - PyPI Publishing
- **Triggers**: GitHub release creation
- **Purpose**: Automatically publish to PyPI
- **Jobs**:
  1. **test**: Run full test suite across all Python versions
  2. **deploy**: Build and publish to PyPI (only after tests pass)
- **Security**: Uses Trusted Publishing (OIDC) instead of API tokens
- **Environment**: `release` (can add protection rules)

## Publishing Process

When you create a GitHub release:
1. Tests run automatically across all Python versions
2. If tests pass, package is built using hatchling
3. Package is published to PyPI via Trusted Publishing
4. No manual intervention needed!

## Build Backend

We use **hatchling** instead of setuptools because:
- Modern, designed for pyproject.toml
- No legacy deprecation warnings
- Cleaner configuration
- Faster builds

This follows the same principles as PACKAGE_SETUP.md but uses modern tooling appropriate for 2024/2025.

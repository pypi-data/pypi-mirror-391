# Contributing to Python CLI Template

Thank you for contributing! This document explains how to work with this template project.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/cli-template.git
cd cli-template

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --group dev
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

Edit the code following these guidelines:
- **Type hints**: All functions must have type hints
- **Docstrings**: Public functions need docstrings
- **Tests**: Add tests for new functionality
- **Simplicity**: Prefer simple, readable code over clever solutions

### 3. Run Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/test_cli.py

# Run with coverage
uv run pytest --cov=cli_template
```

### 4. Check Code Quality

```bash
# Format code (modifies files)
uv run ruff format cli_template/ tests/

# Lint code
uv run ruff check cli_template/ tests/

# Fix auto-fixable lint issues
uv run ruff check --fix cli_template/ tests/

# Type check
uv run pyright cli_template/
```

### 5. Commit Changes

Use [conventional commit](https://www.conventionalcommits.org/) format:

```bash
# Feature (minor version bump)
git commit -m "feat: add new greeting format option"

# Bug fix (patch version bump)
git commit -m "fix: handle empty name gracefully"

# Breaking change (major version bump)
git commit -m "feat!: redesign CLI arguments"

# Documentation (no version bump)
git commit -m "docs: update usage examples"

# Chore/maintenance (no version bump)
git commit -m "chore: update dependencies"
```

**Commit Message Format**:
```
<type>: <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `chore`: Maintenance tasks (dependencies, configs)
- `refactor`: Code refactoring (no behavior change)
- `test`: Adding or modifying tests
- `perf`: Performance improvements

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Quality Standards

### Type Hints

All functions must have type hints:

```python
# Good ✅
def greet(name: str, loud: bool = False) -> str:
    return f"Hello, {name}!"

# Bad ❌
def greet(name, loud=False):
    return f"Hello, {name}!"
```

### Docstrings

Public functions need docstrings:

```python
def greet(name: str, loud: bool = False) -> str:
    """Generate a greeting message.

    Args:
        name: Name to greet
        loud: If True, return in UPPERCASE

    Returns:
        Formatted greeting string
    """
    return f"Hello, {name}!"
```

### Code Formatting

- **Line length**: 88 characters (ruff default)
- **Quotes**: Double quotes for strings
- **Indentation**: 4 spaces (no tabs)

### Testing

- **Unit tests**: Test individual functions in isolation
- **Test naming**: `test_<function>_<scenario>()`
- **Markers**: Use `@pytest.mark.unit` for unit tests
- **Fixtures**: Reuse fixtures from `conftest.py`

Example:
```python
import pytest
from cli_template.main import greet


@pytest.mark.unit
def test_greet_basic():
    """Test basic greeting."""
    result = greet("World")
    assert result == "Hello, World!"


@pytest.mark.unit
def test_greet_invalid_count():
    """Test that invalid count raises error."""
    with pytest.raises(ValueError):
        greet("World", count=0)
```

## Project Structure

```
cli_template/
├── __init__.py       # Package version
├── cli.py            # CLI argument parsing
└── main.py           # Core logic

tests/
├── conftest.py       # Shared fixtures
└── unit/             # Unit tests
    ├── test_cli.py   # CLI tests
    └── test_main.py  # Main logic tests

scripts/
└── bump_version.py   # Version automation (for CI/CD)

.github/workflows/
├── ci.yml            # Test/lint/type-check on PR
└── release.yml       # Auto-release on main
```

## Release Process

**Releases are fully automated!** No manual steps needed.

### How it works:

1. **You commit** to main with conventional commit message
2. **GitHub Actions** analyzes commits since last tag
3. **Version is bumped** automatically (major/minor/patch)
4. **Git tag is created** (e.g., `v0.2.0`)
5. **Package is built** and published to PyPI
6. **GitHub Release** is created with auto-generated notes

### Triggering a Release

Just push to main:

```bash
git commit -m "feat: add new feature"
git push origin main
```

No need to:
- ❌ Manually bump version in files
- ❌ Create git tags manually
- ❌ Build the package yourself
- ❌ Publish to PyPI manually

### Version Calculation

Commits since last tag determine the bump:

- `fix:` → patch (0.1.0 → 0.1.1)
- `feat:` → minor (0.1.0 → 0.2.0)
- `feat!:` or `BREAKING CHANGE` → major (0.1.0 → 1.0.0)
- `docs:`, `chore:` → no bump

### First Release

For the first release (before any tags exist):

```bash
# Option 1: Let CI create v0.1.0 automatically
git commit -m "feat: initial release"
git push origin main

# Option 2: Manually create initial tag
git tag v0.1.0
git push origin v0.1.0
```

## Common Tasks

### Adding a Dependency

```bash
# Add production dependency
uv add package-name

# Add dev dependency
uv add --group dev package-name

# Remove dependency
uv remove package-name
```

### Updating Dependencies

```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add package-name@latest
```

### Running the CLI Locally

```bash
# Via uv run
uv run cli-template [args]

# Or install in editable mode
uv pip install -e .
cli-template [args]
```

### Debugging Tests

```bash
# Run with print statements visible
uv run pytest -v -s

# Run specific test
uv run pytest tests/unit/test_cli.py::test_parse_args_basic -v

# Drop into debugger on failure
uv run pytest --pdb
```

### Checking CI Before Push

Run the same checks that CI runs:

```bash
# All checks in one go
uv run pytest && \
uv run ruff format --check cli_template/ tests/ && \
uv run ruff check cli_template/ tests/ && \
uv run pyright cli_template/
```

## Pull Request Guidelines

### PR Title

Use conventional commit format:

```
feat: add greeting customization
fix: handle edge case in argument parsing
docs: improve usage examples
```

### PR Description

Include:
- **What**: What does this PR do?
- **Why**: Why is this change needed?
- **How**: How was it implemented? (if non-obvious)
- **Testing**: How was it tested?

Template:
```markdown
## What
Adds support for custom greeting prefixes.

## Why
Users requested the ability to customize greetings beyond "Hello".

## How
- Added `--prefix` flag to CLI
- Updated `greet()` function to accept prefix parameter
- Added tests for new functionality

## Testing
- Added unit tests in `test_main.py`
- Manually tested with various prefixes
- All existing tests still pass
```

### Before Submitting PR

Checklist:
- [ ] Tests added and passing
- [ ] Code formatted (`ruff format`)
- [ ] Linting passes (`ruff check`)
- [ ] Type checking passes (`pyright`)
- [ ] Docstrings added for public functions
- [ ] Conventional commit message format

## Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/yourusername/cli-template/discussions)
- **Bugs**: Open an [Issue](https://github.com/yourusername/cli-template/issues)
- **Documentation**: See [README.md](README.md)

## Code of Conduct

Be respectful and constructive. This is a collaborative project.

---

Thank you for contributing! 🎉

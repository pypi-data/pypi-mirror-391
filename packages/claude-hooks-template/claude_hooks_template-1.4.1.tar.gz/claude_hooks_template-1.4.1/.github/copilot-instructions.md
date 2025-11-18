# GitHub Copilot Instructions for Python CLI Template

## Project Overview

This is a **Python CLI template** designed as a GitHub template for creating production-ready CLI applications. The example implementation is a simple greeting CLI (`cli-template` command) that demonstrates the infrastructure.

**Package Name**: `cli-template` (users will rename this)
**CLI Command**: `cli-template` (users will rename this)
**Python Module**: `cli_template` (users will rename this)

## Purpose

This template provides:
- Automated semantic versioning from conventional commits
- CI/CD pipeline for testing, linting, and PyPI publishing
- Type-safe code with strict pyright configuration
- Modern tooling (uv, ruff, pytest)

Users adopt this template by find-replacing package names and replacing the hello-world logic with their actual CLI.

## Architecture and Code Patterns

### Simple, Synchronous Design

The template is intentionally minimal:
- **No async**: Uses simple synchronous code (users add async if needed)
- **No external dependencies**: Empty `dependencies = []` in pyproject.toml
- **Standard library only**: Uses `argparse` for CLI (not Click, Typer, etc.)
- **Pure functions**: Core logic returns values, CLI handles I/O

### Module Organization

```
cli_template/
├── __init__.py    # Package version (from git tags via hatch-vcs)
├── cli.py         # Argument parsing, validation, main() entry point
└── main.py        # Core logic (users replace this with their CLI)
```

**cli.py** responsibilities:
- Parse command-line arguments with `argparse`
- Validate inputs
- Call core logic functions
- Handle I/O (print results, write files)
- Return exit codes (0 success, 1 failure)

**main.py** responsibilities:
- Pure functions that implement business logic
- No I/O operations (returns values instead)
- Fully type-hinted
- Easy to test in isolation

### Type Safety

**All functions must have type hints**:
```python
# Good ✅
def greet(name: str, loud: bool = False, count: int = 1) -> str:
    return f"Hello, {name}!"

# Bad ❌
def greet(name, loud=False, count=1):
    return f"Hello, {name}!"
```

Use `pyright` in strict mode (configured in pyproject.toml).

### Error Handling

- Validate inputs early (in CLI layer)
- Raise descriptive exceptions with clear messages
- Let CLI layer catch exceptions and print user-friendly errors
- Always return proper exit codes (0 or 1)

## Development Practices

### Testing Requirements

Write unit tests for all new functionality:
- Place tests in `tests/unit/`
- Use `@pytest.mark.unit` marker
- Test pure functions in isolation
- Mock I/O operations
- Aim for fast tests (<1 second for entire suite)

Example test structure:
```python
import pytest
from cli_template.main import greet


@pytest.mark.unit
def test_greet_basic():
    """Test basic greeting."""
    result = greet("World")
    assert result == "Hello, World!"


@pytest.mark.unit
def test_greet_invalid_input():
    """Test error handling."""
    with pytest.raises(ValueError):
        greet("", count=0)
```

### Code Quality Tools

Before committing, always run:
```bash
# Format code (modifies files)
uv run ruff format cli_template/ tests/

# Lint code
uv run ruff check cli_template/ tests/

# Type check
uv run pyright cli_template/

# Run tests
uv run pytest tests/unit/ -v
```

### Package Management

Use `uv` for all package operations:
```bash
# Install dependencies
uv sync --group dev

# Add production dependency
uv add package-name

# Add dev dependency
uv add --group dev package-name

# Remove dependency
uv remove package-name

# Update dependencies
uv sync --upgrade
```

## Design Philosophy

### Template vs. User CLI

**Template maintainers** (us):
- Improve infrastructure (versioning, CI/CD, tooling)
- Keep example CLI simple and clear
- Document how to customize
- Avoid adding CLI-specific features

**Template users** (them):
- Replace hello-world logic with their CLI
- Add their dependencies
- Customize for their use case
- Inherit all infrastructure automatically

### Unix Philosophy

Follow "do one thing well":
- Template does: Provide CLI infrastructure
- Users do: Build their actual CLI
- Keep template minimal and generic
- Avoid opinionated CLI frameworks

### Simplicity Over Features

**What NOT to add to template**:
- ❌ Complex CLI frameworks (Click, Typer)
- ❌ Async boilerplate (users add if needed)
- ❌ Database integrations
- ❌ API client code
- ❌ Config file parsing (YAML, TOML)
- ❌ Logging setup beyond basic
- ❌ Subcommands (users add if needed)

**What to maintain**:
- ✅ Automated versioning system
- ✅ CI/CD workflows
- ✅ Type checking configuration
- ✅ Linting/formatting setup
- ✅ Test structure
- ✅ Clear documentation

## Configuration Defaults

### Versioning (Automated)

- **Version source**: Git tags via `hatch-vcs`
- **No manual bumps**: Version calculated from commits
- **Conventional commits**: Used by `scripts/bump_version.py`
- **First release**: v0.1.0 (created automatically on first `feat:` commit)

### Code Quality Standards

- **Line length**: 88 characters (ruff default)
- **Quote style**: Double quotes
- **Type checking**: Strict mode (pyright)
- **Python version**: 3.10+ (matrix test on 3.10 and 3.12)

### CI/CD

**On every push/PR** (`.github/workflows/ci.yml`):
- Run unit tests
- Lint with ruff
- Format check with ruff
- Type check with pyright

**On push to main** (`.github/workflows/release.yml`):
- Analyze commits for version bump
- Create git tag if version changed
- Build package with injected version
- Publish to PyPI (if `PYPI_API_TOKEN` secret set)
- Create GitHub Release

## Commit Convention

Use conventional commits for automated versioning:

| Prefix | Version Bump | Example |
|--------|--------------|---------|
| `fix:` | Patch (0.1.0 → 0.1.1) | `fix: handle empty name` |
| `feat:` | Minor (0.1.0 → 0.2.0) | `feat: add --verbose flag` |
| `feat!:` or `BREAKING CHANGE` | Major (0.1.0 → 1.0.0) | `feat!: redesign CLI args` |
| `docs:`, `chore:`, `refactor:` | No bump | `docs: update README` |

**Examples**:
```bash
git commit -m "fix: correct greeting punctuation"
git commit -m "feat: add custom greeting prefix option"
git commit -m "feat!: change CLI argument names"
git commit -m "docs: improve usage examples"
git commit -m "chore: update dependencies"
git commit -m "refactor: extract validation logic"
```

## Non-Obvious Behaviors

1. **Version comes from git tags**: No `__version__` hardcoded in code (hatch-vcs reads from git)
2. **First tag auto-created**: Pushing `feat:` commit to main creates v0.1.0 automatically
3. **Empty dependencies by design**: Template has no runtime deps (users add their own)
4. **uv.lock checked in**: Ensures reproducible dev environments
5. **No integration tests**: Template doesn't need them (users add for their CLI)
6. **Strict type checking**: Catches issues early, improves code quality

## Code Review Checklist

When reviewing code changes:

**For template infrastructure**:
- [ ] Does it improve versioning, CI/CD, or tooling?
- [ ] Is it generic enough for any CLI?
- [ ] Does it add complexity users must remove?
- [ ] Is it documented in README/CONTRIBUTING?

**For example CLI code**:
- [ ] Is it simple and clear?
- [ ] Does it demonstrate best practices?
- [ ] Are all functions type-hinted?
- [ ] Are tests included?
- [ ] Does it follow conventional commit format?

**Code quality**:
- [ ] All functions have type hints
- [ ] Tests included for new functionality
- [ ] Ruff format passes (`uv run ruff format --check`)
- [ ] Ruff lint passes (`uv run ruff check`)
- [ ] Pyright passes (`uv run pyright cli_template/`)
- [ ] Tests pass (`uv run pytest tests/unit/`)
- [ ] **IMPORTANT**: Include file names and line numbers in feedback (e.g., "cli.py:45" or "line 23 in main.py")

## Common Tasks

### Testing the Template

```bash
# Run all checks (what CI runs)
uv run pytest tests/unit/ -v && \
uv run ruff check cli_template/ tests/ && \
uv run ruff format --check cli_template/ tests/ && \
uv run pyright cli_template/

# Test the CLI locally
uv run cli-template World
uv run cli-template World --loud --count 3
```

### Improving Documentation

When updating docs:
- **README.md**: User-facing, focus on "how to use template"
- **CONTRIBUTING.md**: Developer-facing, focus on "how to contribute"
- **CLAUDE.md**: AI assistant guidance, focus on "project context"
- Keep all three in sync with template changes

### Updating Dependencies

```bash
# Update dev dependencies
uv add --group dev package@latest

# Update all dependencies
uv sync --upgrade

# Regenerate lockfile
uv lock
```

### Versioning Script

`scripts/bump_version.py` is used by CI/CD:
- Don't run manually (CI handles it)
- Analyzes commits since last tag
- Determines version bump type
- Creates git tag
- Outputs version info for GitHub Actions

## Template Customization Guide

When users adopt this template, they should:

1. **Find-replace throughout project**:
   - `cli_template` → `their_package_name`
   - `cli-template` → `their-cli-command`
   - Update `pyproject.toml` metadata (name, author, URLs)

2. **Replace example CLI**:
   - Edit `cli_template/cli.py` for their argument parsing
   - Edit `cli_template/main.py` for their core logic
   - Update tests in `tests/unit/`

3. **Add dependencies**:
   - `uv add package-name` for runtime deps
   - Update imports in code

4. **Configure PyPI** (one-time):
   - Create PyPI API token
   - Add `PYPI_API_TOKEN` to GitHub Secrets
   - Push to main → first release happens automatically

## Known Limitations

1. **No async example**: Template uses sync code (users add async if needed)
2. **No subcommands**: Single command only (users add Click/Typer if needed)
3. **No config files**: No TOML/YAML loading (users add if needed)
4. **argparse only**: No fancy CLI framework (intentional - stay generic)
5. **GitHub Actions only**: No GitLab CI, CircleCI, etc.

These are intentional design choices to keep the template minimal.

## Success Criteria

A successful template means:
- ✅ Users can adopt it in <30 minutes
- ✅ Infrastructure "just works" (no setup needed)
- ✅ First commit triggers automated release
- ✅ Users never manually bump versions
- ✅ CI catches issues before merge
- ✅ Template is easy to customize

## Getting Help

For template users:
- **README.md**: How to use template
- **CONTRIBUTING.md**: How to develop with template
- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions

For template maintainers:
- **CLAUDE.md**: Project context for AI assistance
- **This file**: Copilot-specific guidance
- Keep infrastructure simple and well-documented

---

**Remember**: This is a template, not a product. Keep it minimal, generic, and easy to customize. Users will replace the example CLI with their own - our job is to make that easy and provide excellent infrastructure.

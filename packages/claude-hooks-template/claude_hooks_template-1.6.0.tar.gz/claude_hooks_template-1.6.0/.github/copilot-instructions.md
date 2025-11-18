# GitHub Copilot Instructions for claude-hooks

## Priority Hierarchy

**CRITICAL:** Non-negotiable rules that override ALL other instructions
**IMPORTANT:** High-priority rules rarely overridden except by CRITICAL
**MUST:** Required actions unless explicitly contradicted by higher levels
**Bold:** Strong preferences and key guidance
Regular: Standard instructions and preferences

## Project Overview

`claude-hooks` - CLI tool that makes adding Claude Code hooks easy. No manual JSON editing, no chmod commands, no forgetting syntax. Just run a command and your hook is ready to use.

**IMPORTANT: Package Naming**
- **PyPI Package Name**: `claude-hooks-template` (what users install)
- **CLI Command**: `claude-hooks` (what users run)
- **Python Module**: `claude_hooks` (import name)

Note: The PyPI name includes `-template` suffix to avoid conflicts, but the CLI command and documentation use the shorter `claude-hooks` name for better user experience.

## Purpose

This tool provides:
- Simple CLI for creating Claude Code hook scripts
- Automatic script generation with full documentation
- Automatic settings.json configuration
- Support for all Claude Code hook events

## Architecture and Code Patterns

### Simple Two-File Structure

```
claude_hooks/
├── __init__.py  # Package version (from git tags via hatch-vcs)
├── cli.py       # Argument parsing, command dispatch
└── main.py      # All hook logic (templates, settings, file ops)
```

**Why simple?** Hook installation just creates file + updates JSON. No need for added complexity.

### Core Data Structure: HOOK_CONFIG

Everything starts with `HOOK_CONFIG` dict in `main.py`:

```python
HOOK_CONFIG = {
    "on_edit": {
        "event": "PostToolUse",    # Claude event type
        "matcher": "Edit",          # Tool to match (or None)
        "description": "..."        # Human description
    },
    # ... all other hooks
}
```

This one dict drives:
- CLI help text (available hooks)
- Script template selection (PreToolUse vs PostToolUse)
- Settings.json configuration (event + matcher)
- Validation (unknown hook names rejected)

### Hook Template System

Each Claude event type has different JSON schema, so different template:

- **PreToolUse**: Hooks that can block/allow tools (on_read, on_bash, on_plan)
- **PostToolUse**: Hooks that run after tool completes (on_edit, on_write)
- **UserPromptSubmit**: Runs when user submits prompt (on_user_prompt)
- **Stop**: Runs when Claude stops (on_stop)
- **SessionStart**: Runs on session start (on_start)
- **PreCompact**: Runs before context compaction (on_precompact)
- **Snapshot**: Special PreToolUse for periodic snapshots (on_snapshot)

Templates include:
- Complete INPUT JSON schema docs
- Complete OUTPUT JSON schema docs
- Exit code behavior
- Real jq parsing examples you can copy-paste
- TODO comments showing where to add logic

### Settings.json Structure

Hooks stored in nested structure:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/on_edit.sh"
          }
        ]
      }
    ]
  }
}
```

Code handles:
- Creating nested structure if it doesn't exist
- Checking for duplicate hooks (by matcher + command)
- Preserving existing hooks when adding new ones

### Key Functions

**`add_hook(hook_name: str)`** - Main workflow:
1. Validate hook name exists in HOOK_CONFIG
2. Find `.claude/` directory (must exist)
3. Create `.claude/hooks/` directory if needed
4. Call `create_hook_script()` to make .sh file
5. Read `settings.local.json` (or create empty dict)
6. Call `update_hooks_config()` to add hook entry
7. Write updated settings back
8. Print success message

**`create_hook_script(hook_name, hooks_dir)`**:
1. Get config from HOOK_CONFIG
2. Call `get_script_template()` to generate content
3. Write to `{hook_name}.sh`
4. `chmod 0o755` to make executable
5. Return Path to script

**`get_script_template(hook_name)`**:
1. Look up event type in HOOK_CONFIG
2. Call appropriate template function (`_get_pre_tool_use_template`, etc.)
3. Return bash script string with full documentation

**`update_hooks_config(settings, hook_name, script_path)`**:
1. Get event + matcher from HOOK_CONFIG
2. Create nested structure if missing
3. Build hook entry dict
4. Check if hook already exists (compare matcher or command)
5. Append to event's hooks list
6. Return updated settings dict

**`install_all_hooks()`**:
- Loop through all hooks in HOOK_CONFIG
- Call `add_hook()` for each
- Continue on errors (best effort)

## Type Safety

**CRITICAL:** All functions MUST have complete type hints
**IMPORTANT:** Use strict pyright mode - no `Any` types except for JSON handling

Project uses strict pyright mode. Some type casting needed for JSON dict handling:

```python
# Settings is dict[str, Any] because JSON
settings["hooks"][event] = []  # pyright needs casting
event_hooks_list: list[Any] = cast(list[Any], settings["hooks"][event])
```

This is fine - JSON is inherently untyped. Important parts (hook_name, event, matcher) are typed.

## Development Practices

### Testing Requirements

**MUST:** Write unit tests for all new functionality
**IMPORTANT:** Tests MUST pass before committing

Write unit tests for all new functionality:
- Place tests in `tests/unit/`
- Use `@pytest.mark.unit` marker
- Test pure functions in isolation
- Mock I/O operations
- Aim for fast tests (<1 second for entire suite)

Example test structure:
```python
import pytest
from claude_hooks.main import get_script_template

@pytest.mark.unit
def test_get_script_template():
    """Test template generation."""
    result = get_script_template("on_edit")
    assert "PostToolUse" in result
    assert "on_edit" in result
```

### Code Quality Tools

**MUST:** Run all quality checks before committing
**IMPORTANT:** All checks MUST pass (ruff, pyright, pytest)

Before committing, always run:
```bash
# Format code (modifies files)
uv run ruff format claude_hooks/ tests/

# Lint code
uv run ruff check claude_hooks/ tests/

# Type check
uv run pyright claude_hooks/

# Run tests
uv run pytest tests/unit/ -v
```

### Package Management

Use `uv` for all package operations:
```bash
# Install dependencies
uv sync --group dev

# Add dev dependency
uv add --group dev package-name

# Update dependencies
uv sync --upgrade
```

## CI/CD

**`.github/workflows/ci.yml`** (all pushes/PRs):
- Test on Python 3.10 and 3.12
- Run pytest
- Lint with ruff
- Type check with pyright

**`.github/workflows/release.yml`** (main branch only):
- Run `scripts/bump_version.py` to analyze commits
- Create git tag if version bump needed
- Inject static version into pyproject.toml
- Build wheel
- Publish to PyPI (if `PYPI_API_TOKEN` secret exists)
- Create GitHub Release with generated notes

## Automated Versioning

Version comes from git tags, not source code:

**Development:**
- `hatch-vcs` reads git tags for version
- No tags? Version is `0.0.0+{git-sha}`

**CI/CD:**
- `scripts/bump_version.py` analyzes conventional commits
- Determines bump type (major/minor/patch)
- Creates git tag (e.g., `v0.2.0`)
- GitHub Actions injects static version into pyproject.toml
- Builds and publishes to PyPI

**Conventional commits:**
- `fix:` → patch (0.1.0 → 0.1.1)
- `feat:` → minor (0.1.0 → 0.2.0)
- `BREAKING CHANGE` or `feat!:` → major (0.1.0 → 1.0.0)

## Adding New Hooks

When Claude Code adds new hook event:

1. **Add to HOOK_CONFIG** in `main.py`:
```python
"on_new_hook": {
    "event": "NewEventType",
    "matcher": "ToolName",  # or None if no specific tool matcher
    "description": "What it does",
}
```

2. **Add template function** if event type is not handled:
```python
def _get_new_event_template(hook_name: str, description: str) -> str:
    return f"""#!/bin/bash
# {hook_name} - {description}
# [Add INPUT/OUTPUT schemas here]
"""
```

3. **Update `get_script_template()`** to call new template function:
```python
elif event == "NewEventType":
    return _get_new_event_template(hook_name, description)
```

4. **Add tests** in `tests/unit/test_main.py`

That's all. HOOK_CONFIG drives everything else automatically.

## Design Philosophy

**CRITICAL:** Keep code simple – complexity creates hiding places for bugs
**IMPORTANT:** Prefer boring solution over clever solution

**Simplicity-first approach:**
- One dict (`HOOK_CONFIG`) controls everything
- Template functions return strings (no fancy templating engine)
- Settings.json is dict operations (no schema validation library)
- CLI uses stdlib argparse (no Click/Typer)
- No plugins, no extensions, no configuration files

**Why simplicity works:**
- Hook installation is creating a file + updating JSON
- Event types rarely change
- Template docs more important than fancy code
- Users edit `.sh` files, not Python

## Non-Obvious Behaviors

1. **Duplicate detection** works differently for hooks with/without matchers:
   - With matcher: checks `matcher` field
   - Without matcher: checks `command` path

2. **`install_all_hooks()` continues on errors** - best effort approach

3. **Template functions generate complete docs** - users never need to look up Claude docs

4. **Script path in settings.json is relative** - `.claude/hooks/on_edit.sh` not absolute path

5. **`on_snapshot` hook is PreToolUse** but special template - triggers on every tool use for periodic snapshots

## Commit Convention

**MUST:** Use conventional commits for ALL commits
**IMPORTANT:** Commit format determines version bumps

Use conventional commits for automated versioning:

| Prefix | Version Bump | Example |
|--------|--------------|---------|
| `fix:` | Patch (0.1.0 → 0.1.1) | `fix: handle missing .claude directory` |
| `feat:` | Minor (0.1.0 → 0.2.0) | `feat: add on_snapshot hook` |
| `feat!:` or `BREAKING CHANGE` | Major (0.1.0 → 1.0.0) | `feat!: change hook naming convention` |
| `docs:`, `chore:`, `refactor:` | No bump | `docs: update README` |

## Code Review Checklist

**CRITICAL:** Only review code in current PR diff - NEVER analyze code outside changed files
**CRITICAL:** Only provide feedback you are 100% certain is factually accurate - no opinions or subjective suggestions
**MUST:** Include file names and line numbers in ALL feedback (e.g., "cli.py:45")
**MUST:** Assess certainty level before providing feedback - if not 100% certain, do not comment
**IMPORTANT:** Use structured feedback format below
**IMPORTANT:** Think carefully and thoroughly before providing any feedback

When reviewing code changes:

**Feedback Format:**
```
Howdy partner [Emoji] Finding [Category]:

[Details]
```

**Emoji Encoding:**
- 🤖 = ChatGPT/OpenAI
- 🧠 = Claude/Anthropic
- 🔮 = Qwen/Alibaba
- 🚀 = DeepSeek
- ⚡ = Gemini/Google
- 🦾 = Llama/Meta
- 🌟 = Other/Unknown

**Category:** Architecture | Style | Standards | Organization | Testing | Type Safety

**Suggestion Format:** When possible, provide feedback as suggested changes (GitHub's suggestion feature) rather than just PR comments. This makes it easier to apply fixes directly.

**Certainty Requirements:**
- Only provide feedback on objective, verifiable issues (type errors, test failures, syntax errors, security vulnerabilities)
- Do NOT provide feedback based on preferences, style opinions, or subjective architectural choices
- Before commenting, verify the issue is demonstrably incorrect or will cause measurable problems
- If uncertain whether feedback is factual vs. opinion, do not comment

**Thinking Process:**
- Take time to carefully analyze the code before providing feedback
- Verify each concern against documentation, type signatures, and test results
- Consider whether the issue is objectively wrong or just different from your preference
- Only comment when 100% certain the feedback is accurate and actionable

**Functionality**:
- [ ] Does it improve hook installation experience?
- [ ] Does template include complete documentation?
- [ ] Are all functions type-hinted?
- [ ] Are tests included?
- [ ] Does it follow conventional commit format?

**Code quality**:
- [ ] All functions have type hints
- [ ] Tests included for new functionality
- [ ] Ruff format passes (`uv run ruff format --check`)
- [ ] Ruff lint passes (`uv run ruff check`)
- [ ] Pyright passes (`uv run pyright claude_hooks/`)
- [ ] Tests pass (`uv run pytest tests/unit/`)

## Common Tasks

### Testing Locally

```bash
# Run all checks (what CI runs)
uv run pytest tests/unit/ -v && \
uv run ruff check claude_hooks/ tests/ && \
uv run ruff format --check claude_hooks/ tests/ && \
uv run pyright claude_hooks/

# Test the CLI locally
uv run claude-hooks --help
uv run claude-hooks add on_edit
uv run claude-hooks install
```

### Testing Installed Version

```bash
# Install globally
uv tool install claude-hooks-template

# Test it
claude-hooks --help
claude-hooks add on_edit

# Upgrade to latest
uv tool upgrade claude-hooks-template
```

### Improving Documentation

When updating docs:
- **README.md**: User-facing, focus on "how to use tool"
- **CONTRIBUTING.md**: Developer-facing, focus on "how to contribute"
- **CLAUDE.md**: AI assistant guidance, focus on "project context"
- **This file**: Copilot-specific guidance

## Configuration Defaults

### Code Quality Standards

**CRITICAL:** Strict pyright mode - no exceptions
**MUST:** Follow ruff formatting exactly

- **Line length**: 88 characters (ruff default)
- **Quote style**: Double quotes
- **Type checking**: Strict mode (pyright)
- **Python version**: 3.10+ (matrix test on 3.10 and 3.12)

### Versioning Script

`scripts/bump_version.py` is used by CI/CD:
- Don't run manually (CI handles it)
- Analyzes commits since last tag
- Determines version bump type
- Creates git tag
- Outputs version info for GitHub Actions

## Success Criteria

A successful tool means:
- ✅ Users can install hook in <30 seconds
- ✅ Generated hooks have complete documentation
- ✅ No manual JSON editing required
- ✅ Scripts automatically executable
- ✅ Works with all Claude Code hook events
- ✅ CI catches issues before merge

## Getting Help

For users:
- **README.md**: How to use tool
- **GitHub Issues**: Report bugs or request features

For contributors:
- **CLAUDE.md**: Project context for AI assistance
- **This file**: Copilot-specific guidance
- **CONTRIBUTING.md**: Development workflow

---

**Remember**: This tool makes Claude Code hooks easy. Keep it simple, keep it working, keep docs clear.

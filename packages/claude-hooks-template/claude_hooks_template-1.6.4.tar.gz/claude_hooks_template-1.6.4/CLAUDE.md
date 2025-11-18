# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`claude-hooks` - CLI tool that makes adding Claude Code hooks easy. No manual JSON editing, no chmod commands, no forgetting syntax. Just run command and hook ready to use.

**What it does:**
- Creates `.sh` hook scripts with full documentation
- Makes scripts executable automatically
- Updates `.claude/settings.local.json` with correct configuration
- Supports all Claude Code hook events

## Commands

### Development

```bash
# Install dependencies
uv sync --group dev

# Run tests
uv run pytest                    # All tests
uv run pytest tests/unit/ -v    # Unit tests only
uv run pytest --cov=claude_hooks # With coverage

# Code quality
uv run ruff format claude_hooks/ tests/  # Format
uv run ruff check claude_hooks/ tests/   # Lint
uv run pyright claude_hooks/             # Type check

# Run CLI locally
uv run claude-hooks --help
uv run claude-hooks add on_edit
uv run claude-hooks install
```

## Code Architecture

### Simple Two-File Structure

```
claude_hooks/
├── cli.py   # Argument parsing, command dispatch
└── main.py  # All hook logic (templates, settings, file ops)
```

**Why simple?** Hook installation just create file + update JSON. No need for complexity.

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
    "PostToolUse": [           // Event type
      {
        "matcher": "Edit",      // Optional: filter by tool
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
- Creating nested structure if doesn't exist
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

Project uses strict pyright mode. Some type casting needed for JSON dict handling:

```python
# Settings is dict[str, Any] because JSON
settings["hooks"][event] = []  # pyright needs casting
event_hooks_list: list[Any] = cast(list[Any], settings["hooks"][event])
```

This fine - JSON inherently untyped. Important parts (hook_name, event, matcher) are typed.

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

## Testing

Only unit tests (tool too simple for integration tests):

```
tests/
├── conftest.py          # Fixtures (temp directories)
└── unit/
    ├── test_cli.py      # Argument parsing, command dispatch
    └── test_main.py     # Core functions (template gen, settings update)
```

Tests use temp directories, never touch real `.claude/` directory.

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

## Adding New Hooks

When Claude Code adds new hook event:

1. **Add to HOOK_CONFIG** in `main.py`:
```python
"on_new_hook": {
    "event": "NewEventType",
    "matcher": "ToolName" or None,
    "description": "What it does",
}
```

2. **Add template function** if event type not handled:
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

4. **Test it** - add test cases in `tests/unit/test_main.py`

That all. HOOK_CONFIG drives everything else automatically.

## Design Philosophy

**Grug simple approach:**
- One dict (`HOOK_CONFIG`) controls everything
- Template functions return strings (no fancy templating engine)
- Settings.json is dict operations (no schema validation library)
- CLI uses stdlib argparse (no Click/Typer)
- No plugins, no extensions, no configuration files

**Why simple work:**
- Hook installation is create file + update JSON
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

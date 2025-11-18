"""Main logic for claude-hooks."""

import json
from pathlib import Path
from typing import Any, cast

# Hook configuration mapping
HOOK_CONFIG = {
    "on_edit": {
        "event": "PostToolUse",
        "matcher": "Edit",
        "description": "Triggers after Edit tool completes",
    },
    "on_todo_complete": {
        "event": "PostToolUse",
        "matcher": "TodoWrite",
        "description": "Triggers after TodoWrite tool completes",
    },
    "on_stop": {
        "event": "Stop",
        "matcher": None,
        "description": "Triggers when agent stops responding",
    },
    "on_start": {
        "event": "SessionStart",
        "matcher": None,
        "description": "Triggers when session starts",
    },
    "on_bash": {
        "event": "PreToolUse",
        "matcher": "Bash",
        "description": "Triggers before Bash tool executes",
    },
    "on_git_commit": {
        "event": "PreToolUse",
        "matcher": "Bash",
        "description": "Triggers before Bash tool executes (filter for git commit in script)",
    },
    "on_ask_user": {
        "event": "PreToolUse",
        "matcher": "AskUserQuestion",
        "description": "Triggers before AskUserQuestion tool executes",
    },
    "on_write": {
        "event": "PostToolUse",
        "matcher": "Write",
        "description": "Triggers after Write tool completes",
    },
    "on_multiedit": {
        "event": "PostToolUse",
        "matcher": "MultiEdit",
        "description": "Triggers after MultiEdit tool completes",
    },
    "on_task_complete": {
        "event": "PostToolUse",
        "matcher": "Task",
        "description": "Triggers after Task tool completes",
    },
    "on_read": {
        "event": "PreToolUse",
        "matcher": "Read",
        "description": "Triggers before Read tool executes",
    },
    "on_user_prompt": {
        "event": "UserPromptSubmit",
        "matcher": None,
        "description": "Triggers when user submits a prompt",
    },
    "on_plan": {
        "event": "PreToolUse",
        "matcher": "ExitPlanMode",
        "description": "Triggers before ExitPlanMode tool executes",
    },
    "on_precompact": {
        "event": "PreCompact",
        "matcher": None,
        "description": "Triggers before context compaction begins",
    },
    "on_snapshot": {
        "event": "PreToolUse",
        "matcher": None,
        "description": "Triggers periodically to save conversation snapshots",
    },
}


def _get_pre_tool_use_template(hook_name: str, description: str) -> str:
    """Generate PreToolUse event template."""
    return f"""#!/bin/bash
# {hook_name} - {description}
#
# INPUT JSON SCHEMA:
# {{
#   "session_id": "string",
#   "transcript_path": "string",
#   "cwd": "string",
#   "permission_mode": "default|plan|acceptEdits|bypassPermissions",
#   "hook_event_name": "PreToolUse",
#   "tool_name": "string (e.g., 'Read', 'Edit', 'Bash')",
#   "tool_input": {{}} (tool-specific parameters)
# }}
#
# OUTPUT JSON SCHEMA:
# {{
#   "hookSpecificOutput": {{
#     "hookEventName": "PreToolUse",
#     "permissionDecision": "allow|deny|ask",
#     "permissionDecisionReason": "string (optional)",
#     "updatedInput": {{}} (optional - modify tool parameters)
#   }},
#   "continue": true|false (optional, default: true),
#   "stopReason": "string (optional)",
#   "suppressOutput": true|false (optional, default: false),
#   "systemMessage": "string (optional)"
# }}
#
# EXIT CODES:
#   0 - Normal success (allow tool execution)
#   2 - Block tool execution and show stderr to Claude
#   Other - Error condition
#
# EXAMPLES:
#
#   # Allow tool execution:
#   echo '{{"hookSpecificOutput": {{"hookEventName": "PreToolUse", "permissionDecision": "allow"}}}}'
#
#   # Block tool execution:
#   echo '{{"hookSpecificOutput": {{"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Restricted file"}}}}'
#
#   # Modify tool input (e.g., change file path):
#   MODIFIED_INPUT=$(echo "$INPUT" | jq '.tool_input.file_path = "/new/path"')
#   echo '{{"hookSpecificOutput": {{"hookEventName": "PreToolUse", "permissionDecision": "allow", "updatedInput": '"$MODIFIED_INPUT"'}}}}'
#
#   # Parse specific fields:
#   TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')
#   FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
#   CWD=$(echo "$INPUT" | jq -r '.cwd')

INPUT=$(cat)

# Default: allow tool execution
echo '{{"hookSpecificOutput": {{"hookEventName": "PreToolUse", "permissionDecision": "allow"}}}}'

# TODO: Add your hook logic here
# Input available in $INPUT variable
# Parse fields with jq as shown in examples above

exit 0
"""


def _get_post_tool_use_template(hook_name: str, description: str) -> str:
    """Generate PostToolUse event template."""
    return f"""#!/bin/bash
# {hook_name} - {description}
#
# INPUT JSON SCHEMA:
# {{
#   "session_id": "string",
#   "transcript_path": "string",
#   "cwd": "string",
#   "permission_mode": "default|plan|acceptEdits|bypassPermissions",
#   "hook_event_name": "PostToolUse",
#   "tool_name": "string (e.g., 'Edit', 'Write', 'TodoWrite')",
#   "tool_input": {{}} (tool-specific parameters that were used),
#   "tool_response": {{}} (tool-specific response/result)
# }}
#
# OUTPUT JSON SCHEMA:
# {{
#   "decision": "block|undefined (optional)",
#   "reason": "string (required if decision is 'block')",
#   "hookSpecificOutput": {{
#     "hookEventName": "PostToolUse",
#     "additionalContext": "string (optional - added to Claude's context)"
#   }},
#   "continue": true|false (optional, default: true),
#   "stopReason": "string (optional)",
#   "suppressOutput": true|false (optional, default: false),
#   "systemMessage": "string (optional)"
# }}
#
# EXIT CODES:
#   0 - Normal success
#   2 - Show stderr to Claude for processing
#   Other - Error condition
#
# NOTE: Tool has already executed when this hook runs!
#
# EXAMPLES:
#
#   # Add context about what was changed:
#   FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
#   echo '{{"hookSpecificOutput": {{"hookEventName": "PostToolUse", "additionalContext": "Modified: '"$FILE_PATH"'"}}}}'
#
#   # Parse edited content (for Edit tool):
#   OLD_STRING=$(echo "$INPUT" | jq -r '.tool_input.old_string // empty')
#   NEW_STRING=$(echo "$INPUT" | jq -r '.tool_input.new_string // empty')
#
#   # Parse tool response:
#   RESPONSE=$(echo "$INPUT" | jq -r '.tool_response')
#
#   # Access common fields:
#   TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')
#   CWD=$(echo "$INPUT" | jq -r '.cwd')

INPUT=$(cat)

# Default: do nothing, let tool result pass through
echo '{{}}'

# TODO: Add your hook logic here
# Tool has already executed - you can only add context or run side effects
# (e.g., run linter, update docs, send notification)

exit 0
"""


def _get_user_prompt_submit_template(hook_name: str, description: str) -> str:
    """Generate UserPromptSubmit event template."""
    return f"""#!/bin/bash
# {hook_name} - {description}
#
# INPUT JSON SCHEMA:
# {{
#   "session_id": "string",
#   "transcript_path": "string",
#   "cwd": "string",
#   "permission_mode": "default|plan|acceptEdits|bypassPermissions",
#   "hook_event_name": "UserPromptSubmit",
#   "prompt": "string (the user's submitted prompt)"
# }}
#
# OUTPUT JSON SCHEMA:
# {{
#   "decision": "block|undefined (optional)",
#   "reason": "string (shown to user if blocked)",
#   "hookSpecificOutput": {{
#     "hookEventName": "UserPromptSubmit",
#     "additionalContext": "string (optional - injected into Claude's context)"
#   }},
#   "continue": true|false (optional, default: true),
#   "stopReason": "string (optional)",
#   "suppressOutput": true|false (optional, default: false),
#   "systemMessage": "string (optional)"
# }}
#
# EXIT CODES:
#   0 - Normal success (can inject context via stdout OR JSON additionalContext)
#   2 - Block prompt and erase from context, show stderr to user
#   Other - Error condition
#
# EXAMPLES:
#
#   # Inject additional context:
#   echo '{{"hookSpecificOutput": {{"hookEventName": "UserPromptSubmit", "additionalContext": "Current git branch: main"}}}}'
#
#   # Block prompt:
#   echo '{{"decision": "block", "reason": "Prompt contains restricted content"}}}}'
#   exit 2
#
#   # Parse user's prompt:
#   USER_PROMPT=$(echo "$INPUT" | jq -r '.prompt')
#
#   # Check for keywords:
#   if echo "$USER_PROMPT" | grep -q "forbidden"; then
#     echo '{{"decision": "block", "reason": "Forbidden keyword detected"}}}}'
#     exit 2
#   fi

INPUT=$(cat)

# Default: do nothing, let prompt through
echo '{{}}'

# TODO: Add your hook logic here
# Use this to inject context (git status, env vars, etc.) or validate prompts

exit 0
"""


def _get_stop_template(hook_name: str, description: str) -> str:
    """Generate Stop event template."""
    return f"""#!/bin/bash
# {hook_name} - {description}
#
# INPUT JSON SCHEMA:
# {{
#   "session_id": "string",
#   "transcript_path": "string",
#   "permission_mode": "default|plan|acceptEdits|bypassPermissions",
#   "hook_event_name": "Stop",
#   "stop_hook_active": true|false (indicates if already continuing from previous stop)
# }}
#
# OUTPUT JSON SCHEMA:
# {{
#   "decision": "block|undefined (optional)",
#   "reason": "string (required if decision is 'block')",
#   "continue": true|false (optional, default: true),
#   "stopReason": "string (optional)",
#   "suppressOutput": true|false (optional, default: false),
#   "systemMessage": "string (optional)"
# }}
#
# EXIT CODES:
#   0 - Normal success
#   2 - Block stoppage and show stderr to Claude (makes Claude continue)
#   Other - Error condition
#
# IMPORTANT: Check stop_hook_active to prevent infinite loops!
#
# EXAMPLES:
#
#   # Check if already continuing:
#   ALREADY_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active')
#   if [ "$ALREADY_ACTIVE" = "true" ]; then
#     exit 0  # Don't trigger again
#   fi
#
#   # Make Claude continue (e.g., run tests):
#   echo "Please run the test suite" >&2
#   exit 2
#
#   # Let Claude stop normally:
#   exit 0

INPUT=$(cat)

# Default: let Claude stop
exit 0

# TODO: Add your hook logic here
# Use this to auto-run tests, linters, or other checks when Claude finishes

exit 0
"""


def _get_session_start_template(hook_name: str, description: str) -> str:
    """Generate SessionStart event template."""
    return f"""#!/bin/bash
# {hook_name} - {description}
#
# INPUT JSON SCHEMA:
# {{
#   "session_id": "string",
#   "transcript_path": "string",
#   "permission_mode": "default|plan|acceptEdits|bypassPermissions",
#   "hook_event_name": "SessionStart",
#   "source": "startup|resume|clear|compact"
# }}
#
# OUTPUT JSON SCHEMA:
# {{
#   "hookSpecificOutput": {{
#     "hookEventName": "SessionStart",
#     "additionalContext": "string (optional - injected into Claude's initial context)"
#   }},
#   "continue": true|false (optional, default: true),
#   "stopReason": "string (optional)",
#   "suppressOutput": true|false (optional, default: false),
#   "systemMessage": "string (optional)"
# }}
#
# EXIT CODES:
#   0 - Normal success (stdout added as context for Claude)
#   2 - Show stderr to user only
#   Other - Error condition
#
# ENVIRONMENT VARIABLES:
#   CLAUDE_ENV_FILE - Path to file for persisting env vars across sessions
#
# EXAMPLES:
#
#   # Inject git status on startup:
#   if [ "$(echo "$INPUT" | jq -r '.source')" = "startup" ]; then
#     GIT_STATUS=$(git status --short 2>/dev/null || echo "Not a git repo")
#     echo '{{"hookSpecificOutput": {{"hookEventName": "SessionStart", "additionalContext": "Git status:\\n'"$GIT_STATUS"'"}}}}'
#   fi
#
#   # Different behavior based on source:
#   SOURCE=$(echo "$INPUT" | jq -r '.source')
#   case "$SOURCE" in
#     startup) echo "Fresh session started" ;;
#     resume)  echo "Session resumed" ;;
#     clear)   echo "Session cleared" ;;
#     compact) echo "Context compacted" ;;
#   esac

INPUT=$(cat)

# Default: do nothing
echo '{{}}'

# TODO: Add your hook logic here
# Use this to inject initial context (git status, env vars, project info)

exit 0
"""


def _get_precompact_template(hook_name: str, description: str) -> str:
    """Generate PreCompact event template."""
    return f"""#!/bin/bash
# {hook_name} - {description}
#
# INPUT JSON SCHEMA:
# {{
#   "session_id": "string",
#   "transcript_path": "string",
#   "cwd": "string",
#   "permission_mode": "default|plan|acceptEdits|bypassPermissions",
#   "hook_event_name": "PreCompact"
# }}
#
# OUTPUT JSON SCHEMA:
# {{
#   "hookSpecificOutput": {{
#     "hookEventName": "PreCompact",
#     "permissionDecision": "allow|deny|ask"
#   }},
#   "continue": true|false (optional, default: true),
#   "stopReason": "string (optional)",
#   "suppressOutput": true|false (optional, default: false),
#   "systemMessage": "string (optional)"
# }}
#
# EXIT CODES:
#   0 - Normal success (allow compaction)
#   2 - Block compaction and show stderr to user
#   Other - Error condition
#
# EXAMPLES:
#
#   # Save transcript snapshot before compaction:
#   TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path')
#   TRANSCRIPT_NAME=$(basename "$TRANSCRIPT_PATH" .jsonl)
#   SNAPSHOT_DIR="$HOME/.claude/snapshots/$TRANSCRIPT_NAME"
#   mkdir -p "$SNAPSHOT_DIR"
#   tail -n 1000 "$TRANSCRIPT_PATH" > "$SNAPSHOT_DIR/precompact_$(date +%Y%m%d-%H%M%S).txt"
#
#   # Always allow compaction (default behavior):
#   echo '{{"hookSpecificOutput": {{"hookEventName": "PreCompact", "permissionDecision": "allow"}}}}'

INPUT=$(cat)

# Extract transcript path
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // empty')

# Always allow compaction
echo '{{"hookSpecificOutput": {{"hookEventName": "PreCompact", "permissionDecision": "allow"}}}}'

# TODO: Add your hook logic here
# Example: Save snapshot of transcript before compaction
# if [ -n "$TRANSCRIPT_PATH" ] && [ -f "$TRANSCRIPT_PATH" ]; then
#   TRANSCRIPT_NAME=$(basename "$TRANSCRIPT_PATH" .jsonl)
#   SNAPSHOT_DIR="$HOME/.claude/snapshots/$TRANSCRIPT_NAME"
#   mkdir -p "$SNAPSHOT_DIR" 2>/dev/null
#   tail -n 1000 "$TRANSCRIPT_PATH" > "$SNAPSHOT_DIR/precompact_$(date +%Y%m%d-%H%M%S).txt" 2>/dev/null
# fi

exit 0
"""


def _get_snapshot_template(hook_name: str, description: str) -> str:
    """Generate snapshot hook template (PreToolUse variant for periodic snapshots)."""
    return f"""#!/bin/bash
# {hook_name} - {description}
#
# This hook triggers on every tool use. You can use it to periodically
# save conversation snapshots based on message count or time.
#
# INPUT JSON SCHEMA:
# {{
#   "session_id": "string",
#   "transcript_path": "string",
#   "cwd": "string",
#   "permission_mode": "default|plan|acceptEdits|bypassPermissions",
#   "hook_event_name": "PreToolUse",
#   "tool_name": "string",
#   "tool_input": {{}}
# }}
#
# OUTPUT JSON SCHEMA:
# {{
#   "hookSpecificOutput": {{
#     "hookEventName": "PreToolUse",
#     "permissionDecision": "allow|deny|ask"
#   }},
#   "continue": true|false (optional, default: true),
#   "stopReason": "string (optional)",
#   "suppressOutput": true|false (optional, default: false),
#   "systemMessage": "string (optional)"
# }}
#
# EXIT CODES:
#   0 - Normal success (always allow tool execution)
#   Other - Error condition
#
# EXAMPLES:
#
#   # Save snapshot every 100 messages:
#   TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path')
#   MESSAGE_COUNT=$(wc -l < "$TRANSCRIPT_PATH" 2>/dev/null | tr -d ' ' || echo "0")
#
#   if [ "$MESSAGE_COUNT" -gt 0 ] && [ $((MESSAGE_COUNT % 100)) -eq 0 ]; then
#     TRANSCRIPT_NAME=$(basename "$TRANSCRIPT_PATH" .jsonl)
#     SNAPSHOT_DIR="$HOME/.claude/snapshots/$TRANSCRIPT_NAME"
#     mkdir -p "$SNAPSHOT_DIR"
#     START=$((MESSAGE_COUNT - 100))
#     tail -n 100 "$TRANSCRIPT_PATH" > "$SNAPSHOT_DIR/message_${{START}}-${{MESSAGE_COUNT}}.txt"
#   fi

INPUT=$(cat)

# Always allow tool execution (this is non-blocking)
echo '{{"hookSpecificOutput": {{"hookEventName": "PreToolUse", "permissionDecision": "allow"}}}}'

# Extract transcript path
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // empty')

# Exit if no transcript
if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
  exit 0
fi

# TODO: Add your snapshot logic here
# Example: Save snapshot every 100 messages
# MESSAGE_COUNT=$(wc -l < "$TRANSCRIPT_PATH" 2>/dev/null | tr -d ' ' || echo "0")
#
# if [ "$MESSAGE_COUNT" -gt 0 ] && [ $((MESSAGE_COUNT % 100)) -eq 0 ]; then
#   TRANSCRIPT_NAME=$(basename "$TRANSCRIPT_PATH" .jsonl)
#   SNAPSHOT_DIR="$HOME/.claude/snapshots/$TRANSCRIPT_NAME"
#   mkdir -p "$SNAPSHOT_DIR" 2>/dev/null
#   START=$((MESSAGE_COUNT > 100 ? MESSAGE_COUNT - 100 : 0))
#   tail -n 100 "$TRANSCRIPT_PATH" > "$SNAPSHOT_DIR/message_${{START}}-${{MESSAGE_COUNT}}.txt" 2>/dev/null &
# fi

exit 0
"""


def _get_generic_template(hook_name: str, description: str) -> str:
    """Generate generic template for unknown event types."""
    return f"""#!/bin/bash
# {hook_name} - {description}

INPUT=$(cat)

# Default response
echo '{{}}'

# TODO: Add your hook logic here
# Input available in $INPUT variable
# Parse with: echo "$INPUT" | jq -r '.field'

exit 0
"""


def get_script_template(hook_name: str) -> str:
    """Generate bash script template for a hook.

    Args:
        hook_name: Name of the hook (e.g., 'on_edit')

    Returns:
        Bash script content as string
    """
    config = HOOK_CONFIG[hook_name]
    description_raw = config["description"]
    event_raw = config["event"]

    # Type assertions for pyright
    assert isinstance(description_raw, str)
    assert isinstance(event_raw, str)

    description: str = description_raw
    event: str = event_raw

    # Generate event-specific documentation
    if event == "PreToolUse":
        # Special case for snapshot hook
        if hook_name == "on_snapshot":
            return _get_snapshot_template(hook_name, description)
        return _get_pre_tool_use_template(hook_name, description)
    elif event == "PostToolUse":
        return _get_post_tool_use_template(hook_name, description)
    elif event == "UserPromptSubmit":
        return _get_user_prompt_submit_template(hook_name, description)
    elif event == "Stop":
        return _get_stop_template(hook_name, description)
    elif event == "SessionStart":
        return _get_session_start_template(hook_name, description)
    elif event == "PreCompact":
        return _get_precompact_template(hook_name, description)
    else:
        # Fallback for any unknown event types
        return _get_generic_template(hook_name, description)


def create_hook_script(hook_name: str, hooks_dir: Path) -> Path:
    """Create hook script file.

    Args:
        hook_name: Name of the hook
        hooks_dir: Path to .claude/hooks directory

    Returns:
        Path to created script file
    """
    script_path = hooks_dir / f"{hook_name}.sh"
    script_content = get_script_template(hook_name)

    script_path.write_text(script_content)
    script_path.chmod(0o755)

    return script_path


def read_settings(settings_path: Path) -> dict[str, Any]:
    """Read settings.local.json file.

    Args:
        settings_path: Path to settings.local.json

    Returns:
        Parsed JSON as dict
    """
    if not settings_path.exists():
        return {}

    return json.loads(settings_path.read_text())


def write_settings(settings_path: Path, settings: dict[str, Any]) -> None:
    """Write settings to settings.local.json file.

    Args:
        settings_path: Path to settings.local.json
        settings: Settings dict to write
    """
    settings_path.write_text(json.dumps(settings, indent=2) + "\n")


def update_hooks_config(
    settings: dict[str, Any], hook_name: str, script_path: Path
) -> dict[str, Any]:
    """Update settings with new hook configuration.

    Args:
        settings: Current settings dict
        hook_name: Name of hook being added
        script_path: Path to hook script

    Returns:
        Updated settings dict
    """
    config = HOOK_CONFIG[hook_name]
    event = config["event"]
    matcher = config["matcher"]

    # Ensure hooks key exists
    if "hooks" not in settings:
        settings["hooks"] = {}

    # Ensure event key exists
    if event not in settings["hooks"]:
        settings["hooks"][event] = []

    # Get hooks list for this event - pyright: ignore[reportUnknownVariableType]
    event_hooks = settings["hooks"][event]  # pyright: ignore[reportUnknownVariableType]
    if not isinstance(event_hooks, list):
        settings["hooks"][event] = []
        event_hooks = []

    # Build hook entry with relative path
    # Convert absolute path to relative from cwd
    try:
        relative_path = script_path.relative_to(Path.cwd())
    except ValueError:
        # Fallback to absolute if can't make relative
        relative_path = script_path

    hook_entry: dict[str, Any] = {
        "hooks": [
            {
                "type": "command",
                "command": str(relative_path),
            }
        ]
    }

    # Add matcher if needed
    if matcher is not None:
        hook_entry["matcher"] = matcher

    # Check if hook already exists
    for existing_any in event_hooks:  # pyright: ignore[reportUnknownVariableType]
        if not isinstance(existing_any, dict):
            continue
        existing: dict[str, Any] = existing_any  # type: ignore[assignment]
        if matcher is not None:
            if existing.get("matcher") == matcher:
                print(f"Hook {hook_name} already exists in settings")
                return settings
        else:
            # For hooks without matchers, check command (use relative path for comparison)
            existing_hooks_raw = existing.get("hooks", [])
            if isinstance(existing_hooks_raw, list):
                for h_any in existing_hooks_raw:  # pyright: ignore[reportUnknownVariableType]
                    if isinstance(h_any, dict):
                        h: dict[str, Any] = h_any  # type: ignore[assignment]
                        if h.get("command") == str(relative_path):
                            print(f"Hook {hook_name} already exists in settings")
                            return settings

    # Add hook entry
    event_hooks_list: list[Any] = cast(list[Any], settings["hooks"][event])
    event_hooks_list.append(hook_entry)

    return settings


def add_hook(hook_name: str) -> None:
    """Add a hook to the project.

    Args:
        hook_name: Name of hook to add (e.g., 'on_edit')
    """
    if hook_name not in HOOK_CONFIG:
        raise ValueError(f"Unknown hook: {hook_name}")

    # Find project root (.claude directory)
    cwd = Path.cwd()
    claude_dir = cwd / ".claude"

    if not claude_dir.exists():
        raise FileNotFoundError(
            "No .claude directory found in current directory. "
            "Are you in a Claude Code project?"
        )

    # Create hooks directory
    hooks_dir = claude_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    # Create hook script
    script_path = create_hook_script(hook_name, hooks_dir)
    print(f"Created hook script: {script_path}")

    # Update settings.local.json
    settings_path = claude_dir / "settings.local.json"
    settings = read_settings(settings_path)
    settings = update_hooks_config(settings, hook_name, script_path)
    write_settings(settings_path, settings)

    config = HOOK_CONFIG[hook_name]
    event = config["event"]
    matcher = config["matcher"]

    print("Added hook to settings.local.json")
    print(f"  Event: {event}")
    if matcher:
        print(f"  Matcher: {matcher}")
    print(f"\nEdit {script_path} to customize hook behavior")


def install_all_hooks() -> None:
    """Install all available hooks at once."""
    print("Installing all available hooks...\n")

    for hook_name in HOOK_CONFIG:
        print(f"Installing {hook_name}...")
        try:
            add_hook(hook_name)
            print()
        except Exception as e:
            print(f"Failed to install {hook_name}: {e}\n")

    print("All hooks installed!")

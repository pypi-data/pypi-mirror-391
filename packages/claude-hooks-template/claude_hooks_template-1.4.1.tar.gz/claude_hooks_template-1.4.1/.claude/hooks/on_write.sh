#!/bin/bash
# on_write - Triggers after Write tool completes
#
# INPUT JSON SCHEMA:
# {
#   "session_id": "string",
#   "transcript_path": "string",
#   "cwd": "string",
#   "permission_mode": "default|plan|acceptEdits|bypassPermissions",
#   "hook_event_name": "PostToolUse",
#   "tool_name": "string (e.g., 'Edit', 'Write', 'TodoWrite')",
#   "tool_input": {} (tool-specific parameters that were used),
#   "tool_response": {} (tool-specific response/result)
# }
#
# OUTPUT JSON SCHEMA:
# {
#   "decision": "block|undefined (optional)",
#   "reason": "string (required if decision is 'block')",
#   "hookSpecificOutput": {
#     "hookEventName": "PostToolUse",
#     "additionalContext": "string (optional - added to Claude's context)"
#   },
#   "continue": true|false (optional, default: true),
#   "stopReason": "string (optional)",
#   "suppressOutput": true|false (optional, default: false),
#   "systemMessage": "string (optional)"
# }
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
#   echo '{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "Modified: '"$FILE_PATH"'"}}'
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
echo '{}'

# TODO: Add your hook logic here
# Tool has already executed - you can only add context or run side effects
# (e.g., run linter, update docs, send notification)

exit 0

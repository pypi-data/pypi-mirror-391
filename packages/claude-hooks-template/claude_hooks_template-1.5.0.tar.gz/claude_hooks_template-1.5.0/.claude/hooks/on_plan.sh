#!/bin/bash
# on_plan - Triggers before ExitPlanMode tool executes
#
# INPUT JSON SCHEMA:
# {
#   "session_id": "string",
#   "transcript_path": "string",
#   "cwd": "string",
#   "permission_mode": "default|plan|acceptEdits|bypassPermissions",
#   "hook_event_name": "PreToolUse",
#   "tool_name": "string (e.g., 'Read', 'Edit', 'Bash')",
#   "tool_input": {} (tool-specific parameters)
# }
#
# OUTPUT JSON SCHEMA:
# {
#   "hookSpecificOutput": {
#     "hookEventName": "PreToolUse",
#     "permissionDecision": "allow|deny|ask",
#     "permissionDecisionReason": "string (optional)",
#     "updatedInput": {} (optional - modify tool parameters)
#   },
#   "continue": true|false (optional, default: true),
#   "stopReason": "string (optional)",
#   "suppressOutput": true|false (optional, default: false),
#   "systemMessage": "string (optional)"
# }
#
# EXIT CODES:
#   0 - Normal success (allow tool execution)
#   2 - Block tool execution and show stderr to Claude
#   Other - Error condition
#
# EXAMPLES:
#
#   # Allow tool execution:
#   echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}'
#
#   # Block tool execution:
#   echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Restricted file"}}'
#
#   # Modify tool input (e.g., change file path):
#   MODIFIED_INPUT=$(echo "$INPUT" | jq '.tool_input.file_path = "/new/path"')
#   echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow", "updatedInput": '"$MODIFIED_INPUT"'}}'
#
#   # Parse specific fields:
#   TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')
#   FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
#   CWD=$(echo "$INPUT" | jq -r '.cwd')

INPUT=$(cat)

# Default: allow tool execution
echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}'

# TODO: Add your hook logic here
# Input available in $INPUT variable
# Parse fields with jq as shown in examples above

exit 0

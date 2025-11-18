#!/bin/bash
# on_stop - Triggers when agent stops responding
#
# INPUT JSON SCHEMA:
# {
#   "session_id": "string",
#   "transcript_path": "string",
#   "permission_mode": "default|plan|acceptEdits|bypassPermissions",
#   "hook_event_name": "Stop",
#   "stop_hook_active": true|false (indicates if already continuing from previous stop)
# }
#
# OUTPUT JSON SCHEMA:
# {
#   "decision": "block|undefined (optional)",
#   "reason": "string (required if decision is 'block')",
#   "continue": true|false (optional, default: true),
#   "stopReason": "string (optional)",
#   "suppressOutput": true|false (optional, default: false),
#   "systemMessage": "string (optional)"
# }
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

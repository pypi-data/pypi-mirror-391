#!/bin/bash
# on_user_prompt - Triggers when user submits a prompt
#
# INPUT JSON SCHEMA:
# {
#   "session_id": "string",
#   "transcript_path": "string",
#   "cwd": "string",
#   "permission_mode": "default|plan|acceptEdits|bypassPermissions",
#   "hook_event_name": "UserPromptSubmit",
#   "prompt": "string (the user's submitted prompt)"
# }
#
# OUTPUT JSON SCHEMA:
# {
#   "decision": "block|undefined (optional)",
#   "reason": "string (shown to user if blocked)",
#   "hookSpecificOutput": {
#     "hookEventName": "UserPromptSubmit",
#     "additionalContext": "string (optional - injected into Claude's context)"
#   },
#   "continue": true|false (optional, default: true),
#   "stopReason": "string (optional)",
#   "suppressOutput": true|false (optional, default: false),
#   "systemMessage": "string (optional)"
# }
#
# EXIT CODES:
#   0 - Normal success (can inject context via stdout OR JSON additionalContext)
#   2 - Block prompt and erase from context, show stderr to user
#   Other - Error condition
#
# EXAMPLES:
#
#   # Inject additional context:
#   echo '{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "Current git branch: main"}}'
#
#   # Block prompt:
#   echo '{"decision": "block", "reason": "Prompt contains restricted content"}}'
#   exit 2
#
#   # Parse user's prompt:
#   USER_PROMPT=$(echo "$INPUT" | jq -r '.prompt')
#
#   # Check for keywords:
#   if echo "$USER_PROMPT" | grep -q "forbidden"; then
#     echo '{"decision": "block", "reason": "Forbidden keyword detected"}}'
#     exit 2
#   fi

INPUT=$(cat)

# Default: do nothing, let prompt through
echo '{}'

# TODO: Add your hook logic here
# Use this to inject context (git status, env vars, etc.) or validate prompts

exit 0

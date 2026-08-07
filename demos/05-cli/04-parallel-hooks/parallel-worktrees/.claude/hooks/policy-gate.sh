#!/usr/bin/env bash
INPUT=$(cat)
# Claude sends the pending tool call as JSON on stdin, this pulls out the command
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# \b marks a word boundary and \s+ one or more spaces, so this matches rm -rf as a whole word
if echo "$COMMAND" | grep -Eq '\brm\s+-rf\b'; then
  echo "Policy gate: rm -rf is blocked." >&2
  # exit 2 is the only code that blocks the call, any other non-zero code just warns
  exit 2
fi
exit 0

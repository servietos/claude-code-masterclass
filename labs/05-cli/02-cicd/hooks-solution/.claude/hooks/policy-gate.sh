#!/usr/bin/env bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

if echo "$COMMAND" | grep -E '\brm\s+-rf\b' >/dev/null; then
  echo "Policy gate: rm -rf is blocked." >&2
  exit 2
fi

if echo "$COMMAND" | grep -E '\bgit\s+push\s+.*--force\b' >/dev/null; then
  echo "Policy gate: force push is blocked." >&2
  exit 2
fi

exit 0

#!/usr/bin/env bash

# resolve the hook next to this script so the check works from any directory
HOOK="$(dirname "$0")/.claude/hooks/policy-gate.sh"

# the same JSON the harness pipes into a PreToolUse hook, sent by hand instead of by a session
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /tmp/test-dir"}}' | "$HOOK"
# $? is the exit code of the command that just ran, 2 means the call was blocked
echo "blocked command exit code: $?"

echo '{"tool_name":"Bash","tool_input":{"command":"npm test"}}' | "$HOOK"
echo "allowed command exit code: $?"

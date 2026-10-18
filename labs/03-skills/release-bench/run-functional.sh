#!/usr/bin/env bash
HERE="$(cd "$(dirname "$0")" && pwd)"
PROMPT="${1:?pass the prompt as the first argument}"
OUT="${2:-$HERE/tests/functional-run.md}"
mkdir -p "$(dirname "$OUT")"

# Plain text output so the saved file is the answer itself; the same denied tools as the trigger sweep keep the project unchanged.
(cd "$HERE" && claude -p "$PROMPT" --strict-mcp-config \
  --disallowedTools Edit Write NotebookEdit Bash PowerShell < /dev/null) | tee "$OUT"

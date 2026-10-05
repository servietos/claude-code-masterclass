#!/usr/bin/env bash
set -euo pipefail

payload=$(cat)

# CLAUDE_PLUGIN_DATA is exported to hook processes only, so :- falls back to a path derived from where this script sits
data_dir="${CLAUDE_PLUGIN_DATA:-$(dirname "$0")/../.metrics}"
mkdir -p "$data_dir"
log_path="$data_dir/tool-usage.jsonl"

timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
# claude sends the finished tool call as json on stdin, and jq's // supplies the fallback when a field is absent
session_id=$(printf '%s' "$payload" | jq -r '.session_id // ""')
tool_name=$(printf '%s' "$payload" | jq -r '.tool_name // ""')
tool_input=$(printf '%s' "$payload" | jq -c '.tool_input // {}')
duration_ms=$(printf '%s' "$payload" | jq -r '.duration_ms // 0')
is_error=$(printf '%s' "$payload" | jq -r '.is_error // false')
cwd=$(printf '%s' "$payload" | jq -r '.cwd // ""')

# --arg quotes a value as a string, --argjson keeps it as raw json so the object, number and boolean stay typed
jq -nc \
  --arg timestamp "$timestamp" \
  --arg session_id "$session_id" \
  --arg tool_name "$tool_name" \
  --argjson tool_input "$tool_input" \
  --argjson duration_ms "$duration_ms" \
  --argjson is_error "$is_error" \
  --arg cwd "$cwd" \
  '{timestamp:$timestamp, session_id:$session_id, tool_name:$tool_name, tool_input:$tool_input, duration_ms:$duration_ms, is_error:$is_error, cwd:$cwd}' \
  >> "$log_path"

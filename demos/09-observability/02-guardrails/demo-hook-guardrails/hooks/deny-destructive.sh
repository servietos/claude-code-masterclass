#!/usr/bin/env bash
set -uo pipefail

# the hook inherits the agent's working directory, so the log path is derived from the script's own location
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
log_path="$script_dir/blocked.log"

deny() {
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}' "$1"
  # exit 0 with this JSON on stdout is the deny verdict, exit 2 also blocks but throws the reason away
  exit 0
}

# Claude sends the pending tool call as JSON on stdin
payload=$(cat)

if ! command -v jq >/dev/null 2>&1; then
  deny "Guardrail hook cannot run: jq is not installed. Install jq, then retry."
fi

if ! command=$(printf '%s' "$payload" | jq -r '.tool_input.command // empty' 2>/dev/null); then
  deny "Guardrail hook could not parse the tool payload."
fi

if [[ -z "$command" ]]; then
  exit 0
fi

# [[:space:]] is a whitespace class and {2} a repeat count, so -[rf]{2} matches both -rf and -fr
patterns=(
  '(^|[[:space:];&|(])rm[[:space:]]+-[rf]{2}([[:space:]]|$)'
  'Remove-Item.*(-Recurse.*-Force|-Force.*-Recurse)'
  'git[[:space:]]+push[[:space:]].*--force'
  'git[[:space:]]+push[[:space:]].*-f([[:space:]]|$)'
  'git[[:space:]]+reset[[:space:]]+--hard'
  ':\(\)[[:space:]]*\{[[:space:]]*:\|:&[[:space:]]*\}'
)

reasons=(
  'recursive forced rm'
  'recursive forced Remove-Item'
  'git push --force'
  'git push -f'
  'git reset --hard'
  'fork bomb signature'
)

for i in "${!patterns[@]}"; do
  if [[ "$command" =~ ${patterns[$i]} ]]; then
    { printf '%s BLOCKED (%s): %s\n' "$(date +%Y-%m-%dT%H:%M:%S%:z)" "${reasons[$i]}" "$command" >> "$log_path"; } 2>/dev/null || true
    deny "Destructive command rejected by guardrail hook: ${reasons[$i]}. Logged to hooks/blocked.log."
  fi
done

exit 0

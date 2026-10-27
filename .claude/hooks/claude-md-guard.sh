#!/bin/bash
# PostToolUse hook: keep CLAUDE.md short. Detail belongs in a skill, not here.
# Exit 2 feeds stderr back to the model as blocking feedback; exit 0 stays silent.

MAX_LINES=90

file=$(jq -r '.tool_response.filePath // .tool_input.file_path // empty' 2>/dev/null)
[ -z "$file" ] && exit 0
[ "$(basename "$file")" = "CLAUDE.md" ] || exit 0
[ -f "$file" ] || exit 0

lines=$(wc -l < "$file")

if [ "$lines" -gt "$MAX_LINES" ]; then
  cat >&2 <<EOF
CLAUDE.md is now $lines lines (cap $MAX_LINES). It is a router, not a manual.
Move the detail you just added into the skill that owns it and leave a one-line pointer:
- demo / presenter / lab guide rules -> the create-class skill, leaf references/create-guide.md
- writing and voice rules            -> .claude/skills/brand-voice-code/references/rules.md
- slide rules                        -> the create-pptx skill and the /create-repo-pptx command
- anything else procedural           -> a skill under .claude/skills/
Keep only: repo purpose, folder layout, one-line rules, harness delegation.
EOF
  exit 2
fi

exit 0

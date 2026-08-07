#!/bin/bash
# PostToolUse hook: the topic lists in the course index and every module readme stay scannable.
# Each bullet is a label of at most 6 words, never a sentence. Detail belongs in the Topics table.
# Exit 2 feeds stderr back to the model as blocking feedback; exit 0 stays silent.

MAX_WORDS=6

file=$(jq -r '.tool_response.filePath // .tool_input.file_path // empty' 2>/dev/null)
[ -z "$file" ] && exit 0
# normalize Windows separators so the path test sees one form
norm=${file//\\//}

if [[ "$norm" =~ /demos/[Rr]eadme\.md$ ]]; then
  # course index: every bullet in the file belongs to a module's topic list
  stop_at_heading=0
elif [[ "$norm" =~ /demos/[^/]+/[Rr]eadme\.md$ ]]; then
  # module readme: the head list only, so Knowledge Check answer options stay exempt
  stop_at_heading=1
else
  exit 0
fi
[ -f "$file" ] || exit 0

# Backticks are stripped so a code span counts as the one word a reader sees,
# not as three whitespace-separated tokens.
offenders=$(awk -v max="$MAX_WORDS" -v stop="$stop_at_heading" '
  /^## / { if (stop) exit; next }
  /^- / {
    line = $0
    gsub(/`/, "", line)
    n = split(line, w, " ") - 1
    if (n > max) printf "  %d words: %s\n", n, $0
  }
' "$file")

if [ -n "$offenders" ]; then
  cat >&2 <<EOF
$(basename "$(dirname "$file")")/$(basename "$file") has topic bullets over $MAX_WORDS words:
$offenders
That list is a scannable index, not prose. Rewrite each one as a 4-6 word label
and let the Topics table below carry the explanation.
EOF
  exit 2
fi

exit 0

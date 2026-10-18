#!/usr/bin/env bash
HERE="$(cd "$(dirname "$0")" && pwd)"
PROMPTS="${1:-$HERE/tests/trigger-prompts.tsv}"
# One session per repeat; loading is a model decision, so a single run is an anecdote.
REPEATS="${REPEATS:-3}"

printf '| # | Expected | Fires | Observed | Verdict | Prompt |\n|---|---|---|---|---|---|\n'

n=0
# IFS is a literal tab so a prompt containing spaces stays one field.
while IFS=$'\t' read -r expected prompt; do
  n=$((n + 1))
  fires=0

  for _ in $(seq "$REPEATS"); do
    # --strict-mcp-config starts no MCP servers; --disallowedTools removes every tool that could edit the project.
    # < /dev/null keeps claude from reading the rest of the prompt file from the loop's stdin.
    # The grep counts only a load of release-notes, so any other skill that fires is ignored.
    if (cd "$HERE" && claude -p "$prompt" --output-format stream-json --verbose \
          --strict-mcp-config \
          --disallowedTools Edit Write NotebookEdit Bash PowerShell \
          < /dev/null) \
       | grep -q '"skill":"release-notes"'; then
      fires=$((fires + 1))
    fi
  done

  # The majority decides the row; the raw count stays visible so 2/3 never reads as a clean pass.
  if [ $((fires * 2)) -gt "$REPEATS" ]; then observed=fire; else observed=no-fire; fi
  if [ "$observed" = "$expected" ]; then verdict=pass; else verdict="**FAIL**"; fi

  printf '| %s | %s | %s/%s | %s | %s | %s |\n' \
    "$n" "$expected" "$fires" "$REPEATS" "$observed" "$verdict" "$prompt"
done < "$PROMPTS"

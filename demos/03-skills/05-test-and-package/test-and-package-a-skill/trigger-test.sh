#!/usr/bin/env bash
HERE="$(cd "$(dirname "$0")" && pwd)"
PROMPTS="${1:-$HERE/trigger-prompts.tsv}"
# One session per repeat. Loading is not deterministic, so a single run is an anecdote.
REPEATS="${REPEATS:-3}"

printf '| # | Expected | Fires | Observed | Verdict | Prompt |\n|---|---|---|---|---|---|\n'

n=0
# IFS is set to a literal tab so a prompt containing spaces stays one field.
while IFS=$'\t' read -r expected prompt; do
  n=$((n + 1))
  fires=0

  for _ in $(seq "$REPEATS"); do
    # Each session starts in this project, so "my changes" means these files. Plan mode is what
    # keeps the sweep read-only: a --disallowedTools list did not stop the authoring prompts from
    # writing into the project, and denying every tool instead would leave the skill as the only
    # move a session has, which biases the very thing being measured.
    # < /dev/null is load-bearing: without it claude inherits this loop's stdin, which is the prompt
    # file, and consumes the rows the loop has not read yet.
    if (cd "$HERE" && claude -p "$prompt" --output-format stream-json --verbose \
          --strict-mcp-config --permission-mode plan \
          < /dev/null) \
       | grep -q '"name":"Skill"'; then
      fires=$((fires + 1))
    fi
  done

  # Majority decides the row; the raw count stays visible so a 2/3 never reads as a clean pass.
  if [ $((fires * 2)) -gt "$REPEATS" ]; then observed=fire; else observed=no-fire; fi
  if [ "$observed" = "$expected" ]; then verdict=pass; else verdict="**FAIL**"; fi

  printf '| %s | %s | %s/%s | %s | %s | %s |\n' \
    "$n" "$expected" "$fires" "$REPEATS" "$observed" "$verdict" "$prompt"
done < "$PROMPTS"

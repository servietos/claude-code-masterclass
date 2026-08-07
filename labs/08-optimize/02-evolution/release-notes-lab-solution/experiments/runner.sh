#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RUNS="${RUNS:-3}"
BASE_REV="${BASE_REV:-}"
PROMPT="${PROMPT:-Run the release-notes skill}"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="experiments/runs"
METRICS="${METRICS:-metrics.json}"

mkdir -p "$OUT_DIR"

START_REF=""
if [ -n "$BASE_REV" ]; then
  if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "abort: working tree is dirty, BASE_REV checkout would drop your skill edits" >&2
    exit 1
  fi
  START_REF="$(git rev-parse --abbrev-ref HEAD)"
  if [ "$START_REF" = "HEAD" ]; then
    START_REF="$(git rev-parse HEAD)"
  fi
  git checkout --quiet --detach "$(git rev-parse --verify "$BASE_REV")" || exit 1
fi
MEASURED_SHA="$(git rev-parse HEAD)"

aborted=0
sections_present=0
merge_commits_included=0
outputs=""

for i in $(seq 1 "$RUNS"); do
  raw="$OUT_DIR/$STAMP-$i.json"
  md="$OUT_DIR/$STAMP-$i.md"
  claude -p "$PROMPT" --output-format json >"$raw" 2>"$OUT_DIR/$STAMP-$i.err"
  status=$?

  if [ "$status" -ne 0 ]; then
    aborted=$((aborted + 1))
    : >"$md"
    continue
  fi

  is_error="$(jq -r '.is_error // false' "$raw")"
  jq -r '.result // ""' "$raw" >"$md"

  if [ "$is_error" = "true" ] || [ ! -s "$md" ]; then
    aborted=$((aborted + 1))
    continue
  fi

  if grep -q '^# Version' "$md" && grep -q '^## Features' "$md" && grep -q '^## Fixes' "$md"; then
    sections_present=$((sections_present + 1))
  fi

  if grep -qi 'merge' "$md"; then
    merge_commits_included=$((merge_commits_included + 1))
  fi

  outputs="$outputs $md"
done

identical_outputs="$(
  for f in $outputs; do
    if [ -s "$f" ]; then
      git hash-object "$f"
    fi
  done | sort | uniq -c | awk '{ pairs += $1 * ($1 - 1) / 2 } END { print pairs + 0 }'
)"

cat >"$METRICS" <<JSON
{
  "measured_rev": "$MEASURED_SHA",
  "run_count": $RUNS,
  "identical_outputs": $identical_outputs,
  "sections_present": $sections_present,
  "merge_commits_included": $merge_commits_included,
  "aborted_runs": $aborted
}
JSON

if [ -n "$START_REF" ]; then
  git checkout --quiet "$START_REF"
fi

cat "$METRICS"

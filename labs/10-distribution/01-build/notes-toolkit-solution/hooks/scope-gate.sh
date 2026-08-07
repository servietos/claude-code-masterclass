#!/usr/bin/env bash
set -euo pipefail

payload=$(cat)

file_path=$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty')
project_dir=$(printf '%s' "$payload" | jq -r '.cwd // empty')
[ -n "$project_dir" ] || project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"

[ -n "$file_path" ] || exit 0

normalise() {
  printf '%s' "$1" | tr '\\' '/' | sed 's#//*#/#g'
}

file_path=$(normalise "$file_path")
project_dir=$(normalise "$project_dir")

case "$file_path" in
  /*|[A-Za-z]:/*)
    rel="${file_path#"$project_dir"}"
    if [ "$rel" = "$file_path" ]; then
      rel=""
    else
      rel="${rel#/}"
    fi
    ;;
  *)
    rel="${file_path#./}"
    ;;
esac

if [ -z "$rel" ]; then
  echo "scope-gate: blocked write outside the project: $file_path" >&2
  exit 2
fi

case "$rel" in
  *..*)
    echo "scope-gate: blocked path traversal: $rel" >&2
    exit 2
    ;;
esac

case "$rel" in
  .notes/*|src/*|tests/*|.claude/*|README.md)
    exit 0
    ;;
esac

echo "scope-gate: blocked write to '$rel'. Allowed: .notes/, src/, tests/, .claude/, README.md" >&2
exit 2

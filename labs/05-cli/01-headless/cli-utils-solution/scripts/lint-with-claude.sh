#!/usr/bin/env bash
set -euo pipefail

OUT=$(claude -p "Read src/slugify.ts and src/kebab-to-camel.ts. Look for: (1) unused exports, (2) missing JSDoc on exported functions, (3) any function over 30 lines. If you find ANY issue, end your response with the exact token: LINT_FAIL. If everything is clean, end with LINT_PASS." --output-format text)

echo "$OUT"

if grep -q "LINT_FAIL" <<< "$OUT"; then
  echo "claude-lint: issues found" >&2
  exit 1
fi

if grep -q "LINT_PASS" <<< "$OUT"; then
  exit 0
fi

echo "claude-lint: indeterminate output, neither LINT_PASS nor LINT_FAIL found" >&2
exit 2

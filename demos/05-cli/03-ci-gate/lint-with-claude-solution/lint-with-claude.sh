#!/usr/bin/env bash
# run from the script's own folder, so prompt.txt and src/ resolve wherever CI calls it from
cd "$(dirname "$0")"

echo "Running Claude headless..."
# < /dev/null keeps claude from waiting on stdin when nobody is at the terminal
OUTPUT=$(claude -p "$(cat prompt.txt)" --tools "Read,Glob,Grep" --max-turns 10 < /dev/null)
echo "$OUTPUT"

# the exit code is the CI contract: 1 fails the build, 0 passes it, 2 says the run was unusable
if echo "$OUTPUT" | grep -q "LINT_FAIL"; then
  echo "LINT_FAIL found. Build blocked."
  exit 1
elif echo "$OUTPUT" | grep -q "LINT_PASS"; then
  echo "LINT_PASS found. Build approved."
  exit 0
else
  echo "Indeterminate outcome."
  exit 2
fi

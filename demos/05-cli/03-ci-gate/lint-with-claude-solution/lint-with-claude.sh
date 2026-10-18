#!/usr/bin/env bash
# Run from this script's folder so src/, test/ and prompt.txt resolve
cd "$(dirname "$0")" || exit 2
# Headless audit with read-only tools; the response is captured so the verdict token can be matched
output=$(claude -p "$(cat prompt.txt)" --tools "Read,Glob,Grep" --max-turns 10)
status=$?
printf '%s\n' "$output"
# A non-zero exit (including hitting the turn cap) means the run produced no verdict
if [ "$status" -ne 0 ]; then
  exit 2
fi
pass=0
fail=0
# Match each verdict token anywhere in the response
printf '%s' "$output" | grep -q 'LINT_PASS' && pass=1
printf '%s' "$output" | grep -q 'LINT_FAIL' && fail=1
# Exactly one token is a verdict; zero or both is an outcome the gate cannot act on
if [ "$pass$fail" = "10" ]; then
  exit 0
fi
if [ "$pass$fail" = "01" ]; then
  exit 1
fi
exit 2

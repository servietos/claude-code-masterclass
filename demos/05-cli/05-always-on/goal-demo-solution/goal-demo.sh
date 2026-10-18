#!/usr/bin/env bash

# the goal condition lives in its own file, so the prompt below stays one readable line
GOAL=$(cat "$(dirname "$0")/goal-condition.txt")

# --max-turns bounds the loop, --output-format json makes the run machine readable
# < /dev/null keeps claude from waiting on stdin, jq keeps the three fields worth showing
claude -p "Keep working until this goal is met.

$GOAL" \
  --allowed-tools "Read,Edit,Bash(npm:*)" \
  --permission-mode acceptEdits \
  --max-turns 15 \
  --output-format json < /dev/null | jq '{result: .result, turns: .num_turns, cost: .total_cost_usd}'

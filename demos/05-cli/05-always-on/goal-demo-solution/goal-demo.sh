#!/usr/bin/env bash

GOAL=$(cat "$(dirname "$0")/goal-condition.txt")

claude -p "Keep working until this goal is met.

$GOAL" \
  --allowed-tools "Read,Edit,Bash(npm:*)" \
  --permission-mode acceptEdits \
  --max-turns 15 \
  --output-format json < /dev/null | jq '{result: .result, turns: .num_turns, cost: .total_cost_usd}'

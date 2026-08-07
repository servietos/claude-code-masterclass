#!/usr/bin/env pwsh

# the goal condition lives in its own file, -Raw reads it as one string instead of a line array
$Goal = Get-Content (Join-Path $PSScriptRoot 'goal-condition.txt') -Raw

# --max-turns bounds the loop, --output-format json makes the run machine readable
# the backtick is PowerShell's line continuation
claude -p "Keep working until this goal is met.

$Goal" `
    --allowed-tools "Read,Edit,Bash(npm:*)" `
    --permission-mode acceptEdits `
    --max-turns 15 `
    --output-format json |
    # this pipeline is the PowerShell equivalent of the jq filter in the Bash twin
    ConvertFrom-Json |
    Select-Object @{ Name = 'result'; Expression = { $_.result } },
                  @{ Name = 'turns'; Expression = { $_.num_turns } },
                  @{ Name = 'cost'; Expression = { $_.total_cost_usd } } |
    ConvertTo-Json

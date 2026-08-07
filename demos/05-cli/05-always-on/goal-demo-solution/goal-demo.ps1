#!/usr/bin/env pwsh

$Goal = Get-Content (Join-Path $PSScriptRoot 'goal-condition.txt') -Raw

claude -p "Keep working until this goal is met.

$Goal" `
    --allowed-tools "Read,Edit,Bash(npm:*)" `
    --permission-mode acceptEdits `
    --max-turns 15 `
    --output-format json |
    ConvertFrom-Json |
    Select-Object @{ Name = 'result'; Expression = { $_.result } },
                  @{ Name = 'turns'; Expression = { $_.num_turns } },
                  @{ Name = 'cost'; Expression = { $_.total_cost_usd } } |
    ConvertTo-Json

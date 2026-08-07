#!/usr/bin/env pwsh

# $PSScriptRoot is this script's own folder, so the check works from any directory
$Hook = Join-Path $PSScriptRoot '.claude/hooks/policy-gate.ps1'

# the same JSON the harness pipes into a PreToolUse hook, sent by hand instead of by a session
'{"tool_name":"Bash","tool_input":{"command":"rm -rf /tmp/test-dir"}}' | pwsh -NoProfile -File $Hook
# $LASTEXITCODE holds the exit code of the last native command, 2 means the call was blocked
Write-Output "blocked command exit code: $LASTEXITCODE"

'{"tool_name":"Bash","tool_input":{"command":"npm test"}}' | pwsh -NoProfile -File $Hook
Write-Output "allowed command exit code: $LASTEXITCODE"

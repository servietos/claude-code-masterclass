$raw = [Console]::In.ReadToEnd()
$payload = $raw | ConvertFrom-Json
$command = $payload.tool_input.command

$rules = @(
    @{ Reason = 'recursive rm against root'; Regex = '(?<![\w-])rm\s+(?:-\w+\s+)*-\w*r\w*\s+(?:-\w+\s+)*/(?:\s|$)' },
    @{ Reason = 'recursive rm'; Regex = '(?<![\w-])rm\s+(?:-\w+\s+)*-\w*r' },
    @{ Reason = 'recursive forced Remove-Item'; Regex = '(?i)remove-item(?=[^;&|]*-recurse)(?=[^;&|]*-force)' },
    @{ Reason = 'forced git push'; Regex = 'git\s+push(?=[^;&|]*\s(?:--force\b|--force-with-lease\b|-f\b))' },
    @{ Reason = 'git reset --hard'; Regex = 'git\s+reset(?=[^;&|]*\s--hard\b)' }
)

$logPath = Join-Path $PSScriptRoot 'blocked.log'

foreach ($rule in $rules) {
    if ($command -match $rule.Regex) {
        $line = "{0} BLOCKED ({1}): {2}" -f (Get-Date -Format o), $rule.Reason, $command
        Add-Content -Path $logPath -Value $line
        $decision = @{
            hookSpecificOutput = @{
                hookEventName            = 'PreToolUse'
                permissionDecision       = 'deny'
                permissionDecisionReason = "Blocked by deny-destructive hook: $($rule.Reason)"
            }
        } | ConvertTo-Json -Compress -Depth 5
        Write-Output $decision
        exit 0
    }
}

exit 0

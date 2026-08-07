param()

function Deny([string]$Message) {
    $response = [ordered]@{
        hookSpecificOutput = [ordered]@{
            hookEventName            = 'PreToolUse'
            permissionDecision       = 'deny'
            permissionDecisionReason = $Message
        }
    } | ConvertTo-Json -Compress -Depth 5

    Write-Output $response
    # exit 0 with this JSON on stdout is the deny verdict, exit 2 also blocks but throws the reason away
    exit 0
}

# Claude sends the pending tool call as JSON on stdin
$raw = [Console]::In.ReadToEnd()

try {
    $payload = $raw | ConvertFrom-Json -ErrorAction Stop
}
catch {
    Deny 'Guardrail hook could not parse the tool payload.'
}

$command = $payload.tool_input.command

if (-not $command) {
    exit 0
}

# \s is a whitespace class and {2} a repeat count, so -[rf]{2} matches both -rf and -fr
$patterns = @(
    @{ Regex = '(^|[\s;&|(])rm\s+-[rf]{2}(\s|$)'; Reason = 'recursive forced rm' },
    # the two (?=...) lookaheads match without consuming, so the flags are accepted in either order
    @{ Regex = 'Remove-Item(?=.*-Recurse)(?=.*-Force)'; Reason = 'recursive forced Remove-Item' },
    @{ Regex = 'git\s+push\s+.*--force'; Reason = 'git push --force' },
    @{ Regex = 'git\s+push\s+.*-f(\s|$)'; Reason = 'git push -f' },
    @{ Regex = 'git\s+reset\s+--hard'; Reason = 'git reset --hard' },
    @{ Regex = ':\(\)\s*\{\s*:\|:&\s*\}'; Reason = 'fork bomb signature' }
)

foreach ($p in $patterns) {
    if ($command -match $p.Regex) {
        $log = "$(Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz') BLOCKED ($($p.Reason)): $command"
        # $PSScriptRoot is the script's own folder, so the log lands in hooks/ whatever the agent's cwd is
        $logPath = Join-Path $PSScriptRoot 'blocked.log'
        try { Add-Content -Path $logPath -Value $log -ErrorAction SilentlyContinue } catch { }

        Deny "Destructive command rejected by guardrail hook: $($p.Reason). Logged to hooks/blocked.log."
    }
}

exit 0

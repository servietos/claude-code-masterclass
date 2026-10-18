$raw = [Console]::In.ReadToEnd()
$payload = $raw | ConvertFrom-Json
$sessionId = $payload.session_id
$cap = 25

$counterPath = Join-Path $PSScriptRoot 'session-counter.txt'

$state = @{}
if (Test-Path $counterPath) {
    foreach ($line in Get-Content -Path $counterPath) {
        $parts = $line -split '\s+', 2
        if ($parts.Count -eq 2) { $state[$parts[0]] = [int]$parts[1] }
    }
}

$count = 0
if ($state.ContainsKey($sessionId)) { $count = $state[$sessionId] }
$count = $count + 1
$state[$sessionId] = $count

Set-Content -Path $counterPath -Value ($state.Keys | ForEach-Object { "$_ $($state[$_])" })

if ($count -gt $cap) {
    $decision = @{
        hookSpecificOutput = @{
            hookEventName            = 'PreToolUse'
            permissionDecision       = 'deny'
            permissionDecisionReason = "Tool call budget exceeded ($cap). Stop and ask the user for direction."
        }
    } | ConvertTo-Json -Compress -Depth 5
    Write-Output $decision
    exit 0
}

exit 0

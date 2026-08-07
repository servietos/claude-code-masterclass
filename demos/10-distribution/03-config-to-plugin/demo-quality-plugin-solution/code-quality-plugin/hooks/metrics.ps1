param()

# claude sends the finished tool call as json on stdin, and ReadToEnd blocks until it has all of it
$payload = [Console]::In.ReadToEnd() | ConvertFrom-Json

$dataDir = $env:CLAUDE_PLUGIN_DATA
if (-not $dataDir) {
    # CLAUDE_PLUGIN_DATA is exported to hook processes only, so the fallback derives a path from $PSScriptRoot, this script's own folder
    $dataDir = Join-Path $PSScriptRoot '..' '.metrics'
}
if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
}

$logPath = Join-Path $dataDir 'tool-usage.jsonl'

$record = [ordered]@{
    timestamp     = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    session_id    = $payload.session_id
    tool_name     = $payload.tool_name
    tool_input    = $payload.tool_input
    duration_ms   = [int]$payload.duration_ms
    is_error      = [bool]$payload.is_error
    cwd           = $payload.cwd
}

# -Compress keeps the record on one line for jsonl, and without -Depth the default of 2 flattens nested tool_input to a type name
$line = ($record | ConvertTo-Json -Compress -Depth 6)
Add-Content -Path $logPath -Value $line -Encoding utf8

# a non-zero exit from a hook is reported back as a hook failure, so a metrics writer always ends on 0
exit 0

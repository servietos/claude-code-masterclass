param(
    [Parameter(Mandatory)][string]$Prompt,
    [string]$Out = (Join-Path $PSScriptRoot "tests\functional-run.md")
)
New-Item -ItemType Directory -Force (Split-Path $Out) | Out-Null

Push-Location $PSScriptRoot
# Plain text output so the saved file is the answer itself; piping $null closes stdin.
$null | claude -p $Prompt --strict-mcp-config `
    --disallowedTools Edit Write NotebookEdit Bash PowerShell | Tee-Object -FilePath $Out
Pop-Location

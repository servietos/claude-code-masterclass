# $PSScriptRoot is the script's own folder, so the run works from anywhere.
param(
    [string]$Prompts = (Join-Path $PSScriptRoot "tests\trigger-prompts.tsv"),
    # One session per repeat; loading is a model decision, so a single run is an anecdote.
    [int]$Repeats = 3
)

"| # | Expected | Fires | Observed | Verdict | Prompt |"
"|---|---|---|---|---|---|"

$n = 0
foreach ($line in Get-Content $Prompts) {
    $n++
    # Split on the first tab only, so a prompt containing a tab stays intact.
    $expected, $prompt = $line -split "`t", 2
    $fires = 0

    foreach ($i in 1..$Repeats) {
        Push-Location $PSScriptRoot
        # Piping $null closes stdin; without it claude waits for console input.
        # --strict-mcp-config starts no MCP servers; --disallowedTools removes every tool that could edit the project.
        $out = $null | claude -p $prompt --output-format stream-json --verbose `
            --strict-mcp-config `
            --disallowedTools Edit Write NotebookEdit Bash PowerShell | Out-String
        Pop-Location

        # -cmatch is case-sensitive and the pattern names release-notes, so any other skill that fires is ignored.
        if ($out -cmatch '"skill":"release-notes"') { $fires++ }
    }

    # The majority decides the row; the raw count stays visible so 2/3 never reads as a clean pass.
    $observed = if ($fires * 2 -gt $Repeats) { "fire" } else { "no-fire" }
    $verdict = if ($observed -eq $expected) { "pass" } else { "**FAIL**" }

    "| $n | $expected | $fires/$Repeats | $observed | $verdict | $prompt |"
}

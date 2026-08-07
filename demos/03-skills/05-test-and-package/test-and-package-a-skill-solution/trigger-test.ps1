# $PSScriptRoot is the script's own folder, so the run works from anywhere.
param(
    [string]$Prompts = (Join-Path $PSScriptRoot "trigger-prompts.tsv"),
    # One session per repeat. Loading is not deterministic, so a single run is an anecdote.
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
        # Each session starts in this project, so "my changes" means these files. Only the mutating
        # tools are denied: the session still reads and searches like a real one, but cannot edit the
        # project, and leaving the read tools in place keeps Skill from being the only move it has.
        Push-Location $PSScriptRoot
        # Piping $null closes stdin; without it claude inherits the console and waits for input.
        $out = $null | claude -p $prompt --output-format stream-json --verbose `
            --strict-mcp-config `
            --disallowedTools Edit Write NotebookEdit Bash PowerShell | Out-String
        Pop-Location

        # -cmatch is case-sensitive; plain -match would also accept the word "skill" in prose.
        if ($out -cmatch '"name":"Skill"') { $fires++ }
    }

    # Majority decides the row; the raw count stays visible so a 2/3 never reads as a clean pass.
    $observed = if ($fires * 2 -gt $Repeats) { "fire" } else { "no-fire" }
    $verdict = if ($observed -eq $expected) { "pass" } else { "**FAIL**" }

    "| $n | $expected | $fires/$Repeats | $observed | $verdict | $prompt |"
}

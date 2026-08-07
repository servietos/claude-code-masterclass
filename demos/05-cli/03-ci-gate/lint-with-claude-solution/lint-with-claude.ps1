#!/usr/bin/env pwsh
# run from the script's own folder, so prompt.txt and src/ resolve wherever CI calls it from
Set-Location $PSScriptRoot

Write-Output "Running Claude headless..."
# Out-String joins the streamed output lines into one string the checks below can search
$Output = claude -p (Get-Content prompt.txt -Raw) --tools "Read,Glob,Grep" --max-turns 10 | Out-String
Write-Output $Output

# -cmatch is case sensitive, so a lowercase mention of the marker cannot trip the gate
# the exit code is the CI contract: 1 fails the build, 0 passes it, 2 says the run was unusable
if ($Output -cmatch 'LINT_FAIL') {
    Write-Output "LINT_FAIL found. Build blocked."
    exit 1
}
elseif ($Output -cmatch 'LINT_PASS') {
    Write-Output "LINT_PASS found. Build approved."
    exit 0
}
else {
    Write-Output "Indeterminate outcome."
    exit 2
}

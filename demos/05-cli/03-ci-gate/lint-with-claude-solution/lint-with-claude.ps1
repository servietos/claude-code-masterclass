#!/usr/bin/env pwsh
# Run from this script's folder so src/, test/ and prompt.txt resolve
Set-Location $PSScriptRoot
# Headless audit with read-only tools; the response is captured so the verdict token can be matched
$output = claude -p (Get-Content prompt.txt -Raw) --tools "Read,Glob,Grep" --max-turns 10 | Out-String
$status = $LASTEXITCODE
Write-Output $output
# A non-zero exit (including hitting the turn cap) means the run produced no verdict
if ($status -ne 0) {
    exit 2
}
# Match verdict tokens case-sensitively anywhere in the response
$pass = $output -cmatch 'LINT_PASS'
$fail = $output -cmatch 'LINT_FAIL'
# Exactly one token is a verdict; zero or both is an outcome the gate cannot act on
if ($pass -and -not $fail) {
    exit 0
}
if ($fail -and -not $pass) {
    exit 1
}
exit 2

# the default sits outside the checkout so the course repo's own CLAUDE.md never loads into the run, pass a path to override it
param([string]$RunDir = "$HOME\spec-runs\meeting-cost")

# $PSScriptRoot is the folder holding this script, so the copy source resolves from any working directory
$TopicDir = $PSScriptRoot

New-Item -ItemType Directory -Force (Split-Path $RunDir) | Out-Null
# copies only when the run folder is missing, so a second run keeps the work from the first
if (-not (Test-Path $RunDir)) { Copy-Item -Recurse "$TopicDir\meeting-cost" $RunDir }

# -ErrorAction SilentlyContinue returns nothing for a missing uv, so the if reads as a presence test
if (Get-Command uv -ErrorAction SilentlyContinue) {
  # the version pin matches the recorded outputs; --reinstall replaces an older specify-cli that would otherwise stay put
  uv tool install specify-cli==1.2.1 --reinstall
} else {
  pipx install --force specify-cli==1.2.1
}

Set-Location $RunDir
# --force lets init run in a folder that already holds the starter, --non-interactive stops it waiting for a keypress
specify init . --integration claude --script ps --force --non-interactive

Write-Output "Spec Kit ready in $RunDir"
Write-Output "Start the demo with: cd $RunDir; claude"

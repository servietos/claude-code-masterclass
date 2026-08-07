# the default sits outside the checkout because spec kit initialises its own git repo, pass a path to override it
param([string]$RunDir = "$HOME\spec-runs\notes-cli-speckit")

# $PSScriptRoot is the folder holding this script, so the copy source resolves from any working directory
$TopicDir = $PSScriptRoot

New-Item -ItemType Directory -Force (Split-Path $RunDir) | Out-Null
# copies only when the run folder is missing, so a second run keeps the work from the first
if (-not (Test-Path $RunDir)) { Copy-Item -Recurse "$TopicDir\notes-cli" $RunDir }

# -ErrorAction SilentlyContinue makes a missing uv return nothing instead of erroring, so this reads as a presence test
if (Get-Command uv -ErrorAction SilentlyContinue) {
  uv tool install --force specify-cli --from git+https://github.com/github/spec-kit.git
} else {
  pipx install --force git+https://github.com/github/spec-kit.git
}

Set-Location $RunDir
# --force lets init run in a folder that already holds the copied starter
specify init . --integration claude --script ps --force

Write-Output "Spec Kit ready in $RunDir"
Write-Output "Start the demo with: cd $RunDir; claude"

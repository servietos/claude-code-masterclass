# the default sits outside the checkout because bmad installs its own git repo, pass a path to override it
param([string]$RunDir = "$HOME\spec-runs\notes-cli-bmad")

# $PSScriptRoot is the folder holding this script, so the copy source resolves from any working directory
$TopicDir = $PSScriptRoot

New-Item -ItemType Directory -Force (Split-Path $RunDir) | Out-Null
# copies only when the run folder is missing, so a second run keeps the work from the first
if (-not (Test-Path $RunDir)) { Copy-Item -Recurse "$TopicDir\notes-cli" $RunDir }

Set-Location $RunDir
npx --yes bmad-method install --directory . --modules bmm --tools claude-code --yes

Write-Output "BMAD ready in $RunDir"
Write-Output "Start the demo with: cd $RunDir; claude"

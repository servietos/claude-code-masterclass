#Requires -Version 5.1

[CmdletBinding()]
param(
    [switch]$SkipDocker,
    [switch]$SkipVSCode,
    [switch]$SkipExtensions,
    [switch]$SkipBrowser,
    [switch]$VerifyOnly
)

$ErrorActionPreference = 'Continue'

$repoRoot = Split-Path -Parent $PSScriptRoot
$devcontainerJson = Join-Path $repoRoot '.devcontainer/devcontainer.json'
$hugoVersion = '0.128.0'

function Write-Step {
    param([string]$Text)
    Write-Host ''
    Write-Host "==> $Text" -ForegroundColor Cyan
}

function Write-Skip {
    param([string]$Text)
    Write-Host "    already present: $Text" -ForegroundColor DarkGray
}

function Update-SessionPath {
    # winget installs write to the registry, not to this process; re-read both scopes so the new exe is callable right away
    $machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $user = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = "$machine;$user"
}

function Test-Tool {
    param([string]$Command)
    return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

function Install-WingetPackage {
    param(
        [string]$Id,
        [string]$Command,
        [string]$Label,
        [string[]]$ExtraArgs = @()
    )

    if ($Command -and (Test-Tool $Command)) {
        Write-Skip $Label
        return
    }

    Write-Host "    installing $Label ($Id)"
    # --silent keeps vendor installers headless; --accept-*-agreements stops winget waiting on a prompt
    winget install --id $Id --exact --silent --accept-package-agreements --accept-source-agreements @ExtraArgs
    Update-SessionPath
}

function Get-DevcontainerExtensions {
    $raw = Get-Content $devcontainerJson -Raw
    # devcontainer.json is JSONC; ConvertFrom-Json rejects the // comment lines
    $stripped = $raw -replace '(?m)^\s*//.*$', ''
    return (ConvertFrom-Json $stripped).customizations.vscode.extensions
}

function Show-Version {
    param(
        [string]$Label,
        [string]$Command,
        [string]$Arguments
    )

    if (-not (Test-Tool $Command)) {
        Write-Host ("  {0,-16} MISSING" -f $Label) -ForegroundColor Red
        return
    }

    # 2>&1 folds stderr into the pipeline because several of these CLIs print their banner there; the Where drops az's update nag
    $output = (& $Command $Arguments.Split(' ') 2>&1 |
        Where-Object { "$_".Trim() -and "$_" -notmatch '^\s*(WARNING|NOTE)' } |
        Select-Object -First 1) -join ''
    Write-Host ("  {0,-16} {1}" -f $Label, $output.Trim()) -ForegroundColor Green
}

function Show-Verification {
    Write-Step 'Installed toolchain'
    Show-Version 'Claude Code' 'claude' '--version'
    Show-Version '.NET SDK' 'dotnet' '--version'
    Show-Version 'Node.js' 'node' '-v'
    Show-Version 'npm' 'npm' '-v'
    Show-Version 'Python' 'python' '--version'
    Show-Version 'uv' 'uv' '--version'
    Show-Version 'Java' 'java' '-version'
    Show-Version 'Maven' 'mvn' '-v'
    Show-Version 'Hugo' 'hugo' 'version'
    Show-Version 'Terraform' 'terraform' '-version'
    Show-Version 'Azure CLI' 'az' '--version'
    Show-Version 'azd' 'azd' 'version'
    Show-Version 'GitHub CLI' 'gh' '--version'
    Show-Version 'Docker' 'docker' '--version'
    Show-Version 'PowerShell 7' 'pwsh' '--version'
    Show-Version 'Git' 'git' '--version'
    Show-Version 'VS Code' 'code' '--version'
}

if ($VerifyOnly) {
    Show-Verification
    return
}

Write-Host 'Agentic Software Engineering with Claude Code: Windows setup' -ForegroundColor White
Write-Host "Repository: $repoRoot" -ForegroundColor DarkGray

if (-not (Test-Tool 'winget')) {
    Write-Host 'winget not found. Install "App Installer" from the Microsoft Store, then re-run this script.' -ForegroundColor Red
    return
}

Write-Step 'Core runtimes'
Install-WingetPackage -Id 'Git.Git' -Command 'git' -Label 'Git'
Install-WingetPackage -Id 'Microsoft.DotNet.SDK.10' -Command 'dotnet' -Label '.NET 10 SDK'
Install-WingetPackage -Id 'OpenJS.NodeJS.LTS' -Command 'node' -Label 'Node.js 22 LTS'
Install-WingetPackage -Id 'Python.Python.3.12' -Command 'python' -Label 'Python 3.12'
Install-WingetPackage -Id 'astral-sh.uv' -Command 'uv' -Label 'uv'
Install-WingetPackage -Id 'Microsoft.OpenJDK.21' -Command 'java' -Label 'Microsoft OpenJDK 21'
Install-WingetPackage -Id 'Apache.Maven' -Command 'mvn' -Label 'Maven'
Install-WingetPackage -Id 'Microsoft.PowerShell' -Command 'pwsh' -Label 'PowerShell 7'

Write-Step 'Cloud and DevOps tooling'
Install-WingetPackage -Id 'Microsoft.AzureCLI' -Command 'az' -Label 'Azure CLI'
Install-WingetPackage -Id 'Microsoft.Azd' -Command 'azd' -Label 'Azure Developer CLI'
Install-WingetPackage -Id 'Hashicorp.Terraform' -Command 'terraform' -Label 'Terraform'
Install-WingetPackage -Id 'GitHub.cli' -Command 'gh' -Label 'GitHub CLI'
Install-WingetPackage -Id 'Hugo.Hugo.Extended' -Command 'hugo' -Label "Hugo Extended $hugoVersion" -ExtraArgs @('--version', $hugoVersion)

if ($SkipDocker) {
    Write-Host '    skipping Docker Desktop (-SkipDocker)' -ForegroundColor DarkGray
}
else {
    Install-WingetPackage -Id 'Docker.DockerDesktop' -Command 'docker' -Label 'Docker Desktop'
}

if ($SkipVSCode) {
    Write-Host '    skipping VS Code (-SkipVSCode)' -ForegroundColor DarkGray
}
else {
    Install-WingetPackage -Id 'Microsoft.VisualStudioCode' -Command 'code' -Label 'Visual Studio Code'
}

Write-Step 'Claude Code CLI'
if (Test-Tool 'npm') {
    npm install -g @anthropic-ai/claude-code
    Update-SessionPath
}
else {
    Write-Host '    npm not on PATH yet. Open a new terminal and re-run this script.' -ForegroundColor Yellow
}

Write-Step 'Bicep CLI'
if (Test-Tool 'az') {
    az bicep install
}

if ($SkipBrowser) {
    Write-Step 'Playwright browser (skipped)'
}
else {
    Write-Step 'Playwright browser for the playwright and chrome-devtools MCP servers'
    npx --yes playwright install chrome
}

if ($SkipExtensions -or $SkipVSCode) {
    Write-Step 'VS Code extensions (skipped)'
}
elseif (Test-Tool 'code') {
    Write-Step 'VS Code extensions from .devcontainer/devcontainer.json'
    $installed = (code --list-extensions) -join "`n"
    foreach ($extension in Get-DevcontainerExtensions) {
        # the marketplace id is case-insensitive but `code --list-extensions` prints the publisher's own casing
        if ($installed -imatch [regex]::Escape($extension)) {
            Write-Skip $extension
            continue
        }
        Write-Host "    installing $extension"
        code --install-extension $extension --force
    }
}

Show-Verification

Write-Step 'Next steps'
Write-Host '  1. Open a new terminal so every PATH entry is picked up.'
Write-Host '  2. Start Docker Desktop once and let it finish its first-run setup.'
Write-Host "  3. cd $repoRoot"
Write-Host '  4. Run claude and sign in.'
Write-Host '  5. Open any starter under demos/, labs/ or src/ and follow its guide.'
Write-Host ''
Write-Host '  Re-check the toolchain at any time with: pwsh ./scripts/install-class-windows.ps1 -VerifyOnly'

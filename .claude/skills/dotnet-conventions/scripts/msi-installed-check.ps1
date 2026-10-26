<#
.SYNOPSIS
  Check whether an MSI-installed desktop app is the build you just made, without touching Windows Installer.

.DESCRIPTION
  A rebuilt MSI with an unchanged version does not upgrade: it registers a second product of the same
  name and version and Windows Installer keeps the existing equal-version files, so the installed app
  runs old code after a "successful" reinstall. This reads the Uninstall registry keys (never
  Win32_Product, whose query reconfigures every installed MSI) and compares the installed files with a
  build folder (the wixproj's publish folder, or any folder holding the same files) by SHA256.

  Read-only: it never installs, repairs or removes anything.

.EXAMPLE
  pwsh -File msi-installed-check.ps1 -ProductName "Audio Star" -InstallDir "C:\Program Files\Audio Star" -BuildDir .\src\App.Setup\obj\publish
  pwsh -File msi-installed-check.ps1 -ProductName "Presenter Tools" -InstallDir "C:\Program Files\Presenter Tools" -BuildDir .\src\PresenterTools.Setup\obj\publish -Include "PresenterTools*.dll","PresenterTools.exe"

.OUTPUTS
  One line per registered product and per differing file, then a summary line:
  products=<n> duplicates=<n> compared=<n> differing=<n> missing=<n> verdict=current|stale|duplicate|not-installed
  Exit code 0 only for verdict=current.
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)] [string] $ProductName,
  [Parameter(Mandatory)] [string] $InstallDir,
  [Parameter(Mandatory)] [string] $BuildDir,
  [string[]] $Include = @('*.dll', '*.exe')
)

$ErrorActionPreference = 'Stop'

$roots = @(
  'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
  'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
  'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*'
)
$products = @(foreach ($root in $roots) {
  Get-ItemProperty $root -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -eq $ProductName }
})
foreach ($p in $products) {
  "product name=`"$($p.DisplayName)`" version=$($p.DisplayVersion) code=$($p.PSChildName) installed=$($p.InstallDate)"
}
$duplicates = @($products | Group-Object DisplayVersion | Where-Object Count -gt 1 | ForEach-Object { $_.Count - 1 } | Measure-Object -Sum).Sum
if (-not $duplicates) { $duplicates = 0 }

$compared = 0; $differing = 0; $missing = 0
if (Test-Path $InstallDir) {
  $build = Get-ChildItem -Path (Join-Path $BuildDir '*') -Include $Include -File
  foreach ($file in $build) {
    $compared++
    $installed = Join-Path $InstallDir $file.Name
    if (-not (Test-Path $installed)) {
      $missing++
      "missing file=$($file.Name)"
      continue
    }
    if ((Get-FileHash $installed).Hash -ne (Get-FileHash $file.FullName).Hash) {
      $differing++
      $i = Get-Item $installed
      "differs file=$($file.Name) installed=$($i.VersionInfo.FileVersion)@$($i.LastWriteTime.ToString('s')) build=$($file.VersionInfo.FileVersion)@$($file.LastWriteTime.ToString('s'))"
    }
  }
}

$verdict = if ($products.Count -eq 0 -or -not (Test-Path $InstallDir)) { 'not-installed' }
  elseif ($duplicates -gt 0) { 'duplicate' }
  elseif ($differing -gt 0 -or $missing -gt 0) { 'stale' }
  else { 'current' }

"products=$($products.Count) duplicates=$duplicates compared=$compared differing=$differing missing=$missing verdict=$verdict"
if ($verdict -ne 'current') { exit 1 }

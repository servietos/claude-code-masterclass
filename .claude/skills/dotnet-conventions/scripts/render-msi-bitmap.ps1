<#
.SYNOPSIS
  Render an HTML page to a 24-bit BMP for a WiX/MSI Bitmap control, at a chosen scale.

.DESCRIPTION
  MSI dialogs can show only a bitmap plus native controls, so a branded screen paints its scene and
  copy into one picture. This renders that picture from a scratch HTML page with headless Edge (so web
  fonts and CSS work) and converts the screenshot to the 24-bit BMP the MSI Bitmap control expects.
  Draw at -Scale 2 so the dialog stays sharp at 150 percent display scaling; the 1x size is the
  control's size in pixels at 96 dpi (one dialog unit is about 1.333 px, so the stock 370 x 234 unit
  area is 493 x 312).

  Edge runs with its own throwaway profile, so a running Edge window is never touched.

.EXAMPLE
  pwsh -File render-msi-bitmap.ps1 -Html .\start.html -Width 613 -Height 387 -Out ..\Assets\start.bmp
  pwsh -File render-msi-bitmap.ps1 -Html .\exit.html -Width 493 -Height 312 -Out .\exit.bmp -DryRun

.OUTPUTS
  One summary line: bitmap=<path> width=<px> height=<px> bpp=24 bytes=<n>
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)] [string] $Html,
  [Parameter(Mandatory)] [int] $Width,
  [Parameter(Mandatory)] [int] $Height,
  [Parameter(Mandatory)] [string] $Out,
  [double] $Scale = 2,
  [string] $Edge,
  [switch] $DryRun
)
$ErrorActionPreference = 'Stop'

if (-not $Edge) {
  $Edge = @(
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"
  ) | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $Edge -or -not (Test-Path $Edge)) { throw 'msedge.exe not found; pass -Edge <path>' }

$htmlPath = (Resolve-Path $Html).Path
$outPath = [System.IO.Path]::GetFullPath($Out)
$expectedW = [int][math]::Round($Width * $Scale)
$expectedH = [int][math]::Round($Height * $Scale)
$work = Join-Path ([System.IO.Path]::GetTempPath()) ("msi-bmp-" + [guid]::NewGuid().ToString('N'))
$png = Join-Path $work 'shot.png'
$uri = ([System.Uri]$htmlPath).AbsoluteUri

$edgeArgs = @(
  '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check',
  "--user-data-dir=$(Join-Path $work 'profile')",
  "--force-device-scale-factor=$Scale",
  "--window-size=$Width,$Height",
  "--screenshot=$png",
  $uri
)

if ($DryRun) {
  "dry-run edge=`"$Edge`" args=$($edgeArgs -join ' ') out=$outPath expected=${expectedW}x$expectedH"
  return
}

New-Item -ItemType Directory -Force $work | Out-Null
try {
  $p = Start-Process -FilePath $Edge -ArgumentList $edgeArgs -PassThru -WindowStyle Hidden
  if (-not $p.WaitForExit(60000)) { $p.Kill(); throw 'headless Edge did not finish within 60 s' }
  if (-not (Test-Path $png)) { throw "Edge wrote no screenshot ($png)" }

  Add-Type -AssemblyName System.Drawing
  $src = [System.Drawing.Image]::FromFile($png)
  try {
    if ($src.Width -ne $expectedW -or $src.Height -ne $expectedH) {
      throw "screenshot is $($src.Width)x$($src.Height), expected ${expectedW}x$expectedH (check -Width/-Height/-Scale and the page size)"
    }
    $bmp = New-Object System.Drawing.Bitmap $src.Width, $src.Height, ([System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
    try {
      $g = [System.Drawing.Graphics]::FromImage($bmp)
      $g.DrawImage($src, 0, 0, $src.Width, $src.Height)
      $g.Dispose()
      New-Item -ItemType Directory -Force (Split-Path $outPath) | Out-Null
      $bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Bmp)
    } finally { $bmp.Dispose() }
  } finally { $src.Dispose() }
} finally {
  Remove-Item -Recurse -Force $work -ErrorAction SilentlyContinue
}

$bytes = (Get-Item $outPath).Length
"bitmap=$outPath width=$expectedW height=$expectedH bpp=24 bytes=$bytes"

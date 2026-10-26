<#
.SYNOPSIS
  Puts a before and an after screenshot side by side (before left, after right) in one PNG.

.EXAMPLE
  pwsh -NoProfile -File wpf-shot-compare.ps1 -Before .\before\Home.png -After .\after\Home.png -Out .\compare\Home.png
  # out=.\compare\Home.png width=3850 height=1230
#>
param(
    [Parameter(Mandatory)] [string] $Before,
    [Parameter(Mandatory)] [string] $After,
    [Parameter(Mandatory)] [string] $Out,
    # px of separator between the two shots
    [int] $Gap = 10
)

Add-Type -AssemblyName System.Drawing
$a = [System.Drawing.Image]::FromFile((Resolve-Path $Before))
$b = [System.Drawing.Image]::FromFile((Resolve-Path $After))
$bmp = New-Object System.Drawing.Bitmap ($a.Width + $Gap + $b.Width), ([Math]::Max($a.Height, $b.Height))
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.Clear([System.Drawing.Color]::Gray)
$g.DrawImage($a, 0, 0, $a.Width, $a.Height)
$g.DrawImage($b, $a.Width + $Gap, 0, $b.Width, $b.Height)
$g.Dispose()
$dir = Split-Path -Parent $Out
if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
"out=$Out width=$($bmp.Width) height=$($bmp.Height)"
$bmp.Dispose(); $a.Dispose(); $b.Dispose()

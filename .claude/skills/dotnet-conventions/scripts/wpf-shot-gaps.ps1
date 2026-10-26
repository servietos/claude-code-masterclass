<#
.SYNOPSIS
  Measures the left and right gap between a content area's edges and its outermost ink in
  PrintWindow screenshots, so "equal margins" is checked in pixels instead of by eye.

.DESCRIPTION
  For every PNG (one file or every *.png in a folder) the script scans the columns from
  -ContentLeft to the content area's right edge between rows -Top and -Bottom, treats every pixel
  that differs from the background by more than -Tolerance as ink, and reports the gap from each
  edge to the first and last ink column. A thin tall ink group within 90 px of the right edge (a
  scrollbar thumb) is ignored by default and reported separately as rightInclScrollbar.

  Measure to the outermost ink, not to layout bounds: an icon glyph sits inside its button and a
  button template may inset its fill, so equal layout margins can still look unequal.

.EXAMPLE
  pwsh -NoProfile -File wpf-shot-gaps.ps1 -Path .\after -ContentLeft 401 -Top 48 -Bottom 970
  # Appsettings  left= 42px ( 28.0 DIP)  right= 42px ( 28.0 DIP)  rightInclScrollbar=30px
  # files=13 equal=9 unequal=4 maxdiff=15px
#>
param(
    [Parameter(Mandatory)] [string] $Path,
    # x of the content area's first column, in px (for a sidebar app: the divider's x plus one)
    [Parameter(Mandatory)] [int] $ContentLeft,
    # x of the content area's last column plus one; default: image width minus -FrameRight
    [int] $ContentRight = 0,
    # px PrintWindow adds at the window's right edge (border and shadow; 11 at 150 percent)
    [int] $FrameRight = 11,
    # rows to scan: skip the title bar above and any bar below the page (a player bar, a status bar)
    [int] $Top = 0,
    [int] $Bottom = 0,
    # background colour as #RRGGBB; default: sampled at (ContentLeft + 2, Top + 2)
    [string] $Background = '',
    [int] $Tolerance = 6,
    [double] $Scale = 1.5,
    # gaps differing by no more than this many px count as equal
    [int] $EqualWithin = 2,
    [switch] $KeepScrollbar
)

Add-Type -AssemblyName System.Drawing
$files = if (Test-Path $Path -PathType Container) { Get-ChildItem -Path $Path -Filter *.png | Sort-Object Name } else { Get-Item $Path }
$count = 0; $equal = 0; $unequal = 0; $maxDiff = 0

foreach ($f in $files) {
    $bmp = [System.Drawing.Bitmap]::FromFile($f.FullName)
    $rect = New-Object System.Drawing.Rectangle 0, 0, $bmp.Width, $bmp.Height
    $data = $bmp.LockBits($rect, 'ReadOnly', 'Format32bppArgb')
    $stride = $data.Stride
    $bytes = New-Object byte[] ($stride * $bmp.Height)
    [Runtime.InteropServices.Marshal]::Copy($data.Scan0, $bytes, 0, $bytes.Length)
    $bmp.UnlockBits($data)

    $right = if ($ContentRight -gt 0) { $ContentRight } else { $bmp.Width - $FrameRight }
    $y0 = [Math]::Max(0, $Top)
    $y1 = if ($Bottom -gt 0) { [Math]::Min($Bottom, $bmp.Height) } else { $bmp.Height }

    if ($Background) {
        $c = [System.Drawing.ColorTranslator]::FromHtml($Background); $bgR = $c.R; $bgG = $c.G; $bgB = $c.B
    } else {
        $i = ($y0 + 2) * $stride + ($ContentLeft + 2) * 4; $bgB = $bytes[$i]; $bgG = $bytes[$i + 1]; $bgR = $bytes[$i + 2]
    }

    # per column: is there ink, and the longest vertical ink run (a scrollbar thumb is thin and tall)
    $groups = New-Object System.Collections.Generic.List[object]
    $cur = $null
    for ($x = $ContentLeft; $x -lt $right; $x++) {
        $run = 0; $best = 0; $any = $false
        for ($y = $y0; $y -lt $y1; $y++) {
            $i = $y * $stride + $x * 4
            if ([Math]::Abs($bytes[$i] - $bgB) -gt $Tolerance -or [Math]::Abs($bytes[$i + 1] - $bgG) -gt $Tolerance -or [Math]::Abs($bytes[$i + 2] - $bgR) -gt $Tolerance) {
                $any = $true; $run++; if ($run -gt $best) { $best = $run }
            } else { $run = 0 }
        }
        if ($any) {
            if ($cur -and $x -eq $cur.End + 1) { $cur.End = $x; if ($best -gt $cur.Run) { $cur.Run = $best } }
            else { $cur = [pscustomobject]@{ Start = $x; End = $x; Run = $best }; $groups.Add($cur) }
        }
    }
    $bmp.Dispose()
    $count++
    if ($groups.Count -eq 0) { "{0,-24} no ink between rows {1} and {2}" -f $f.BaseName, $y0, $y1; continue }

    $lastAll = $groups[$groups.Count - 1].End
    $content = if ($KeepScrollbar) { $groups } else {
        @($groups | Where-Object { -not (($_.End - $_.Start) -le 6 -and $_.Run -ge 40 -and $_.Start -gt $right - 90) })
    }
    $first = $content[0].Start
    $last = $content[$content.Count - 1].End
    $leftGap = $first - $ContentLeft
    $rightGap = $right - 1 - $last
    $diff = [Math]::Abs($leftGap - $rightGap)
    if ($diff -le $EqualWithin) { $equal++ } else { $unequal++ }
    if ($diff -gt $maxDiff) { $maxDiff = $diff }
    "{0,-24} left={1,4}px ({2,5:N1} DIP)  right={3,4}px ({4,5:N1} DIP)  rightInclScrollbar={5}px" -f $f.BaseName, $leftGap, ($leftGap / $Scale), $rightGap, ($rightGap / $Scale), ($right - 1 - $lastAll)
}
"files=$count equal=$equal unequal=$unequal maxdiff=${maxDiff}px"

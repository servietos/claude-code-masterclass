$repo = Split-Path $PSScriptRoot -Parent
$renderer = Join-Path $PSScriptRoot 'md2pdf.py'

$sources = Get-ChildItem -Path (Join-Path $repo 'demos') -Directory |
    ForEach-Object { Join-Path $_.FullName 'pdf/handout.md' } |
    Where-Object { Test-Path $_ }

foreach ($source in $sources) {
    $pdfDir = Split-Path $source -Parent
    $module = Split-Path (Split-Path $pdfDir -Parent) -Leaf
    $target = Join-Path $pdfDir "$module.pdf"

    Write-Host "Rendering $module"
    python $renderer $source $target $module

    $size = [math]::Round((Get-Item $target).Length / 1KB)
    Write-Host "  -> $target ($size KB)"
}

Write-Host "Done: $($sources.Count) PDF(s)"

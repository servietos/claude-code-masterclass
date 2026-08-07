$raw = [Console]::In.ReadToEnd()
$payload = $raw | ConvertFrom-Json

$counterPath = "hooks/session-counter.txt"
$cap = 25

$count = 0
if (Test-Path $counterPath) {
    $count = [int](Get-Content -Path $counterPath -Raw).Trim()
}
$count = $count + 1
Set-Content -Path $counterPath -Value $count

if ($count -gt $cap) {
    $out = @{
        decision = 'block'
        reason   = 'Tool call budget exceeded (25). Stop and ask the user for direction.'
    } | ConvertTo-Json -Compress
    Write-Output $out
    exit 2
}

exit 0

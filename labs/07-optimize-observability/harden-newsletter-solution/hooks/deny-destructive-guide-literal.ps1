$raw = [Console]::In.ReadToEnd()
$payload = $raw | ConvertFrom-Json
$command = $payload.tool_input.command

$rules = @(
    @{ Pattern = 'rm -rf /'; Reason = 'rm -rf against root' },
    @{ Pattern = 'rm -rf .'; Reason = 'rm -rf against current directory' },
    @{ Pattern = 'Remove-Item -Recurse -Force'; Reason = 'recursive forced Remove-Item' },
    @{ Pattern = 'git push --force'; Reason = 'forced push' },
    @{ Pattern = 'git push -f'; Reason = 'forced push (short flag)' },
    @{ Pattern = 'git reset --hard'; Reason = 'hard reset' }
)

foreach ($rule in $rules) {
    if ($command -match $rule.Pattern) {
        $line = "{0} BLOCKED ({1}): {2}" -f (Get-Date -Format o), $rule.Reason, $command
        Add-Content -Path "hooks/blocked.log" -Value $line
        $out = @{ decision = 'block'; reason = $rule.Reason } | ConvertTo-Json -Compress
        Write-Output $out
        exit 2
    }
}

exit 0

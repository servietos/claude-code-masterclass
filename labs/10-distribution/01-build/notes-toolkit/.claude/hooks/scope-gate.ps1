$payload = [Console]::In.ReadToEnd() | ConvertFrom-Json

$filePath = if ($payload.tool_input.file_path) { $payload.tool_input.file_path }
            elseif ($payload.tool_input.notebook_path) { $payload.tool_input.notebook_path }
            else { '' }

$projectDir = if ($payload.cwd) { $payload.cwd }
              elseif ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR }
              else { $PWD.Path }

if (-not $filePath) { exit 0 }

function Normalise($p) { ($p -replace '\\', '/') -replace '/{2,}', '/' }

$filePath = Normalise $filePath
$projectDir = Normalise $projectDir

if ($filePath -match '^(/|[A-Za-z]:/)') {
    $rel = ''
    if ($filePath.StartsWith($projectDir)) {
        $rel = $filePath.Substring($projectDir.Length).TrimStart('/')
    }
} else {
    $rel = $filePath -replace '^\./', ''
}

if (-not $rel) {
    [Console]::Error.WriteLine("scope-gate: blocked write outside the project: $filePath")
    exit 2
}

if ($rel -like '*..*') {
    [Console]::Error.WriteLine("scope-gate: blocked path traversal: $rel")
    exit 2
}

if ($rel -match '^(\.notes/|src/|tests/|\.claude/)' -or $rel -eq 'README.md') {
    exit 0
}

[Console]::Error.WriteLine("scope-gate: blocked write to '$rel'. Allowed: .notes/, src/, tests/, .claude/, README.md")
exit 2

param([string]$TasksFile = 'tasks.txt')

# repository root and this folder's path inside it, so every agent starts in the same folder of its worktree
$Repo = git rev-parse --show-toplevel
$DemoDir = git rev-parse --show-prefix
$Jobs = @()
$Slugs = @()

# worktrees are created beside the repository, as wt-<slug>
function Get-Worktree($slug) {
    Join-Path (Split-Path $Repo -Parent) "wt-$slug"
}

function Remove-Worktrees {
    foreach ($slug in $Slugs) {
        git worktree remove --force (Get-Worktree $slug)
    }
}

New-Item -ItemType Directory -Force logs | Out-Null

foreach ($line in Get-Content $TasksFile) {
    $slug, $desc = $line -split '\|', 2
    $Slugs += $slug
    git worktree add (Get-Worktree $slug) -b "feat/$slug"
    # Start-Job does not inherit the current folder, so the log path is made absolute here
    $Log = Join-Path $PWD "logs/log-$slug.txt"
    # the job runs in the background; its streams go to the log file and only the exit code comes back
    $job = Start-Job -ArgumentList (Get-Worktree $slug), $DemoDir, $desc, $Log -ScriptBlock {
        param($Wt, $DemoDir, $Task, $Log)
        Set-Location (Join-Path $Wt $DemoDir)
        claude -p "$Task. Add tests. Commit the result." --allowed-tools "Read,Edit,Bash(npm:*),Bash(git:*)" --max-turns 10 *> $Log
        # the last statement is the value the job emits, so the caller can read the agent's exit code
        $LASTEXITCODE
    }
    $Jobs += [pscustomobject]@{ Slug = $slug; Job = $job }
}

$failed = $false
foreach ($entry in $Jobs) {
    # -Wait blocks until the job finishes; -AutoRemoveJob deletes it once its output is read
    $code = Receive-Job -Job $entry.Job -Wait -AutoRemoveJob
    if ($code -ne 0) {
        $failed = $true
    }
}

if ($failed) {
    Remove-Worktrees
    exit 1
}

foreach ($slug in $Slugs) {
    # --no-ff keeps one merge commit per task, so each feature stays visible in history
    git merge --no-ff "feat/$slug"
    if ($LASTEXITCODE -ne 0) {
        git merge --abort
        Remove-Worktrees
        exit 1
    }
}

Remove-Worktrees
foreach ($slug in $Slugs) {
    # -d refuses to delete a branch that is not merged, so only merged feature branches go
    git branch -d "feat/$slug"
}

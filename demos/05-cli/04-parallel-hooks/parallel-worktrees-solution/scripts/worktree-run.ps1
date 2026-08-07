#!/usr/bin/env pwsh

# first argument, or tasks.txt when the script is called without one
param([string]$TasksFile = 'tasks.txt')

$Repo = git rev-parse --show-toplevel
# the path of this folder inside the repository, so each worktree can cd to the same place
$DemoDir = git rev-parse --show-prefix
$Parent = Split-Path $Repo -Parent
$Logs = Join-Path $PWD 'logs'

New-Item -ItemType Directory -Force -Path $Logs | Out-Null

$Slugs = @()

function Remove-Worktrees {
    foreach ($slug in $Slugs) {
        git worktree remove (Join-Path $Parent "wt-$slug") --force
    }
    git worktree prune
}

$Launched = @()

foreach ($line in Get-Content $TasksFile) {
    if (-not $line.Trim()) { continue }
    # split each task line into a slug and a task description on the first pipe
    $slug, $desc = $line -split '\|', 2

    $worktree = Join-Path $Parent "wt-$slug"
    Write-Output "Creating worktree $worktree on feat/$slug"
    git worktree add $worktree -b "feat/$slug"

    # Start-Job runs the session in the background, so all agents work at the same time
    $job = Start-Job -ArgumentList $worktree, $DemoDir, $desc, (Join-Path $Logs "log-$slug.txt") -ScriptBlock {
        # a job gets no variables from the caller, param() receives what -ArgumentList passed in
        param($Worktree, $Demo, $Task, $Log)
        Set-Location (Join-Path $Worktree $Demo)
        # *> redirects every output stream, including errors, into the per-agent log
        claude -p $Task --allowed-tools "Read,Edit,Bash(npm:*),Bash(git:*)" --max-turns 8 *> $Log
        # the last line of the block is what Receive-Job hands back, here the agent's exit code
        $LASTEXITCODE
    }

    $Launched += [pscustomobject]@{ Slug = $slug; Job = $job }
    $Slugs += $slug
}

Write-Output "Launched $($Launched.Count) agents, waiting..."

$Failed = @()
foreach ($entry in $Launched) {
    # -Wait blocks until this job finishes and returns the exit code the block emitted
    $code = Receive-Job -Job $entry.Job -Wait -AutoRemoveJob
    if ($code -ne 0) {
        $Failed += "$($entry.Slug) (exit $code)"
    }
}

$Branches = ($Slugs | ForEach-Object { "feat/$_" }) -join ' '

# one failed agent stops the merge, so a half-finished fan-out never lands on the branch
if ($Failed.Count -ne 0) {
    Write-Output "Agents failed, skipping merge:"
    $Failed | ForEach-Object { Write-Output "  $_" }
    Remove-Worktrees
    Write-Output "Branches kept for inspection: $Branches"
    exit 1
}

Write-Output "All agents succeeded, merging..."
foreach ($slug in $Slugs) {
    # --no-ff keeps one merge commit per agent, so each lane stays visible in the history
    git merge --no-ff "feat/$slug" -m "Merge feat/$slug"
    if ($LASTEXITCODE -ne 0) {
        Write-Output "Conflict merging feat/$slug, aborting"
        git merge --abort
        Remove-Worktrees
        Write-Output "Branches kept for inspection: $Branches"
        exit 1
    }
}

Write-Output "Cleaning up..."
Remove-Worktrees
foreach ($slug in $Slugs) {
    # lowercase -d refuses to delete a branch that was never merged
    git branch -d "feat/$slug"
}

git log --oneline --graph -10

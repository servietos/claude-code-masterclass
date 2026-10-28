#!/usr/bin/env pwsh

$RepoRoot = git rev-parse --show-toplevel
# the path of this folder inside the repository, so each worktree can cd to the same place
$DemoDir = git rev-parse --show-prefix
# worktrees are created beside the repository, never inside it
$Parent = Split-Path $RepoRoot -Parent
$FeatA = Join-Path $Parent 'wt-feat-camel'
$FeatB = Join-Path $Parent 'wt-feat-slug'

Write-Output "Creating worktrees..."
git worktree add $FeatA -b feat/improve-camel
git worktree add $FeatB -b feat/improve-slug

Write-Output "Launching parallel Claude sessions..."
# Start-Job runs the session in a background job, so both agents work at the same time
$JobA = Start-Job -ArgumentList $FeatA, $DemoDir -ScriptBlock {
    # a job gets no variables from the caller, param() receives what -ArgumentList passed in
    param($Worktree, $Demo)
    Set-Location (Join-Path $Worktree $Demo)
    # the backtick is PowerShell's line continuation
    claude -p "Improve src/kebab-to-camel.ts to handle multi-word inputs. Add tests. Commit the result." `
        --allowed-tools "Read,Edit,Bash(npm:*),Bash(git:*)" --max-turns 10
}

$JobB = Start-Job -ArgumentList $FeatB, $DemoDir -ScriptBlock {
    param($Worktree, $Demo)
    Set-Location (Join-Path $Worktree $Demo)
    claude -p "Improve src/slugify.ts to preserve numbers in slugs. Add tests. Commit the result." `
        --allowed-tools "Read,Edit,Bash(npm:*),Bash(git:*)" --max-turns 10
}

# -Wait blocks until both jobs finish, -AutoRemoveJob cleans them up afterwards
Receive-Job -Job $JobA, $JobB -Wait -AutoRemoveJob
Write-Output "Both sessions complete."

Write-Output "Resulting branches:"
git log --all --oneline -10

Write-Output "Cleaning up worktrees..."
git worktree remove $FeatA --force
git worktree remove $FeatB --force
git branch -D feat/improve-camel feat/improve-slug

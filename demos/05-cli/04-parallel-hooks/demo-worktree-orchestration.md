# Automate the full worktree lifecycle with a single shell script

A tasks file generalizes the starter's hardcoded two-agent script into a queue, where one line becomes one worktree, one branch, one agent and one log. You end holding a single repeatable command that creates the worktrees, runs the agents in parallel, joins them, merges in sequence and cleans up.

---

Start from a clean working tree in [parallel-worktrees/](parallel-worktrees); the completed script is in [parallel-worktrees-solution/](parallel-worktrees-solution) as `scripts/worktree-run.sh` and `scripts/worktree-run.ps1`.

## Step 1: Implement the Script

Use Claude to write the orchestration script from these patterns. Bash tracks background jobs by PID and joins them with `wait`, PowerShell tracks job objects and joins them with `Receive-Job -Wait`.

```text
Implement scripts/worktree-run.sh.
Use these specific patterns:
  - Capture PIDs into an array: `pids+=($!)`
  - Read tasks with: `while IFS='|' read -r slug desc; do ... done < "$TASKS_FILE"`
  - Get repo root and this folder inside it: `REPO=$(git rev-parse --show-toplevel)` and `DEMO_DIR=$(git rev-parse --show-prefix)`, then run each agent in `$WORKTREE/$DEMO_DIR`
  - Agent log output: redirect each agent's stdout and stderr to `logs/log-<slug>.txt`
  - If any agent exits non-zero, skip the merge, remove the worktrees, keep the `feat/<slug>` branches and exit 1
  - When every agent exits 0, run `git merge --no-ff feat/<slug>` for each slug in order; on a conflict run `git merge --abort`, remove the worktrees and exit 1
  - At the end, remove the worktrees and delete the merged `feat/<slug>` branches
After writing the script:
  1. Run `bash -n scripts/worktree-run.sh` to confirm there are no syntax errors.
  2. Create a sample `tasks.txt` with two entries using functions from src/ in this project. Give each entry a disjoint file scope: name the one source file and the one test file that task owns, and never let two entries name the same file.
  3. Do not run the script yet.
```

```text
Implement scripts/worktree-run.ps1.
Use these specific patterns:
  - Take the tasks file as `param([string]$TasksFile = 'tasks.txt')`
  - Read tasks with: `foreach ($line in Get-Content $TasksFile) { $slug, $desc = $line -split '\|', 2 }`
  - Launch each agent with Start-Job, passing the worktree path, the demo folder, the task and the log path in through -ArgumentList so the job's script block takes them as param()
  - Redirect all of the agent's streams inside the job with `*> $Log`, then make `$LASTEXITCODE` the last statement of the script block so the job emits it
  - Collect `[pscustomobject]@{ Slug = $slug; Job = $job }` and read each code back with `Receive-Job -Job $entry.Job -Wait -AutoRemoveJob`
  - Get repo root and this folder inside it: `$Repo = git rev-parse --show-toplevel` and `$DemoDir = git rev-parse --show-prefix`, build worktree paths with `Join-Path (Split-Path $Repo -Parent) "wt-$slug"`
  - If any agent's code is non-zero, skip the merge, remove the worktrees, keep the `feat/<slug>` branches and exit 1
  - When every agent exits 0, run `git merge --no-ff feat/<slug>` for each slug in order and test `$LASTEXITCODE` after each merge; on a conflict run `git merge --abort`, remove the worktrees and exit 1
  - At the end, remove the worktrees and delete the merged `feat/<slug>` branches
After writing the script:
  1. Parse-check it without running it:
     `$e = $null; [void][System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path scripts/worktree-run.ps1), [ref]$null, [ref]$e); $e`
  2. Create a sample `tasks.txt` with two entries using functions from src/ in this project. Give each entry a disjoint file scope: name the one source file and the one test file that task owns, and never let two entries name the same file.
  3. Do not run the script yet.
```

**Expected Outcome:** the parse check reports no syntax errors, and `tasks.txt` has two pipe-delimited entries using real functions from the starter project, each naming files the other does not touch, like the [solution's `tasks.txt`](parallel-worktrees-solution/tasks.txt).

Git isolates the lanes only physically, so the disjoint file scopes in `tasks.txt` are what keep the sequential merges from stopping half done.

## Step 2: Run and Verify the Orchestration

Execute the script against the sample tasks, read the logs, and confirm the integration branch contains both changes.

```text
Run the orchestration script:
chmod +x scripts/worktree-run.sh
./scripts/worktree-run.sh tasks.txt
When it finishes:
  1. `git log --oneline --graph -8`: confirm two merge commits appear above the original HEAD.
  2. `npm test`: confirm tests still pass after both merges.
  3. `git worktree list`: confirm no stale worktrees remain.
  4. `cat logs/log-*.txt`: read both agent logs and confirm each committed successfully.
```

```text
Run the orchestration script:
./scripts/worktree-run.ps1 tasks.txt
When it finishes:
  1. `git log --oneline --graph -8`: confirm two merge commits appear above the original HEAD.
  2. `npm test`: confirm tests still pass after both merges.
  3. `git worktree list`: confirm no stale worktrees remain.
  4. `Get-Content logs/log-*.txt`: read both agent logs and confirm each committed successfully.
```

**Expected Outcome:** Two merge commits visible in the graph log. `npm test` passes. `git worktree list` shows only the main worktree. Both log files show a successful commit message from the agent.

The script merges only when every agent succeeded, so two merge commits prove both lanes ran concurrently and finished without manual intervention.

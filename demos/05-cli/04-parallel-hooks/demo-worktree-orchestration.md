# Automate the full worktree lifecycle with a single shell script

A tasks file generalizes the starter's hardcoded two-agent script into a queue, where one line becomes one worktree, one branch, one agent and one log. You design `scripts/worktree-run.sh` (or its `.ps1` twin) as reviewed pseudocode first, implement it, then run it against `tasks.txt` and read both agent logs. You end holding a single repeatable command that creates the worktrees, runs the agents in parallel, joins them, merges in sequence and cleans up.

---

## Setup

Start from a clean working tree:

```bash
cd demos/05-cli/04-parallel-hooks/parallel-worktrees
git status
```

Bash tracks background jobs by PID and joins them with `wait`, PowerShell tracks job objects and joins them with `Receive-Job -Wait`. Each step gives both forms, and the completed script exists as `scripts/worktree-run.sh` and `scripts/worktree-run.ps1`.

---

## Step 1: Design the Orchestration Script

**Overview:** Reason through the structure of the orchestration script before writing a single line. Good upfront design prevents silent failures in parallel runs.

**Research / Planning / Discussion:**

```text
I want to write a bash script that:
  - Reads a list of tasks (one per line, in the format `branch-slug|task-description`)
  - Creates a git worktree for each task on a fresh branch
  - Launches a `claude -p` agent inside each worktree in parallel
  - Waits for all agents to finish
  - Merges each branch back in sequence
  - Removes the worktrees and branches

Before I write it, answer:

1. What does `wait` return if one of the background processes exited with a non-zero code? Should I capture individual exit codes, and if so, how?
2. How should I handle the case where `git merge --no-ff <branch>` fails due to a conflict, should the script abort immediately or attempt all merges and report failures at the end?
3. What is the safest way to remove a worktree that may have uncommitted changes, `git worktree remove` or `git worktree remove --force`?
```

PowerShell:

```text
I want to write a PowerShell script that:
  - Reads a list of tasks (one per line, in the format `branch-slug|task-description`)
  - Creates a git worktree for each task on a fresh branch
  - Launches a `claude -p` agent inside each worktree in parallel with Start-Job
  - Waits for all agents to finish
  - Merges each branch back in sequence
  - Removes the worktrees and branches

Before I write it, answer:

1. A completed job's State is "Completed" even when the command inside it exited non-zero. How do I get the real exit code of a native command out of a background job?
2. How should I handle the case where `git merge --no-ff <branch>` fails due to a conflict, should the script abort immediately or attempt all merges and report failures at the end? How do I detect that failure, given that a failing native command does not throw?
3. What is the safest way to remove a worktree that may have uncommitted changes, `git worktree remove` or `git worktree remove --force`?
```

**Finding:** In Bash, Claude should explain that `wait` returns the exit code of the last job (not the worst), and that `wait <pid>` captures individual codes. In PowerShell it should land on the same problem with a different shape: job state is not an exit code, so the script must emit `$LASTEXITCODE` as the last statement of the job's script block and read it back through `Receive-Job`, and it must test `$LASTEXITCODE` after `git merge` because a failing native command does not raise a terminating error. In both shells it should recommend aborting on the first merge failure (not silently continuing) to avoid corrupted integration branches. On cleanup, it should recommend `--force` only as an explicit fallback, not the default.

**Recipe:**

```text
Design a bash script `scripts/worktree-run.sh` with this structure:

1. Input: a tasks file path as $1, defaulting to `tasks.txt`.
   Format of each line: `slug|task description`

2. Per task: create worktree at `../wt-<slug>` next to the repository root on branch `feat/<slug>`, run claude -p from this demo folder inside that worktree with --max-turns 8 and --allowed-tools "Read,Edit,Bash(npm:*),Bash(git:*)" in the background, capture the PID.

3. After launching all tasks: iterate over the PIDs with `wait <pid>` and record any non-zero exit codes.

4. If any agent failed: print a summary of failures, remove the worktrees but keep the branches so the partial work stays inspectable, and exit 1 without merging.

5. If all agents succeeded: merge each branch with `git merge --no-ff feat/<slug> -m "Merge feat/<slug>"`. Abort with `git merge --abort` and exit 1 on the first conflict.

6. Cleanup: `git worktree remove --force ../wt-<slug>` and `git branch -d feat/<slug>` for each task.

Do not implement it yet, write the design as numbered pseudocode so I can review it first.
```

PowerShell: the same recipe, naming `scripts/worktree-run.ps1`, with two substitutions. In phase 2, launch each agent with `Start-Job` and keep the returned job object alongside its slug instead of capturing a PID. In phase 3, iterate the job objects with `Receive-Job -Wait -AutoRemoveJob` and record any non-zero code the job emitted. Phases 1, 4, 5 and 6 are plain `git` work and read identically in both shells.

**Expected Outcome:** A numbered pseudocode design (not runnable code) covering all six phases. Review it carefully: verify it captures individual PIDs, aborts on agent failure before merging, and cleans up even when merge fails.

---

## Step 2: Implement the Script

**Overview:** Translate the pseudocode design into a working bash script, using Claude to fill in the implementation details.

**Research / Planning / Discussion:**

```text
Look at worktree-parallel.sh in this folder for a reference implementation of parallel worktrees in bash.

For my orchestration script:
1. What pattern should I use to capture multiple background PIDs and check each one?
2. How do I read the slug and description from a pipe-delimited line in a bash while-read loop?
3. Which git commands give me the repository root and this folder's path inside it, so each agent starts in this folder inside its own worktree?
```

PowerShell:

```text
Look at worktree-parallel.ps1 in this folder for a reference implementation of parallel worktrees in PowerShell.

For my orchestration script:
1. What pattern should I use to collect multiple job objects and read each one's exit code back?
2. How do I split the slug and description out of a pipe-delimited line, given that `|` is the pipeline operator and has to be escaped in the regex?
3. Which git commands give me the repository root and this folder's path inside it, so each agent starts in this folder inside its own worktree?
```

**Finding:** In Bash, Claude should show the PID array pattern (`pids+=($!)` followed by `for pid in "${pids[@]}"; do wait "$pid"; ...`), the `IFS='|' read -r slug desc` pattern for pipe-delimited lines, and the pair `$(git rev-parse --show-toplevel)` plus `$(git rev-parse --show-prefix)`. In PowerShell it should show a collection of `[pscustomobject]@{ Slug = ...; Job = ... }` pairs read back with `Receive-Job -Wait`, the `$slug, $desc = $line -split '\|', 2` destructuring form with the pipe escaped and a limit of 2 so a description containing a pipe survives, and the same two `git rev-parse` calls, which need no substitution syntax because PowerShell assigns native command output directly.

**Recipe:**

```text
Implement scripts/worktree-run.sh based on the pseudocode design from Step 1.

Use these specific patterns:
  - Capture PIDs into an array: `pids+=($!)`
  - Read tasks with: `while IFS='|' read -r slug desc; do ... done < "$TASKS_FILE"`
  - Get repo root and this folder inside it: `REPO=$(git rev-parse --show-toplevel)` and `DEMO_DIR=$(git rev-parse --show-prefix)`, then run each agent in `$WORKTREE/$DEMO_DIR`
  - Agent log output: redirect each agent's stdout and stderr to `logs/log-<slug>.txt`

After writing the script:
  1. Run `bash -n scripts/worktree-run.sh` to confirm there are no syntax errors.
  2. Create a sample `tasks.txt` with two entries using functions from src/ in this project. Give each entry a disjoint file scope: name the one source file and the one test file that task owns, and never let two entries name the same file.
  3. Do not run the script yet.
```

PowerShell:

```text
Implement scripts/worktree-run.ps1 based on the pseudocode design from Step 1.

Use these specific patterns:
  - Take the tasks file as `param([string]$TasksFile = 'tasks.txt')`
  - Read tasks with: `foreach ($line in Get-Content $TasksFile) { $slug, $desc = $line -split '\|', 2 }`
  - Launch each agent with Start-Job, passing the worktree path, the demo folder, the task and the log path in through -ArgumentList so the job's script block takes them as param()
  - Redirect all of the agent's streams inside the job with `*> $Log`, then make `$LASTEXITCODE` the last statement of the script block so the job emits it
  - Collect `[pscustomobject]@{ Slug = $slug; Job = $job }` and read each code back with `Receive-Job -Job $entry.Job -Wait -AutoRemoveJob`
  - Get repo root and this folder inside it: `$Repo = git rev-parse --show-toplevel` and `$DemoDir = git rev-parse --show-prefix`, build worktree paths with `Join-Path (Split-Path $Repo -Parent) "wt-$slug"`
  - After each `git merge`, test `$LASTEXITCODE` rather than relying on an exception

After writing the script:
  1. Parse-check it without running it:

     `$e = $null; [void][System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path scripts/worktree-run.ps1), [ref]$null, [ref]$e); $e`
  2. Create a sample `tasks.txt` with two entries using functions from src/ in this project. Give each entry a disjoint file scope: name the one source file and the one test file that task owns, and never let two entries name the same file.
  3. Do not run the script yet.
```

The parse check is the PowerShell equivalent of `bash -n`: it compiles the file and reports syntax errors without executing a line. An empty `$e` is the pass signal.

Git isolates the lanes physically, not semantically, so nothing stops two agents rewriting the same function in their own worktrees. The script merges in sequence with no conflict resolution, so the second merge stops half done when the lanes overlap. That constraint lives in the task descriptions, decided before any agent starts.

**Expected Outcome:** `scripts/worktree-run.sh` or `scripts/worktree-run.ps1` exists, the parse check reports no syntax errors, and `tasks.txt` has two pipe-delimited entries using real functions from the starter project, each naming files the other does not touch. No worktrees or branches have been created yet.

---

## Step 3: Run and Verify the Orchestration

**Overview:** Execute the script against the sample tasks, read the logs, and confirm the integration branch contains both changes.

**Research / Planning / Discussion:**

```text
Before running the script:

1. What is the expected wall-clock time for two agents running in parallel versus the same two agents running sequentially?
2. If one agent commits successfully but the other fails before committing, what will the script do: merge only the successful branch, skip both, or abort?
3. After the script finishes, what single git command shows the complete merge topology of the last 10 commits?
```

**Finding:** Claude should explain that wall-clock time is roughly equal to the slower of the two agents (not their sum), that the script should abort both merges if any agent failed (per the design in Step 1), and that `git log --oneline --graph -10` shows the merge topology.

**Recipe:**

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

PowerShell:

```text
Run the orchestration script:

./scripts/worktree-run.ps1 tasks.txt

When it finishes:
  1. `git log --oneline --graph -8`: confirm two merge commits appear above the original HEAD.
  2. `npm test`: confirm tests still pass after both merges.
  3. `git worktree list`: confirm no stale worktrees remain.
  4. `Get-Content logs/log-*.txt`: read both agent logs and confirm each committed successfully.
```

There is no `chmod` step in the PowerShell path: a `.ps1` has no executable bit. If the shell refuses to run the file at all, that is the execution policy rather than a permission bit, and `pwsh -File ./scripts/worktree-run.ps1 tasks.txt` runs it without changing any machine-wide setting.

**Expected Outcome:** Two merge commits visible in the graph log. `npm test` passes. `git worktree list` shows only the main worktree. Both log files show a successful commit message from the agent. The script ran both agents concurrently and merged both results without manual intervention.

> The script design above uses sequential merges after parallel agent runs. If you want full parallelism including the merge phase, you need a more complex conflict-detection strategy.

The completed reference for this demo lives in [parallel-worktrees-solution/](parallel-worktrees-solution/).

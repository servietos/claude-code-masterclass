---
presents: demo-worktree-orchestration.md
budget: 4 min
beats: 4
---

# Present: Automate the full worktree lifecycle with a single shell script

How a hardcoded two-agent script becomes a task queue, and which three bash details decide whether a failed agent corrupts the integration branch. Four beats: one task line into a lane, the `wait` that reports the wrong exit code, keeping a failed agent out of the merge, and aborting on the first conflict.

------

**Shell:** [`scripts/worktree-run.ps1`](parallel-worktrees-solution/scripts/worktree-run.ps1) is the one script in the module where the translation is more than syntax. The PID array becomes job objects paired with slugs, and the per-PID `wait` becomes `Receive-Job -Wait -AutoRemoveJob`. Say in beat 2 that a PowerShell job reports `Completed` even when the command inside exited non-zero, so the script emits `$LASTEXITCODE` as the job's last statement.

## Beats

### Beat 1: one line of a text file becomes one worktree and one agent (1 min)

**Open:** [`tasks.txt`](parallel-worktrees-solution/tasks.txt) · [`scripts/worktree-run.sh`](parallel-worktrees-solution/scripts/worktree-run.sh) · the `while IFS='|' read` loop
**Say:** Two hardcoded lanes teach the mechanism and stop being useful at three. Separating work from machinery means adding a lane is an edit to data, and the code stays as it is.

```bash
while IFS='|' read -r slug desc; do
  slugs+=("$slug")
  # one worktree and one feat/<slug> branch per task, created beside the repository
  git worktree add "$REPO/../wt-$slug" -b "feat/$slug"
...
  pids+=($!)
done < "$TASKS_FILE"
```

**Result:** the two lines the run consumed, and the only file you edit to add a third lane

```text
kebab-camel|Improve src/kebab-to-camel.ts so kebabToCamel handles multi-word inputs. This task owns only src/kebab-to-camel.ts and test/kebab-to-camel.test.ts
slugify-numbers|Improve src/slugify.ts so slugify preserves numbers in slugs. This task owns only src/slugify.ts and test/slugify.test.ts
```

**Gotcha:** the slug names the worktree path, the branch and the log file at once, so one line of `tasks.txt` is one lane from start to finish.

### Beat 2: a bare `wait` reports success whatever the agents did (1 min)

**Open:** [`scripts/worktree-run.sh`](parallel-worktrees-solution/scripts/worktree-run.sh) · the per-PID `wait` loop
**Say:** Fanning out is the easy half; joining back is where correctness is won or lost. A join that collapses N outcomes into one number has to be checked for which number it kept.

```bash
failed=0
for pid in "${pids[@]}"; do
  # wait returns the agent's exit code; any non-zero marks the whole run as failed
  wait "$pid" || failed=1
done
```

**Result:** `failed` is 1 when any lane exited non-zero, and beat 3 branches on it. Each lane's story is in `logs/log-<slug>.txt`

**Gotcha:** a bare `wait` returns 0 whatever the agents did, so a script that calls it alone declares success even when an agent failed. That is why each PID is waited on by name.

### Beat 3: a failed agent must not reach the merge phase (1 min)

**Open:** [`scripts/worktree-run.sh`](parallel-worktrees-solution/scripts/worktree-run.sh) · the failure branch
**Say:** Merging the lanes that finished produces a branch holding half an intended change with nothing recording that it is half. That is worse than merging nothing, because it looks finished downstream.

```bash
if [ "$failed" -ne 0 ]; then
  remove_worktrees
  exit 1
fi
```

**Result:** `exit 1` before any merge, the worktrees removed and every `feat/<slug>` branch left standing

**Gotcha:** worktrees go because a stale one locks its path and its branch; branches stay so the partial work is still inspectable.

### Beat 4: abort on the first conflict and stop there (1 min)

**Open:** [`scripts/worktree-run.sh`](parallel-worktrees-solution/scripts/worktree-run.sh) · the merge loop · [`readme.md`](readme.md#git-worktrees-as-agent-lanes)
**Say:** Lanes run at the same time, integration happens one branch after another. The only safe answer to a merge that does not apply is to return the repo to a state somebody can start again from. Note that the two task lines own different source files and different test files, because Git's isolation is physical and nothing here resolves a conflict.

```bash
for slug in "${slugs[@]}"; do
  # --no-ff keeps one merge commit per task, so each feature stays visible in history
  if ! git merge --no-ff "feat/$slug"; then
    git merge --abort
    remove_worktrees
    exit 1
  fi
done
```

**Result:** past the loop, cleanup runs and the last statement deletes the merged branches

```bash
remove_worktrees
for slug in "${slugs[@]}"; do
  # -d refuses to delete a branch that is not merged, so only merged feature branches go
  git branch -d "feat/$slug"
done
```

**Gotcha:** agents parallel, merges sequential, a deliberate asymmetry. `git merge --abort` is what keeps the branch from being left half merged for the next run to trip over.

## If the room asks

| Question | Answer |
|---|---|
| How long does a run take? | Roughly the slowest agent, because lanes run in the background and `wait` joins them. |
| Where does agent output go? | `logs/log-<slug>.txt` per lane, the only place a failed lane's story exists. |
| What keeps two lanes from colliding? | Disjoint file scopes in `tasks.txt`. Point two lanes at one function and the second merge stops half done. |

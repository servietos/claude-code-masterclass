---
presents: demo-worktree-orchestration.md
budget: 4 min
beats: 4
---

# Present: Automate the full worktree lifecycle with a single shell script

How a hardcoded two-agent script becomes a task queue, and which three bash details decide whether a failed agent corrupts the integration branch. Four beats: one task line into a lane, the `wait` that reports the wrong exit code, keeping a failed agent out of the merge, and aborting on the first conflict.

------

**Shell:** [`scripts/worktree-run.ps1`](parallel-worktrees-solution/scripts/worktree-run.ps1) is the one script in the module where the translation is more than syntax. Beat 1's PID capture becomes job objects paired with slugs; beat 2's per-PID `wait` becomes `Receive-Job -Wait -AutoRemoveJob`. Say in beat 2 that a PowerShell job reports `Completed` even when the command inside exited non-zero, so the script emits `$LASTEXITCODE` as the job's last statement. The quoted `code=$?` is Windows-fatal: it fills the array with `True`, so no lane is ever recorded as failed.

## Beats

### Beat 1: one line of a text file becomes one worktree and one agent (1 min)

**Open:** [`tasks.txt`](parallel-worktrees-solution/tasks.txt) · [`scripts/worktree-run.sh`](parallel-worktrees-solution/scripts/worktree-run.sh) · the `while IFS='|' read` loop
**Say:** Two hardcoded lanes teach the mechanism and stop being useful at three. Separating work from machinery means adding a lane is editing data, not editing code.

```bash
while IFS='|' read -r slug desc; do
  [ -z "$slug" ] && continue

  WORKTREE="$REPO/../wt-$slug"
  git worktree add "$WORKTREE" -b "feat/$slug"
...
  slugs+=("$slug")
  pids+=($!)
done < "$TASKS_FILE"
```

**Result:** the two lines the run consumed, and the only file you edit to add a third lane

```text
slug-numeric|Change slugify in src/slugify.ts to preserve leading numbers so '42 Best Practices' becomes '42-best-practices'. Add a test in test/slugify.test.ts. Commit with message "feat: preserve numeric slugs".
camel-multi|Change kebabToCamel in src/kebab-to-camel.ts to handle inputs of four or more segments. Add a test in test/kebab-to-camel.test.ts. Commit with message "feat: handle multi-segment kebab input".
```

**Gotcha:** the slug names the worktree path, the branch and the log file at once. `slugs` and `pids` grow together, so index `i` is one lane.

### Beat 2: `wait` alone reports the wrong answer (1 min)

**Open:** [`scripts/worktree-run.sh`](parallel-worktrees-solution/scripts/worktree-run.sh) · the per-PID `wait` loop
**Say:** Fanning out is the easy half; joining back is where correctness is won or lost. A join that collapses N outcomes into one number has to be checked for which number it kept.

```bash
failed=()
for i in "${!pids[@]}"; do
  wait "${pids[$i]}"
  code=$?
  if [ "$code" -ne 0 ]; then
    failed+=("${slugs[$i]} (exit $code)")
  fi
done
```

**Result:** `failed` holds one entry per broken lane, and its length is what beat 3 branches on. Each lane's story is in `logs/log-<slug>.txt`

**Gotcha:** a bare `wait` returns the last job's code, not the worst one, so the script declares success whenever the final agent happened to succeed. That is why the PIDs were captured one at a time.

### Beat 3: a failed agent must not reach the merge phase (1 min)

**Open:** [`scripts/worktree-run.sh`](parallel-worktrees-solution/scripts/worktree-run.sh) · the failure branch
**Say:** Merging the lanes that finished produces a branch holding half an intended change with nothing recording that it is half. That is worse than merging nothing, because it looks finished downstream.

```bash
if [ "${#failed[@]}" -ne 0 ]; then
  echo "Agents failed, skipping merge:"
  printf '  %s\n' "${failed[@]}"
  remove_worktrees
  echo "Branches kept for inspection: $(printf 'feat/%s ' "${slugs[@]}")"
  exit 1
fi
```

**Result:** `exit 1` before any merge, the worktrees removed and every `feat/<slug>` branch left standing

**Gotcha:** worktrees go because a stale one locks its path and its branch; branches stay so the partial work is still inspectable.

### Beat 4: abort on the first conflict rather than pushing on (1 min)

**Open:** [`scripts/worktree-run.sh`](parallel-worktrees-solution/scripts/worktree-run.sh) · the merge loop · [`readme.md`](readme.md#git-worktrees-as-agent-lanes)
**Say:** Lanes run at the same time, integration happens one branch after another. The only safe answer to a merge that does not apply is to return the repo to a state somebody can start again from. Note that the two task lines own different source files and different test files, because Git's isolation is physical and nothing here resolves a conflict.

```bash
for slug in "${slugs[@]}"; do
  if ! git merge --no-ff "feat/$slug" -m "Merge feat/$slug"; then
    echo "Conflict merging feat/$slug, aborting"
    git merge --abort
    remove_worktrees
    echo "Branches kept for inspection: $(printf 'feat/%s ' "${slugs[@]}")"
    exit 1
  fi
done
```

**Result:** past the loop, cleanup runs and the last statement is the report

```bash
remove_worktrees
git log --oneline --graph -10
```

**Gotcha:** agents parallel, merges sequential, a deliberate asymmetry. `git merge --abort` is what keeps the branch from being left half merged for the next run to trip over.

## If the room asks

| Question | Answer |
|---|---|
| How long does a run take? | Roughly the slowest agent, not the sum, since lanes are backgrounded and joined with `wait`. |
| Why `--force` on `git worktree remove`? | An agent leaves untracked files behind. Treat it as the explicit fallback it is. |
| Where does agent output go? | `logs/log-<slug>.txt` per lane, the only place a failed lane's story exists. |
| What stops a runaway agent? | `--max-turns 8` per lane, plus a tool scope limited to editing, testing and committing. |
| Why pseudocode before the real script? | Six phases and their failure paths are cheap to fix in a numbered list, expensive after a run has half merged two branches. |
| What keeps two lanes from colliding? | Disjoint file scopes in `tasks.txt`. Point two lanes at one function and the second merge stops half done. |

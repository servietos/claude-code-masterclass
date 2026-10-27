# Parallel Worktrees Solution

Completed reference for [demo-parallel-hooks.md](../demo-parallel-hooks.md) and [demo-worktree-orchestration.md](../demo-worktree-orchestration.md).

Every script ships in a Bash and a PowerShell form. The two are behaviourally equivalent; pick the one that matches your shell.

| File | What it is |
|---|---|
| `.claude/settings.json` | The `PreToolUse` hook registration that runs the gate on every Bash call |
| `.claude/hooks/policy-gate.sh` | The gate itself: exit 2 on `rm -rf`, exit 0 otherwise |
| `.claude/hooks/policy-gate.ps1` | The same gate in PowerShell, parsing stdin with `ConvertFrom-Json`, where the Bash gate uses `jq` |
| `worktree-parallel.sh` | The fixed two-agent script the policy-gate demo runs and the orchestrator generalizes |
| `worktree-parallel.ps1` | The same two-agent script using `Start-Job` and `Receive-Job -Wait` |
| `scripts/worktree-run.sh` | The generalized orchestrator: one worktree per line of `tasks.txt`, per-agent exit codes, merge or abort |
| `scripts/worktree-run.ps1` | The same orchestrator, reading each agent's exit code back out of its job |
| `tasks.txt` | Two sample tasks in `slug\|description` form |

## Run It

```bash
cd demos/05-cli/04-parallel-hooks/parallel-worktrees-solution
npm install
./scripts/worktree-run.sh tasks.txt
```

PowerShell:

```powershell
cd demos/05-cli/04-parallel-hooks/parallel-worktrees-solution
npm install
./scripts/worktree-run.ps1 tasks.txt
```

Both scripts resolve the repository root with `git rev-parse --show-toplevel` and this folder's path inside it with `git rev-parse --show-prefix`, so each agent starts in this same folder inside its own worktree. Worktrees are created next to the repository root as `wt-<slug>` and removed at the end; agent logs land in `logs/`.

`settings.json` registers the Bash gate. To have the harness run the PowerShell gate instead, change that one `command` value to `pwsh -NoProfile -File "$CLAUDE_PROJECT_DIR/.claude/hooks/policy-gate.ps1"`; a `.ps1` is not self-executing, so it needs the interpreter named in front of it.

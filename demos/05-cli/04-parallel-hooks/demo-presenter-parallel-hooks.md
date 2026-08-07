---
presents: demo-parallel-hooks.md
budget: 2 min
beats: 2
---

# Present: Carry a policy gate into every parallel worktree

A `PreToolUse` hook belongs to the checkout, not to the session, so it travels into every worktree an orchestrator opens. Two beats: the registration and its one-command proof, then the parallel lanes it still covers.

------

**Shell:** beats quote Bash; [`policy-gate.ps1`](parallel-worktrees/.claude/hooks/policy-gate.ps1), [`verify-policy-gate.ps1`](parallel-worktrees-solution/verify-policy-gate.ps1) and [`worktree-parallel.ps1`](parallel-worktrees/worktree-parallel.ps1) are the counterparts. The gate parses stdin with `ConvertFrom-Json` instead of `jq`, and beat 1's registration gains a `pwsh -NoProfile -File` prefix. `$?` is Windows-fatal in beat 1's proof: read `$LASTEXITCODE`, since the beat rests on the room seeing a literal 2.

## Beats

### Beat 1: registration is a matcher plus a path, and it proves itself in one command (1 min)

**Open:** [`.claude/settings.json`](parallel-worktrees/.claude/settings.json) · [`verify-policy-gate.sh`](parallel-worktrees-solution/verify-policy-gate.sh)
**Say:** Policy that depends on somebody remembering to apply it is not policy. Coverage is settled by configuration before the session opens, and a hook is an ordinary program, so it can be proved without an agent taking part.

```json
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/policy-gate.sh" }
        ]
      }
    ]
```

**Result:** the shipped payloads fed in by hand, no agent, no token

```text
Policy gate: rm -rf is blocked.
blocked command exit code: 2
allowed command exit code: 0
```

**Gotcha:** only 2 blocks; any other non-zero code warns and lets the command run. `$CLAUDE_PROJECT_DIR` keeps the path correct wherever the session was launched from, which is exactly what beat 2 depends on.

### Beat 2: the gate is a property of the checkout, not of the session (1 min)

**Open:** [`worktree-parallel.sh`](parallel-worktrees/worktree-parallel.sh) · [`.claude/settings.json`](parallel-worktrees/.claude/settings.json)
**Say:** The real question about any safety mechanism is what happens once work fans out to agents nobody is watching. Policy in the checkout answers that by default: every lane opens the same project and loads the same configuration.

```bash
# ( ... ) & runs the session in a background subshell, so both agents work at the same time
(
  cd "$FEAT_A/$DEMO_DIR"
  claude -p "Improve src/kebab-to-camel.ts to handle multi-word inputs. Add tests. Commit the result." \
    --allowed-tools "Read,Edit,Bash(npm:*),Bash(git:*)" --max-turns 10
) &
```

**Result:** `settings.json` and both gate scripts are tracked, so every worktree checks them out again and `rm -rf` is blocked in each lane

**Gotcha:** `--allowed-tools` on that line scopes what this agent may attempt; the hook decides what any agent in this checkout may actually do.

## If the room asks

| Question | Answer |
|---|---|
| Why not just say so in `CLAUDE.md`? | A prompt instruction relies on the model complying. The hook runs at the process boundary, outside the model's awareness. |
| Where do we write a hook from scratch? | Module 2, [Build a Three-Event Hook Pipeline](../../02-harness/03-hooks/demo-hook-pipeline.md): payload contract, exit codes, and the `Stop` event. |
| Is one `rm -rf` pattern enough? | No. Module 09, [Enforce Least Privilege with Hook Guardrails](../../09-observability/02-guardrails/demo-hook-guardrails.md), covers six patterns, a deny decision object, and the audit log. |
| Do I need `--settings` for a headless run? | Not when the agent starts inside the project. Pass it when the working directory is not the project root. |

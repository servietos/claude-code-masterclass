# Carry a policy gate into every parallel worktree

A `PreToolUse` hook is registered in the checkout, not in the session, so agents launched into separate worktrees all load it. You check the gate the starter ships, then run the two-agent script and see `rm -rf` refused in a lane nobody is watching.

------

## Setup

```bash
cd demos/05-cli/04-parallel-hooks/parallel-worktrees
claude
```

The worktrees the demo creates land under the repository root and are removed at the end. The Bash hook script parses its stdin payload with `jq`, so `jq` must be on your PATH; the PowerShell hook uses the built-in `ConvertFrom-Json` and needs nothing extra.

The starter ships the gate in both forms, `.claude/hooks/policy-gate.sh` and `.claude/hooks/policy-gate.ps1`, and `settings.json` registers the Bash one.

## Part A: Read the Registration

Open [parallel-worktrees/.claude/settings.json](parallel-worktrees/.claude/settings.json). The whole gate is a matcher plus a path:

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

`$CLAUDE_PROJECT_DIR` resolves against the project the session opened, which is the property Part C rests on: a worktree is a different absolute path and the registration still finds its own copy of the script. Bash gets the script path directly because the shebang makes the file self-executing; PowerShell needs the interpreter named in front of it, which also keeps a slow user profile out of a hook that runs on every Bash call:

```json
{ "type": "command", "command": "pwsh -NoProfile -File \"$CLAUDE_PROJECT_DIR/.claude/hooks/policy-gate.ps1\"" }
```

## Part B: Confirm the Gate Fires

Feed the gate the same JSON the harness would send, without spending a Claude turn:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /tmp/test-dir"}}' | .claude/hooks/policy-gate.sh
echo $?
```

PowerShell:

```powershell
'{"tool_name":"Bash","tool_input":{"command":"rm -rf /tmp/test-dir"}}' | pwsh -NoProfile -File .claude/hooks/policy-gate.ps1
$LASTEXITCODE
```

The script prints `Policy gate: rm -rf is blocked.` on stderr and exits `2`. Exit code 2 is the value that makes a `PreToolUse` hook block the call; any other non-zero code only surfaces a warning. Run this first whenever a gate does not fire in a real session: it separates a bad pattern, a non-executable script, and a path that never resolved, which look identical from inside the agent.

## Part C: Prove the Gate Holds Across Parallel Agents

The starter ships [parallel-worktrees/worktree-parallel.sh](parallel-worktrees/worktree-parallel.sh) and [parallel-worktrees/worktree-parallel.ps1](parallel-worktrees/worktree-parallel.ps1), so you do not write either here. Run it from the starter:

```bash
bash worktree-parallel.sh
```

PowerShell:

```powershell
./worktree-parallel.ps1
```

Each agent runs in its own worktree, and `settings.json` plus both gate scripts are tracked files, so every worktree checks them out again and loads the same configuration. Ask one of them to remove a directory with `rm -rf` and the call is blocked in the worktree exactly as it was in Part B. `--allowed-tools` on the `claude -p` line scopes what one agent may attempt; the hook decides what any agent in this checkout may actually do.

The completed version of this demo, with the gate and the parallel worktree script, lives in [parallel-worktrees-solution/](parallel-worktrees-solution/). Run the script from the folder it sits in: it resolves both the repository root and its own path inside the repository from the current directory.

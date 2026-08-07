---
presents: demo-hook-guardrails.md
budget: 4 min
beats: 4
---

# Present: Enforce Least Privilege with Hook Guardrails

Two layers of least privilege: a hook is the safety net, a scoped toolset is the primary defense. Four beats: the matcher list, the deny contract, the blocked log, the tool that was never there.

------

**Shell:** beats quote Bash; [`hooks/deny-destructive.ps1`](demo-hook-guardrails/hooks/deny-destructive.ps1) is the twin, same six patterns and the same literal deny payload. Beat 1 exists only because Windows adds a `PowerShell` tool a Bash-only matcher never sees; on macOS and Linux that second matcher never fires and `pwsh` is not needed.

## Beats

### Beat 1: a guardrail is only as wide as its matcher list (1 min)

**Open:** [`.claude/settings.json`](demo-hook-guardrails/.claude/settings.json) · the two `PreToolUse` matchers and their handlers
**Say:** A hook is wired to tool names, so its coverage is whatever you enumerated. There is no concept of "any shell".

```json
        "matcher": "Bash",
...
            "command": "bash",
            "args": ["${CLAUDE_PROJECT_DIR}/hooks/deny-destructive.sh"]
...
        "matcher": "PowerShell",
...
            "command": "pwsh",
            "args": ["-NoProfile", "-File", "${CLAUDE_PROJECT_DIR}/hooks/deny-destructive.ps1"]
```

**Result:** the adversarial pass on the Bash-only wiring, in [`verification.md`](demo-hook-guardrails-solution/verification.md#why-both-matchers-ship)

```json
"permission_denials":[]
```

**Gotcha:** `build/` was gone afterwards and no log line was written, so the guardrail passed review on one operating system and was decorative on another.

### Beat 2: the deny verdict is exit 0 plus JSON on stdout, never exit 2 (1 min)

**Open:** [`hooks/deny-destructive.sh`](demo-hook-guardrails/hooks/deny-destructive.sh) · the `deny()` function, lines 8-12 · [Hard Stops and Scope Constraints](readme.md#hard-stops-and-scope-constraints)
**Say:** The reason is not a log line, it is text handed back to the model. A mismatched exit code still blocks the call, so it reads as a silent refusal.

```bash
deny() {
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}' "$1"
  # exit 0 with this JSON on stdout is the deny verdict, exit 2 also blocks but throws the reason away
  exit 0
}
```

**Result:** the literal payload, identical from both scripts across sixteen tested commands, in [`verification.md`](demo-hook-guardrails-solution/verification.md#pattern-matrix)

```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Destructive command rejected by guardrail hook: recursive forced rm. Logged to hooks/blocked.log."}}
```

**Gotcha:** on exit 2 stdout is discarded and stderr becomes the reason, so this JSON plus exit 2 blocks with no explanation at all.

### Beat 3: every block is a near-miss caught on tape (1 min)

**Open:** [`hooks/deny-destructive.sh`](demo-hook-guardrails/hooks/deny-destructive.sh) · the `reasons` array, lines 39-46 · [`build/old.txt`](demo-hook-guardrails/build/old.txt)
**Say:** A guardrail that only blocks leaves nothing behind. The log is an incident record for actions that never happened.

```bash
    { printf '%s BLOCKED (%s): %s\n' "$(date +%Y-%m-%dT%H:%M:%S%:z)" "${reasons[$i]}" "$command" >> "$log_path"; } 2>/dev/null || true
```

**Result:** eight blocks, timestamp and matched reason and verbatim command, in [`hooks/blocked.log`](demo-hook-guardrails-solution/hooks/blocked.log), a file that exists only in the solution

```text
2026-07-23T07:19:51+02:00 BLOCKED (recursive forced rm): rm -rf build/
2026-07-23T07:19:52+02:00 BLOCKED (recursive forced rm): rm -rf .
2026-07-23T07:19:52+02:00 BLOCKED (recursive forced Remove-Item): Remove-Item build -Recurse -Force
2026-07-23T07:19:52+02:00 BLOCKED (git push --force): git push --force origin main
2026-07-23T07:19:52+02:00 BLOCKED (git push -f): git push -f origin main
2026-07-23T07:19:52+02:00 BLOCKED (git reset --hard): git reset --hard HEAD~1
2026-07-23T07:19:52+02:00 BLOCKED (fork bomb signature): :(){ :|:& };:
2026-07-23T07:19:53+02:00 BLOCKED (recursive forced rm): rm -fr /
```

**Gotcha:** read the rate as a signal, not a score: ten of these in a week says the agent's scope is too wide, one says the hook is doing its job.

### Beat 4: the safest tool is the one the agent never had (1 min)

**Open:** [`.claude/agents/research-agent.md`](demo-hook-guardrails/.claude/agents/research-agent.md) · the `tools:` frontmatter key · [Least Privilege Per Sub-Agent](readme.md#least-privilege-per-sub-agent)
**Say:** Interception inspects a call that was made; absence leaves no call to inspect. Both layers ship because they fail in opposite directions.

```markdown
name: research-agent
...
model: sonnet
tools: Read, Grep, Glob
---
...
You answer research questions about the current repository. You can read files, grep across them, and glob for paths. Edit, Write, and Bash are not in your tool list, so they are not available to you at all.
```

**Result:** the delegated run emitted no `Bash` call, so the hook never ran, in [`verification.md`](demo-hook-guardrails-solution/verification.md#live-claude-code-runs)

```text
Run 2 (the readme's Run 2 prompt) returned `is_error: false`.
...
No `Bash` call was emitted by the sub-agent, so the hook never ran for it.
```

**Gotcha:** scope is minimal but rigid, hooks are flexible but only as good as the patterns you wrote, which is why neither replaces the other.

## If the room asks

| Question | Answer |
|---|---|
| Does it catch what the model actually reaches for? | Yes. Asked to clear `build/`, it proposed `rm -rf build/* build/.[!.]* 2>/dev/null; ls -la build/`, which landed in `permission_denials` and left `build/old.txt` intact. |
| What if the destructive command is hidden inside a script the agent runs? | The hook sees only the top-level invocation; also deny `Bash(bash:*)` and `Bash(sh:*)` so no sub-shell escapes the matcher. |
| Can a hook transform a command instead of blocking it? | Yes: return `"permissionDecision":"allow"` with an `updatedInput` object and Claude Code runs the rewritten call. |
| Does the hook slow things down? | Every invocation starts a process: a few milliseconds for `bash`, a few hundred for `pwsh`. |
| Why did my allow list not apply? | Allow rules in a project `.claude/settings.json` need the workspace trust dialog accepted first; hooks fire regardless. |

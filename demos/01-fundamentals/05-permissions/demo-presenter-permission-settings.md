---
presents: demo-permission-settings.md
budget: 4 min
beats: 4
---

# Present: Lock Down a Repository With Permission Rules

Four beats build a permission policy one rule at a time and test each outcome it produces. The room walks away able to predict any rule's outcome from the deny, ask, allow ordering, and able to spot a rule that parses cleanly and protects nothing.

------

**No solution folder ships.** The run adds a `.claude/` folder the starter does not have, and the rest of the proof is behavioural.

## Beats

### Beat 1: A denied path stays denied through the shell (1 min)

**Open:** [Step 1: Make a secret genuinely unreachable](demo-permission-settings.md#step-1-make-a-secret-genuinely-unreachable) · [`permissions-api/appsettings.Secrets.json`](permissions-api/appsettings.Secrets.json)
**Say:** Denying a file by path is the one outcome nothing in a prompt can talk around. The room asks immediately whether the block survives the obvious shell detour.

```json
    "deny": [
      "Read(./appsettings.Secrets.json)",
      "Read(./secrets/**)",
      "Edit(./secrets/**)"
    ]
```

**Result:** the shell route through `cat` is refused by the harness, quoted from the tool result Claude reports

```text
Permission to use Bash with command cat appsettings.Secrets.json has been denied.
```

**Gotcha:** the starter's `CLAUDE.md` forbids reading the file, so without the lift in the prompt Claude refuses before any tool call and the deny rule never fires. Read and Edit deny rules already cover `cat`, `head`, `tail` and `sed` inside Bash, so you write no separate shell rule.

### Beat 2: Deny wins first, and cannot carry an exception (1 min)

**Open:** [Step 1: Make a secret genuinely unreachable](demo-permission-settings.md#step-1-make-a-secret-genuinely-unreachable) · [`readme.md`](readme.md#denials-are-a-feature)
**Say:** Deny rules are for the plausible commands that arrive late in a long session. Their whole value is that there is no button to press. The room meets this same command inventory a second time in [Guardrails](../../07-optimize-observability/05-guardrails/demo-hook-guardrails.md), where a `PreToolUse` hook stops it in the harness, and a settings rule stops it at the permission check.

```json
  "deny": [
    ...
    "Bash(rm -rf *)",
    "Bash(sudo *)",
    "Bash(git push --force *)",
    "Bash(git reset --hard *)"
  ]
```

**Result:** a refusal with no prompt offered.

**Gotcha:** deny, then ask, then allow, first match wins with specificity playing no part, so denying `Bash(git push *)` while allowing `Bash(git push origin main)` blocks every push.

### Beat 3: Team policy and personal convenience are different files (1 min)

**Open:** [Step 2: Separate team policy from personal overrides](demo-permission-settings.md#step-2-separate-team-policy-from-personal-overrides) · [`readme.md`](readme.md#where-permissions-are-stored)
**Say:** Two files hold permission rules for one repository, and the difference is who they bind. A settings diff never gets the scrutiny a code diff does.

```json
{
  "permissions": {
    "allow": [
      "Bash(dotnet run)",
      "Read(~/scratch/**)"
    ]
  }
}
```

**Result:** `git status --short` lists the committed policy file and not the local override

```text
?? .claude/settings.json
```

**Gotcha:** local beats project beats user-level, with managed settings above all, but that ordering applies to allow rules only: no local file can weaken a deny.

### Beat 4: Two startup lines that explain "my rules do nothing" (1 min)

**Open:** [Step 3: Prove the policy holds](demo-permission-settings.md#step-3-prove-the-policy-holds) · [`readme.md`](readme.md#workspace-trust)
**Say:** A policy can be syntactically perfect and still be doing nothing, and the evidence arrives before the first prompt. Two unrelated causes produce the same appearance.

```text
Ignoring 3 permissions.allow entries from .claude/settings.json: this workspace has not been trusted. Run Claude Code interactively here once and accept the trust dialog, or ...

...

Permission deny rule (.claude\settings.json): Write(./secrets/**) is not matched by file permission checks — only Edit(path) rules are. Use Edit(./secrets/**) instead (Edit rules cover all file-editing tools).
```

**Result:** a startup carrying neither line.

**Gotcha:** workspace trust suppresses every allow entry while leaving deny rules active; `Write`, `NotebookEdit` and `Glob` path rules parse and are never matched by the file checks.

## If the room asks

| Question | Answer |
|---|---|
| My allow rules did nothing. What is wrong? | The workspace was almost certainly never trusted; run `claude` interactively once, accept the dialog, and read the first lines of startup. |
| Does the deny stop a script from reading the secrets file? | No, a Python or Node process that opens it is an ordinary subprocess; enable the sandbox for OS-level enforcement. |
| How do I know the policy is actually tested? | One action per branch: `dotnet build` untouched, `dotnet nuget push` prompts, both routes to the secrets file refused, `cat TodoApi.csproj` still works. |

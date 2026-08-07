---
presents: demo-permission-settings.md
budget: 6 min
beats: 6
---

# Present: Lock Down a Repository With Permission Rules

Six beats build a permission policy one rule at a time and test each outcome it produces. The room walks away able to predict any rule's outcome from the deny, ask, allow ordering, and able to spot a rule that parses cleanly and protects nothing.

------

**No solution folder ships.** The run adds a `.claude/` folder the starter does not have, and the rest of the proof is behavioural.

## Beats

### Beat 1: Prose is a request, the settings file is the control (1 min)

**Open:** [`permissions-api/CLAUDE.md`](permissions-api/CLAUDE.md) · the `## Secrets` section · [`permissions-api/appsettings.Secrets.json`](permissions-api/appsettings.Secrets.json)
**Say:** Permission rules are enforced by Claude Code itself, outside the model. Prose shapes what Claude tries to do and never changes what it is allowed to do.

```markdown
## Secrets

`appsettings.Secrets.json` holds connection strings and API keys. Never read it, never echo it, and never copy its values into another file.
```

**Result:** nothing enforces this yet; `permissions-api/` ships no `.claude/` folder at all.

**Gotcha:** the starter already asks for exactly the protection the demo goes on to build, which is the point of opening here.

### Beat 2: The space before the wildcard is the size of the grant (1 min)

**Open:** [Step 2: Allow the commands you run constantly](demo-permission-settings.md#step-2-allow-the-commands-you-run-constantly) · [`readme.md`](readme.md#bash-patterns)
**Say:** Approval fatigue is a security problem, not a comfort one: at twenty prompts an hour nobody reads them. Pre-approve the narrow commands you run all day and nothing wider.

```json
{
  "permissions": {
    "allow": [
      "Bash(dotnet build)",
      "Bash(dotnet restore)",
      "Bash(dotnet test *)",
      ...
    ]
  }
}
```

**Result:** `.claude/settings.json` in [`permissions-api/`](permissions-api/), the starter's first, carrying five allow rules; `dotnet build` stops prompting and `dotnet run` still does.

**Gotcha:** `Bash(dotnet test *)` matches `dotnet test --filter Unit` and not `dotnet testfoo`, because the space enforces a word boundary; drop it and both match.

### Beat 3: A denied path stays denied through the shell (1 min)

**Open:** [Step 3: Make a secret genuinely unreachable](demo-permission-settings.md#step-3-make-a-secret-genuinely-unreachable) · [`permissions-api/appsettings.Secrets.json`](permissions-api/appsettings.Secrets.json)
**Say:** Denying a file by path is the one outcome nothing in a prompt can talk around. The room asks immediately whether the block survives the obvious shell detour.

```json
    "deny": [
      "Read(./appsettings.Secrets.json)",
      "Read(./.env)",
      "Read(./secrets/**)",
      "Edit(./secrets/**)"
    ]
```

**Result:** both routes refused, the direct Read and the shell route through `cat`

```text
Permission denied — the command wasn't run, so I have no output from it.
```

**Gotcha:** Read and Edit deny rules already cover `cat`, `head`, `tail` and `sed` inside Bash, so you write no separate shell rule.

### Beat 4: Deny wins first, and cannot carry an exception (1 min)

**Open:** [Step 4: Refuse the commands that cannot be undone](demo-permission-settings.md#step-4-refuse-the-commands-that-cannot-be-undone) · [`readme.md`](readme.md#denials-are-a-feature)
**Say:** Deny rules are for the plausible commands that arrive late in a long session, not the dramatic ones nobody would approve. Their whole value is that there is no button to press. The room meets this same command inventory a second time in [02: Guardrails](../../09-observability/02-guardrails/readme.md), where a `PreToolUse` hook stops it in the harness rather than a settings rule stopping it at the permission check.

```json
  "deny": [
    ...
    "Bash(rm -rf *)",
    "Bash(sudo *)",
    "Bash(git push --force *)",
    "Bash(git reset --hard *)"
  ]
```

**Result:** a refusal that cites the deny rule, with no prompt offered.

**Gotcha:** deny, then ask, then allow, first match wins with specificity playing no part, so denying `Bash(git push *)` while allowing `Bash(git push origin main)` blocks every push.

### Beat 5: Team policy and personal convenience are different files (1 min)

**Open:** [Step 5: Separate team policy from personal overrides](demo-permission-settings.md#step-5-separate-team-policy-from-personal-overrides) · [`readme.md`](readme.md#where-permissions-are-stored)
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

**Result:** `.claude/settings.local.json` beside the committed file, and `git status --short` does not list it

```diff
 permissions-api/
+  .claude/settings.json
+  .claude/settings.local.json
   appsettings.Secrets.json
   CLAUDE.md
   TodoApi.csproj
```

**Gotcha:** local beats project beats user-level, with managed settings above all, but that ordering applies to allow rules only: no local file can weaken a deny.

### Beat 6: Two startup lines that explain "my rules do nothing" (1 min)

**Open:** [Step 6: Prove the policy holds](demo-permission-settings.md#step-6-prove-the-policy-holds) · [`readme.md`](readme.md#workspace-trust)
**Say:** A policy can be syntactically perfect and still be doing nothing, and the evidence arrives before the first prompt. Two unrelated causes produce the same appearance.

```text
Ignoring 2 permissions.allow entries from .claude/settings.json: this workspace has not been trusted. Run Claude Code interactively here once and accept the trust dialog.

...

Permission deny rule (.claude\settings.json): Write(./secrets/**) is not matched by file permission checks — only Edit(path) rules are. Use Edit(./secrets/**) instead (Edit rules cover all file-editing tools).
```

**Result:** a startup carrying neither line, plus a `## Permissions` section added to [`permissions-api/CLAUDE.md`](permissions-api/CLAUDE.md).

**Gotcha:** workspace trust suppresses every allow entry while leaving deny rules active; `Write`, `NotebookEdit` and `Glob` path rules parse and are never matched by the file checks.

## If the room asks

| Question | Answer |
|---|---|
| My allow rules did nothing. What is wrong? | The workspace was almost certainly never trusted; run `claude` interactively once, accept the dialog, and read the first lines of startup. |
| Does `Bash(dotnet build)` cover `dotnet build && dotnet run`? | No, compound commands are checked per subcommand; seven separators are recognised, listed in the Step 2 tip. |
| Does the deny stop a script from reading the secrets file? | No, a Python or Node process that opens it is an ordinary subprocess; enable the sandbox for OS-level enforcement. |
| Why did my rule match nothing without a warning? | Deny and ask rules with unknown tool names warn at startup, allow rules do not; `Stop Task` is a transcript label, not a tool name. |
| How do I know the policy is actually tested? | One action per branch: `dotnet build` untouched, `dotnet nuget push` prompts, both routes to the secrets file refused, `cat TodoApi.csproj` still works. |

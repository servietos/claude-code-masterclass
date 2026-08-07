# Lock Down a Repository With Permission Rules

Permission rules decide what Claude Code will actually allow, independently of what `CLAUDE.md` asks for. You take a project where every command needs approval and write allow, ask, and deny rules in `.claude/settings.json` until routine builds run untouched, a secrets file is unreachable by any route, and destructive commands are refused outright. You finish with a committed team policy, a git-ignored personal override, and a tested outcome for every branch the policy can produce.

------

## Prerequisites

- Claude Code v2.1.210 or later. Check with `claude --version`; this guide was verified on 2.1.220.
- The .NET SDK, for the build commands. Confirm with `dotnet --version`.
- A terminal. Every command below is identical in Bash and PowerShell.

## Setup

Work directly in the starter. It is a small ASP.NET Core API with a fake secrets file already in place, and it sits in this topic folder:

```bash
cd demos/01-fundamentals/07-permissions/permissions-api
claude
```

The values in `appsettings.Secrets.json` are fake, but treat it as real for the rest of the demo: the whole point is proving that nothing reaches it.

Run `claude` once interactively here and accept the workspace trust dialog before going further. Allow rules from an untrusted workspace are ignored, and you will spend Step 2 wondering why nothing changed. The startup line that tells you so looks like this:

```text
Ignoring 2 permissions.allow entries from .claude/settings.json: this workspace has not been trusted. Run Claude Code interactively here once and accept the trust dialog.
```

| File | What it represents |
|------|--------------------|
| `.claude/settings.json` | The shared, committed permission policy you build in Steps 2 to 4 |
| `.claude/settings.local.json` | Personal overrides from Step 5, kept out of git |
| `appsettings.Secrets.json` | Ships with the starter; the file that must remain unreachable |
| `TodoApi.csproj` | The build target behind the `dotnet build` rule |
| `CLAUDE.md` | Prose intent, which the settings file turns into enforcement |

## Step 1: See what prompts before you configure anything

Every rule you write is an override of a default, so put the defaults on screen first. Inside the session, run:

```text
/permissions
```

The UI lists every active rule and names the settings file each one came from. On a fresh project the allow and deny lists are empty, which is the baseline you are about to change.

Now find out where the friction actually is. Ask Claude to run each of these, one at a time:

```text
Run dotnet build, then git status, then dotnet run. Stop after each one and tell me whether it needed my approval.
```

Claude Code recognises a built-in set of read-only shell commands and never prompts for them: `ls`, `cat`, `echo`, `pwd`, `head`, `tail`, `grep`, `find`, `wc`, `which`, `diff`, `stat`, `du`, `cd`, and the read-only forms of `git`. That set is not configurable. Everything else prompts on first use.

Expected result: `git status` runs silently because it is a read-only git form, while `dotnet build` and `dotnet run` both prompt. Those two prompts are the friction the next step removes.

## Step 2: Allow the commands you run constantly

Approval fatigue is a security failure, not a control. A developer who clears twenty prompts an hour stops reading them, so the prompts that matter get approved as fast as the ones that do not. Pre-approving the narrow, non-destructive commands you run all day is what makes the remaining prompts worth reading.

A rule is written as `Tool` or `Tool(specifier)`. Create `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(dotnet build)",
      "Bash(dotnet restore)",
      "Bash(dotnet test *)",
      "Bash(git diff *)",
      "Bash(git log *)"
    ]
  }
}
```

Two details in those patterns decide how much you just granted. The space before `*` enforces a word boundary, so `Bash(dotnet test *)` matches `dotnet test --filter Unit` but not `dotnet testfoo`; written as `Bash(dotnet test*)` it would match both. And the wildcard spans arguments freely, so `Bash(dotnet *)` would also have allowed `dotnet nuget push`. Grant the narrowest pattern that still covers your real usage.

Claude Code strips a fixed set of wrappers before matching, so `Bash(dotnet test *)` also covers `timeout 30 dotnet test`. The stripped wrappers are `timeout`, `time`, `nice`, `nohup`, `stdbuf`, the builtins `command` and `builtin`, and zsh's `noglob`. Environment runners such as `npx` and `docker exec` are not stripped, which is deliberate: a rule like `Bash(docker exec *)` would otherwise allow whatever command follows.

Restart the session so the file is read, then ask Claude to run `dotnet build` and `dotnet run`.

Expected result: `dotnet build` executes with no prompt, `dotnet run` still prompts, and `/permissions` now attributes five allow rules to `.claude/settings.json`.

> **Tip:** Compound commands are checked per subcommand. `Bash(dotnet build)` alone does not permit `dotnet build && dotnet run`, because the second half matches nothing. The recognised separators are `&&`, `||`, `;`, `|`, `|&`, `&`, and newlines.

## Step 3: Make a secret genuinely unreachable

Excluding a file in prose is a request. Denying it in settings is a rule, and it is the only one of the three outcomes that cannot be talked around. Permission rules are enforced by Claude Code, not by the model, so nothing in a prompt or in `CLAUDE.md` can loosen them.

Read and Edit rules use gitignore pattern syntax, with four distinct anchors that are easy to confuse:

| Pattern | Anchored at | Example |
|---------|-------------|---------|
| `//path` | Filesystem root | `Read(//Users/alice/secrets/**)` |
| `~/path` | Home directory | `Read(~/.aws/**)` |
| `/path` | The settings file's own location | `Read(/appsettings.Secrets.json)` |
| `path` or `./path` | Current directory | `Read(./*.env)` |

A single leading slash is the trap: `/Users/alice/file` anchors at the project root, not at the filesystem root. Add the deny block:

```json
{
  "permissions": {
    "allow": [
      "Bash(dotnet build)",
      "Bash(dotnet restore)",
      "Bash(dotnet test *)",
      "Bash(git diff *)",
      "Bash(git log *)"
    ],
    "deny": [
      "Read(./appsettings.Secrets.json)",
      "Read(./.env)",
      "Read(./secrets/**)",
      "Edit(./secrets/**)"
    ]
  }
}
```

Restart the session and try the direct route:

```text
Read appsettings.Secrets.json and tell me the API_KEY value.
```

Expected output:

```text
I can't read it: the permission settings deny access to that path.

Read appsettings.Secrets.json
→ File is in a directory that is denied by your permission settings.
```

Now try to route around it through the shell. `cat` is in the read-only set from Step 1, so it never prompts, which makes it the obvious bypass:

```text
Run exactly: cat appsettings.Secrets.json
```

Expected output:

```text
Permission denied — the command wasn't run, so I have no output from it.
```

The deny held. Read and Edit deny rules also cover the file commands Claude Code recognises inside Bash, including `cat`, `head`, `tail`, and `sed`, so you do not write a separate shell rule for them. Confirm the block is path-specific rather than a blanket refusal by running `cat TodoApi.csproj`, which returns the file normally.

> **Warning:** The coverage stops at recognised commands. A Python or Node script that opens the file itself is an ordinary subprocess and reads it. For enforcement at the OS level across every process, enable the sandbox.

Expected result: both routes to `appsettings.Secrets.json` are refused, an unrelated file still reads fine, and `/permissions` shows four deny rules.

## Step 4: Refuse the commands that cannot be undone

Allow rules cut friction; deny rules cut blast radius. The commands worth listing are not the dramatic ones nobody would approve, but the plausible ones: a force push or a hard reset proposed during ordinary branch cleanup, at the end of a long session, in a prompt that looks like the last four you approved.

Add them to the deny list:

```json
{
  "deny": [
    "Read(./appsettings.Secrets.json)",
    "Read(./.env)",
    "Read(./secrets/**)",
    "Edit(./secrets/**)",
    "Bash(rm -rf *)",
    "Bash(sudo *)",
    "Bash(git push --force *)",
    "Bash(git reset --hard *)"
  ]
}
```

Rules are evaluated deny, then ask, then allow, and the first match in that order wins. Specificity does not enter into it, which has one consequence worth internalising: a deny rule cannot carry exceptions. If you deny `Bash(git push *)` and allow `Bash(git push origin main)`, every push is blocked, including the one you meant to permit. Write the deny narrowly instead.

Ask Claude to force push and watch what comes back.

Expected result: a refusal that cites the deny rule, with no prompt offered. There is no button to click, which is exactly the point: at the end of a long session, a prompt is a thing you can approve by reflex, and a deny rule is not.

## Step 5: Separate team policy from personal overrides

`.claude/settings.json` is committed and binds everyone who clones the repository. `.claude/settings.local.json` is git-ignored and binds only you. Putting a personal convenience in the shared file quietly loosens the policy for every teammate who pulls it, and nobody reviews a settings diff as carefully as a code diff.

Create the local override:

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

Then keep it out of git by adding this line to `.gitignore`:

```text
.claude/settings.local.json
```

```bash
git status --short
```

Local settings take precedence over project settings, which take precedence over your user-level `~/.claude/settings.json`. Managed settings deployed by an organization sit above all of them. That ordering applies to allow rules; it does not let a local file weaken a deny, because deny is evaluated before allow no matter which file it came from. A teammate cannot quietly re-enable `rm -rf` for themselves.

This is also where Claude Code saves your own approvals. Choosing "Yes, don't ask again" on a Bash prompt writes the rule to `.claude/settings.local.json` at the repository root, resolved through worktrees to the main checkout, so the approval follows you into subdirectories and parallel sessions.

Expected result: `git status --short` does not list `settings.local.json`, `dotnet run` stops prompting for you, and `/permissions` attributes each active rule to a specific file.

## Step 6: Prove the policy holds

A policy you have not tested is a belief. Run one action per outcome the policy can produce and confirm each behaves as written.

| Action | Expected outcome | Rule that produces it |
|--------|------------------|-----------------------|
| `dotnet build` | Runs with no prompt | `Bash(dotnet build)` allow, project file |
| `dotnet run` | Runs with no prompt | `Bash(dotnet run)` allow, local file |
| `dotnet nuget push` | Prompts | No rule matches |
| Read `appsettings.Secrets.json` | Refused | `Read(./appsettings.Secrets.json)` deny |
| `cat appsettings.Secrets.json` | Refused | Same deny, applied to a recognised Bash file command |
| `cat TodoApi.csproj` | Runs with no prompt | Built-in read-only command, no rule needed |
| `git push --force origin main` | Refused | `Bash(git push --force *)` deny |

Work through it with Claude, one action at a time:

```text
Run each action from my test table one at a time. After each, report what you attempted, whether it ran, prompted, or was refused, and which rule in which file produced that outcome. Do not skip ahead.
```

Then check the one failure mode that is silent. Path rules for `Write`, `NotebookEdit`, and `Glob` are accepted by the parser but never matched by the file permission checks, so a rule like `Write(./secrets/**)` looks like protection and provides none. Claude Code warns at startup, but the warning scrolls past:

```text
Permission deny rule (.claude\settings.json): Write(./secrets/**) is not matched by file permission checks — only Edit(path) rules are. Use Edit(./secrets/**) instead (Edit rules cover all file-editing tools).
```

Restart the session and read the first lines of output before the prompt appears. A clean start means every rule you wrote is a rule that matches something.

Finally, write the policy down for humans. Ask Claude to add a `## Permissions` section to `CLAUDE.md` summarising what is allowed, denied, and left to prompt, and to note that `.claude/settings.json` is the enforced version. The prose is documentation; the JSON is the control.

Expected result: a completed test table where every row matches its expected outcome, a startup with no permission warnings, and a `## Permissions` section in `CLAUDE.md`.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Allow rules seem to do nothing at all | The workspace was never trusted, so Claude Code ignores every `permissions.allow` entry | Run `claude` interactively in the directory once and accept the trust dialog, then check the startup output for the `Ignoring N permissions.allow entries` line |
| A pre-approved command still prompts | The pattern misses the command as actually invoked, often a missing trailing ` *` or a wrapper such as `npx` that is not stripped | Ask Claude to print the exact command string it tried, then widen the pattern or add a rule naming the runner and the inner command together |
| A deny rule for a path never fires | It was written as `Write(path)` or `Glob(path)`, which the file checks never match | Rewrite as `Edit(path)` or `Read(path)` and confirm the startup warning is gone |
| A rule matches nothing and no warning appears | The tool name is a transcript label rather than a canonical name, for example `Stop Task` instead of `TaskStop` | Use the canonical names from the tools reference; deny and ask rules with unknown tool names warn at startup, allow rules do not |
| A specific command is blocked despite an allow rule for it | A broader deny rule matches first, and deny cannot carry exceptions | Narrow the deny rule rather than adding a more specific allow |
| Rules differ between you and a teammate | A personal allowance landed in the committed file, or your local file is doing work you assumed was shared | Run `/permissions`, which names the source file for every rule, then move each rule to the scope it belongs in |

## Summary

You replaced blanket approval with an explicit, tested policy. Routine builds and read-only git run untouched, a secrets file is denied by path and stays denied through the shell, irreversible commands are refused with no prompt to approve by reflex, and personal convenience lives in a git-ignored override that cannot weaken the shared deny rules.

You can now:

- Write allow rules with the narrowest pattern that covers real usage, and explain what each wildcard grants.
- Deny a path with the correct anchor and verify the block holds through both the Read tool and recognised Bash file commands.
- Predict any rule's outcome from the deny, ask, allow ordering and the scope precedence.
- Spot a rule that parses but never matches, before it is the only thing standing between an agent and your credentials.


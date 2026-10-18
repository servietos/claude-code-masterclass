# Lock Down a Repository With Permission Rules

Permission rules decide what Claude Code will actually allow, independently of what `CLAUDE.md` asks for. You write allow, ask, and deny rules in `.claude/settings.json` until routine builds run untouched, a secrets file is unreachable by any route, and destructive commands are refused outright.

------

Work in `demos/01-fundamentals/05-permissions/permissions-api`; no solution folder ships, so the policy you build lives in a new `permissions-api/.claude/` folder.

## Step 1: Make a secret genuinely unreachable

Run `claude` here once and accept the workspace trust dialog, because allow rules from an untrusted workspace are ignored. Then create `.claude/settings.json` with allow rules for the commands you run constantly and a deny block for the secrets file:

```json
{
  "permissions": {
    "allow": [
      "Bash(dotnet build)",
      "Bash(dotnet test *)",
      "Bash(git log *)"
    ],
    "deny": [
      "Read(./appsettings.Secrets.json)",
      "Read(./secrets/**)",
      "Edit(./secrets/**)"
    ]
  }
}
```

Add `Bash(rm -rf *)`, `Bash(sudo *)`, `Bash(git push --force *)` and `Bash(git reset --hard *)` to the deny list as well. Rules are evaluated deny, then ask, then allow, and the first match wins, so a deny rule cannot carry exceptions. Restart the session and try the shell route, which the Read deny also covers for `cat`, `head`, `tail`, and `sed`. The starter's `CLAUDE.md` already says never to read the file, so lift that rule for this one command; otherwise Claude refuses on its own and the deny rule is never tested:

```text
Permission test: for this one command I lift the CLAUDE.md secrets rule, so the deny rule in .claude/settings.json is the only thing that can stop it. Run exactly: cat appsettings.Secrets.json
```

```text
Permission to use Bash with command cat appsettings.Secrets.json has been denied.
```

## Step 2: Separate team policy from personal overrides

`.claude/settings.json` is committed and binds everyone who clones the repository; `.claude/settings.local.json` is git-ignored and binds only you, and no local file can weaken a deny. Create the local override and add `.claude/settings.local.json` to `.gitignore`:

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

Expected result: `git status --short` does not list `settings.local.json`, `dotnet run` stops prompting for you, and `/permissions` attributes each active rule to a specific file.

## Step 3: Prove the policy holds

A policy you have not tested is a belief. Work through one action per outcome with Claude, one at a time, and have it report which rule in which file produced each outcome:

| Action | Expected outcome | Rule that produces it |
|--------|------------------|-----------------------|
| `dotnet build` | Runs with no prompt | `Bash(dotnet build)` allow, project file |
| `dotnet run` | Runs with no prompt | `Bash(dotnet run)` allow, local file |
| `dotnet nuget push` | Prompts | No rule matches |
| Read `appsettings.Secrets.json` | Refused | `Read(./appsettings.Secrets.json)` deny |
| `cat appsettings.Secrets.json` | Refused | Same deny, applied to a recognised Bash file command |
| `cat TodoApi.csproj` | Runs with no prompt | Built-in read-only command, no rule needed |
| `git push --force origin main` | Refused | `Bash(git push --force *)` deny |

Then restart and read the startup lines: path rules for `Write`, `NotebookEdit`, and `Glob` parse and are never matched, so a clean start without this warning means every rule you wrote matches something:

```text
Permission deny rule (.claude\settings.json): Write(./secrets/**) is not matched by file permission checks — only Edit(path) rules are. Use Edit(./secrets/**) instead (Edit rules cover all file-editing tools).
```

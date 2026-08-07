---
presents: demo-config-to-plugin.md
budget: 4 min
beats: 4
---

# Present: Package, Validate, and Publish a Plugin

Becoming a plugin is a packaging change, not a rewrite: one manifest, one hook wire-up, one catalog entry. Four beats: the manifest, `${CLAUDE_PLUGIN_ROOT}`, what refuses to travel, the catalog pin.

------

**Shell:** beats quote the Git Bash hook; [`hooks/metrics.ps1`](demo-quality-plugin/code-quality-plugin/hooks/metrics.ps1) is the twin for a machine without `jq` or Git Bash, wired as `pwsh -NoProfile -File "${CLAUDE_PLUGIN_ROOT}/hooks/metrics.ps1"` with `"shell": "powershell"` on the entry. Reading the log differs too: `cat ~/.claude/plugins/data/<id>/tool-usage.jsonl` against `Get-Content $env:USERPROFILE\.claude\plugins\data\<id>\tool-usage.jsonl`.

## Beats

### Beat 1: the manifest is the only file the conversion adds (1 min)

**Open:** [`code-quality-plugin/.claude-plugin/plugin.json`](demo-quality-plugin/code-quality-plugin/.claude-plugin/plugin.json) · the `name`, `description` and `version` keys · [What Moves and What Stays](readme.md#what-moves-and-what-stays)
**Say:** A working `.claude/` folder already has the shape a plugin needs, so packaging is a manifest and a folder move. What the manifest adds is identity, and the release tooling reads it from this file alone.

```json
{
  "name": "code-quality-plugin",
  "description": "Bundles a /create-docs command, a brand-voice skill, a code-reviewer skill, and a PostToolUse metrics hook into one installable Code-Quality package.",
  "version": "1.0.0",
  ...
  "license": "MIT",
  "keywords": ["docs", "review", "metrics", "quality"]
}
```

**Result:** `plugin details` resolved the bundle by name and priced it, recorded in [`demo-quality-plugin-solution/readme.md`](demo-quality-plugin-solution/readme.md#step-5-validate-before-publishing)

```text
It prints the component inventory (3 skills, 1 hook) and the projected token cost,
```

**Gotcha:** the release tag `claude plugin tag` writes is `{name}--v{version}`, read from this file and nothing else.

### Beat 2: `${CLAUDE_PLUGIN_ROOT}` resolves only inside the plugin's own hooks.json (1 min)

**Open:** [`code-quality-plugin/hooks/hooks.json`](demo-quality-plugin/code-quality-plugin/hooks/hooks.json) · the `PostToolUse` entry and its `command` line · [The Conversion Lifecycle](readme.md#the-conversion-lifecycle)
**Say:** A plugin ends up at a path its author never sees, so nothing inside it can address its own files absolutely. Outside its scope the variable is not an error, it is an unexpanded string that fails later as a bad path.

```json
...
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/metrics.sh\""
          }
        ]
...
```

**Result:** one JSONL record per tool call at the resolved data path, captured in [`demo-quality-plugin-solution/readme.md`](demo-quality-plugin-solution/readme.md#step-3-inspect-metrics)

```json
{"timestamp":"2026-07-22T20:55:18Z","session_id":"d10342a8","tool_name":"Read","tool_input":{"file_path":"sample-code/inventory.py"},"duration_ms":2,"is_error":false,"cwd":"D:\\demo"}
```

**Gotcha:** a project hook is wired in `settings.json` and addresses its script through `$CLAUDE_PROJECT_DIR`; show the two variables side by side, because that swap is the whole difference.

### Beat 3: model and permission defaults refuse to travel (1 min)

**Open:** [`demo-quality-plugin/project-settings.json`](demo-quality-plugin/project-settings.json) · the whole file, `model` plus `permissions`
**Say:** An installed plugin arrives from another team, so a package that could widen your allow list on install would be a distribution channel for permissions. The line is invisible until something fails to apply.

```json
{
  "model": "claude-sonnet-4-6",
  "permissions": {
    "allow": ["Read", "Grep", "Glob", "Edit", "Write"],
    "deny": ["Bash(rm -rf:*)", "Bash(git push --force:*)"]
  },
  ...
}
```

**Result:** the run left it parked one level above the plugin, and no file inside the packaged tree carries either key: [`demo-quality-plugin-solution/readme.md`](demo-quality-plugin-solution/readme.md#folder-layout)

```text
├── code-quality-plugin/                # the plugin
│   ├── .claude-plugin/plugin.json      # manifest
...
├── project-settings.json               # project-level model and permissions
└── sample-code/
    └── inventory.py                    # target for /create-docs
```

### Beat 4: the catalog is a separate artifact that pins a version (1 min)

**Open:** [Part D: Publish to a Team Catalog](demo-config-to-plugin.md#part-d-publish-to-a-team-catalog) · [Versioning and Release Identity](readme.md#versioning-and-release-identity)
**Say:** Publishing is a second artifact, not a second copy, which is what lets a team curate installs without owning the code. The pin decides which bytes an install receives.

```text
Create a directory acme-plugin-catalog/ containing .claude-plugin/marketplace.json
with name, description, owner, and one plugins entry for quality-review-plugin.
Point the entry at a github source for acme-corp/quality-review-plugin pinned by ref "main".
Show the /plugin marketplace add and /plugin install commands that a teammate would run.
```

**Result:** the run's only new directory, [`acme-plugin-catalog/.claude-plugin/marketplace.json`](demo-quality-plugin-solution/acme-plugin-catalog/.claude-plugin/marketplace.json), repointed from `main` to the release tag

```json
    {
      "name": "code-quality-plugin",
      "source": {
        "source": "github",
        "repo": "acme-corp/code-quality-plugin",
        "ref": "code-quality-plugin--v1.0.0"
      },
      ...
      "version": "1.0.0"
    }
```

**Gotcha:** `ref` takes a branch or a tag and `sha` takes a full 40-character commit, and nothing cross-checks this `version` against `plugin.json`.

## If the room asks

| Question | Answer |
|---|---|
| What did the run actually add? | One directory. `diff -rq` against the starter reports `Only in demo-quality-plugin-solution: acme-plugin-catalog`, plus a differing `readme.md`. |
| What does `claude plugin validate --strict` catch? | Manifest errors, unparseable `SKILL.md` frontmatter (classically an unquoted colon), and invalid hook event names, all otherwise silent no-loads. |
| What does validation miss? | Unknown frontmatter keys pass and are then ignored at runtime, so a reviewer still reads the frontmatter. |
| Why stop at `claude plugin tag --dry-run`? | It tags whichever git repo owns the plugin path, here the course repository, and refuses while anything under that path is uncommitted. |
| Where does the hook log land? | `${CLAUDE_PLUGIN_DATA}` is exported to hook processes only and resolves to `~/.claude/plugins/data/<plugin-id>/`; a `--plugin-dir` load carries the id `<name>-inline`. |

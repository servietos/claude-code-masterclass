# Package, Validate, and Publish a Plugin

Turning a working `.claude/` configuration into something a teammate can install is a packaging step, not a rewrite. You add a `plugin.json` manifest, rewire the hook to `${CLAUDE_PLUGIN_ROOT}` in the plugin's own `hooks.json`, load the result with `--plugin-dir`, validate it, then publish it through a team catalog and a version tag. You end up holding an installable plugin plus the `marketplace.json` entry a teammate installs it from.

------

The [demo-quality-plugin/](demo-quality-plugin/readme.md) folder contains the starter bundle used in this demo.

## Setup

Work directly in the starter:

```bash
cd demo-quality-plugin
claude
```

## Part A: Scaffold the Plugin

Wrap the existing `.claude/` config in a plugin manifest:

```text
Create quality-review-plugin/.claude-plugin/plugin.json with:
  name: "quality-review-plugin"
  description: "Bundles a code-review skill and a PostToolUse metrics hook."
  version: "1.0.0"
  author: { name: "Demo Author", email: "demo@example.com" }
  license: "MIT"

Copy skills/ and hooks/ from .claude/ into quality-review-plugin/.
Add quality-review-plugin/hooks/hooks.json with the PostToolUse entry from .claude/settings.json,
rewritten to the command bash "${CLAUDE_PLUGIN_ROOT}/hooks/metrics.sh".
Do not rename any files.
```

Expected result: a `quality-review-plugin/` directory with the manifest plus all copied components. `settings.json` stays behind in `.claude/`.

## Part B: Test Locally

Load the plugin from disk and confirm the skill and hook are active:

```bash
claude --plugin-dir ./quality-review-plugin
```

Inside the session:

```text
Invoke /quality-review-plugin:code-review against any TypeScript file in this project.
Then check that the hook log has a new entry.
```

The namespaced skill should respond, and the log should show one JSON line per tool call the skill made.

## Part C: Inspect and Validate

Run the two inspection commands before publishing, in a terminal outside the Claude Code session:

```bash
claude plugin validate --strict ./quality-review-plugin
claude --plugin-dir ./quality-review-plugin plugin details quality-review-plugin
```

`details` resolves a plugin by name, so an uninstalled plugin needs the `--plugin-dir` flag in front of the subcommand. Fix any reported issue before continuing.

## Part D: Publish to a Team Catalog

Create the catalog next to the plugin, with the manifest inside `.claude-plugin/`:

```text
Create a directory acme-plugin-catalog/ containing .claude-plugin/marketplace.json
with name, description, owner, and one plugins entry for quality-review-plugin.
Point the entry at a github source for acme-corp/quality-review-plugin pinned by ref "main".
Show the /plugin marketplace add and /plugin install commands that a teammate would run.
```

Validate the catalog, then look at the release tag the catalog would pin to instead of a moving branch. `claude plugin tag` tags the git repo that contains the plugin path, and here that repo is this course repository, so stop at the dry run: it prints the tag it would create without writing one.

```bash
claude plugin validate ./acme-plugin-catalog
claude plugin tag --dry-run ./quality-review-plugin
```

A real release runs that same command without `--dry-run` from the plugin's own repository, which is the only place the tag belongs, and that is exactly why the dry run is the right thing to run here. The command also refuses while anything under the plugin path is uncommitted, so a real release commits the plugin there first.

The tag is `quality-review-plugin--v1.0.0`, with name and version read from `plugin.json` alone. Nothing cross-checks the catalog entry, so bump `marketplace.json` alongside it. Repoint the catalog entry from `ref: "main"` to that tag, or to a full 40-character `sha` when the team needs an exact commit.

The completed, validated result of every step above, including the catalog, is [demo-quality-plugin-solution/](demo-quality-plugin-solution/readme.md).

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/plugin marketplace add <repo-or-path>` | Register the team catalog so its plugins become installable in this session. |
| `/plugin install <plugin>@<marketplace>` | Install the published plugin from the catalog and pick the scope it applies to. |
| `/plugin uninstall <plugin>` | Remove the installed plugin before rerunning the demo from a clean state. |

## Key Topics Covered in This Demo

- [Plugins reference](https://code.claude.com/docs/en/plugins-reference): full `plugin.json` schema, component locations, and the `claude plugin` commands
- [Plugins](https://code.claude.com/docs/en/plugins): the `--plugin-dir` flag and the `/reload-plugins` dev loop
- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces): `marketplace.json` schema and `ref` versus `sha` pinning


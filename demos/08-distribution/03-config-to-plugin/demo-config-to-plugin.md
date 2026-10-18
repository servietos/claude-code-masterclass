# Package, Validate, and Publish a Plugin

Turning a working `.claude/` configuration into something a teammate can install is a packaging step. You add a `plugin.json` manifest, rewire the hook to `${CLAUDE_PLUGIN_ROOT}` in the plugin's own `hooks.json`, load the result with `--plugin-dir`, validate it, then publish it through a team catalog and a version tag.

------

Work directly in the [demo-quality-plugin/](demo-quality-plugin/readme.md) starter bundle; the completed, validated result, including the catalog, is [demo-quality-plugin-solution/](demo-quality-plugin-solution/readme.md).

## Part A: Scaffold the Plugin

The starter already holds the packaged tree, so this step checks the conversion:

```text
Read quality-review-plugin/.claude-plugin/plugin.json and confirm it has
  name: "quality-review-plugin", version: "1.0.0", license: "MIT".
Read quality-review-plugin/hooks/hooks.json and confirm its PostToolUse command is
  bash "${CLAUDE_PLUGIN_ROOT}/hooks/metrics.sh".
Confirm skills/ and hooks/ sit under quality-review-plugin/ with their filenames unchanged.
Change no file. Report each check as pass or fail.
```

Expected result: a report with every check passing and no file changed. `project-settings.json` stays beside the plugin, outside its tree.

## Part B: Inspect and Validate

Run the two inspection commands before publishing, in a terminal outside the Claude Code session:

```bash
claude plugin validate --strict ./quality-review-plugin
claude --plugin-dir ./quality-review-plugin plugin details quality-review-plugin
```

`details` resolves a plugin by name, so an uninstalled plugin needs the `--plugin-dir` flag in front of the subcommand. Fix any reported issue before continuing.

## Part C: Publish to a Team Catalog

Create the catalog next to the plugin, with the manifest inside `.claude-plugin/`:

```text
Create a directory acme-plugin-catalog/ containing .claude-plugin/marketplace.json
with name, description, owner, and one plugins entry for quality-review-plugin at version 1.0.0.
Point the entry at a github source for acme-corp/quality-review-plugin pinned by ref "main".
Show the /plugin marketplace add and /plugin install commands that a teammate would run.
```

Validate the catalog, then dry-run the release tag. `claude plugin tag` tags the git repo that contains the plugin path, and here that repo is this course repository, so stop at the dry run: it prints the tag it would create without writing one.

```bash
claude plugin validate ./acme-plugin-catalog
claude plugin tag --dry-run ./quality-review-plugin
```

The tag is `quality-review-plugin--v1.0.0`, with name and version read from `plugin.json` alone, so bump `marketplace.json` alongside it. Repoint the catalog entry from `ref: "main"` to that tag, or to a full 40-character `sha` when the team needs an exact commit:

```json
      "source": {
        "source": "github",
        "repo": "acme-corp/quality-review-plugin",
        "ref": "quality-review-plugin--v1.0.0"
      },
```

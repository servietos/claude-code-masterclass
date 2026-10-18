# Bundle and Distribute Your Config as a Plugin

A `.claude/` directory works perfectly for one developer on one machine. The moment a second developer needs the same skills, hooks, and sub-agent definitions, copy-paste and git submodules become the answer, and that answer does not scale. Plugins convert a working local config into a versioned, installable unit with a name, a manifest, and a one-command install path that every teammate can reproduce.

This module covers the full plugin lifecycle: why plugins exist, what the manifest and component tree look like, how to convert an existing `.claude/` config into a publishable plugin, and how marketplace catalogs let enterprises pin, curate, and govern what their teams install.

- Plugins vs. standalone configuration: namespacing
- Plugin anatomy: manifest, skills, hooks, MCP
- Bundling skills, hooks, and MCP configs
- LSP servers and background monitors
- Default agent activation via plugin settings
- Testing with --plugin-dir and /reload-plugins
- Converting `.claude/` configs into plugins
- Release tags and version identity
- Publishing to official and team marketplaces

## Topics

| Topic | Description |
|-------|-------------|
| [01: Why Plugins Exist](01-why-plugins/readme.md) | The distribution problem standalone `.claude/` cannot solve, the trade-off table between standalone and plugin form, and the namespacing cost that is the only real difference between them. |
| [02: Plugin Anatomy](02-plugin-anatomy/readme.md) | The single required manifest file and the optional component tree around it: skills, hooks, MCP, LSP servers, monitors, default settings, and the two plugin-scoped environment variables. |
| [03: From .claude/ Config to Published Plugin](03-config-to-plugin/readme.md) | What a working `.claude/` directory gains and loses on the way to becoming a plugin: the component mapping, the hook and `settings.json` rules that change form, the local-load inner loop, and the release tag read from `plugin.json` alone. |
| [04: Marketplaces and Distribution](04-marketplaces/readme.md) | Catalog versus plugin source separation, `ref` versus `sha` pinning, enterprise controls in managed policy, reserved names, and the security posture every install should pass. |

## Demos

| Topic | Description |
|-------|-------------|
| [03: From .claude/ Config to Published Plugin](03-config-to-plugin/demo-config-to-plugin.md) | Convert a working `.claude/` directory into a versioned plugin, test it locally with `--plugin-dir`, inspect and validate the manifest, and publish it to a team marketplace catalog. |

Every demo has a presenter guide beside it (`demo-presenter-<slug>.md`) holding the same
teaching in timed beats, for delivery without running the demo live.

## Starter and Solution Folders

Work in each topic's starter (for example `demo-quality-plugin/`); the finished, runnable result is beside it in `<starter>-solution/`.

## Labs

| Lab | Description |
|-----|-------------|
| [Build a Plugin From a `.claude/` Configuration](../../labs/08-distribution/lab-01-build-a-plugin.md) | Convert a working configuration of skills, hooks, slash commands and an MCP server into a self-contained plugin, tested with `--plugin-dir`. |
| [Audit a Plugin Before You Install It](../../labs/08-distribution/lab-02-plugin-security.md) | Audit a real plugin's manifest, hooks, MCP servers and skills for attack patterns, then write a malicious mini-plugin and name the red flags. |

## Knowledge Check

### CQ-01: The Only Required File

What is the minimum a directory needs to be a valid plugin?

- A) A `.claude-plugin/plugin.json` manifest; every other component is optional.
- B) A manifest plus at least one skill, since a plugin with no components cannot be installed.
- C) A manifest plus a `settings.json` declaring which components to activate.
- D) A manifest, a `hooks/hooks.json`, and a `.mcp.json`, which together define the plugin surface.

**Answer: A**

The manifest at `.claude-plugin/plugin.json` is the single mandatory file. Everything else exists to extend that root, and you ship only the components you actually have. Requiring more would make a plugin that bundles a single MCP config impossible.

### CQ-02: The Layout Mistake That Fails Silently

A developer places `skills/`, `agents/`, and `hooks/` inside `.claude-plugin/` next to the manifest. What happens?

- A) The harness loads them but namespaces them under a reserved prefix.
- B) The harness loads nothing it finds there and does not warn, which is why `claude plugin validate` exists.
- C) The plugin fails to install with an explicit layout error.
- D) The components load, but only after `/reload-plugins` is run once.

**Answer: B**

Only `plugin.json` belongs inside `.claude-plugin/`. Everything else lives at the plugin root beside it, and misplaced components are silently ignored rather than reported. That silence is exactly why the validate command is part of the publishing routine.

### CQ-03: Disabling a Dependency

A plugin `invoice-parser` declares a dependency on `currency-converter`, and both are enabled. Running `claude plugin disable currency-converter` produces what result?

- A) It succeeds, and `invoice-parser` is automatically disabled too, to maintain integrity.
- B) It succeeds, and `invoice-parser` stays enabled but fails at runtime when it calls the missing dependency.
- C) It fails, because an enabled plugin depends on the one being disabled.
- D) It succeeds after prompting for a replacement implementation to substitute.

**Answer: C**

Claude Code enforces declared plugin dependencies, so the command is rejected and both plugins stay as they were. The correct sequence is to disable the dependent first, then its dependency. It neither cascades the disable nor leaves a dependent broken.

### CQ-04: Where a Plugin Writes Its State

A plugin ships a script in its tree and needs to cache results between sessions. Which variables apply?

- A) `${CLAUDE_PLUGIN_ROOT}` for both, since the plugin owns its whole directory.
- B) `${CLAUDE_PLUGIN_ROOT}` for the bundled script path, `${CLAUDE_PLUGIN_DATA}` for the cache.
- C) `${CLAUDE_PLUGIN_DATA}` for both, since runtime resolution is more portable.
- D) Neither; plugins must use absolute paths resolved at install time.

**Answer: B**

`CLAUDE_PLUGIN_ROOT` points at the installation directory and is for anything shipped in the tree. `CLAUDE_PLUGIN_DATA` is a persistent directory that survives across sessions and is for anything written at runtime. Mixing them is the bug that breaks a plugin on the second machine, where the install path differs but the data path is what the plugin owns.

### CCA-F Q31 (Domain 2: Tool Design and MCP Integration)

An architect is maintaining a complex project using `Claude Code`, which relies on several custom plugins. The `invoice-parser` plugin has a declared dependency on the `currency-converter` plugin. Both plugins are currently enabled. The architect attempts to disable the `currency-converter` plugin by running the command `claude plugin disable currency-converter`. Based on the documented behavior for plugin dependency handling in `Claude Code`, what is the expected outcome?

- A) The command will succeed, and the architect will be prompted to provide an alternative implementation or a mock for the `invoice-parser` plugin to use.
- B) The `currency-converter` plugin will be disabled, and the `invoice-parser` plugin will be automatically disabled as well to maintain dependency integrity.
- C) The command will succeed, disabling the `currency-converter` plugin. The `invoice-parser` plugin will remain enabled but will fail at runtime when it attempts to call the missing dependency.
- D) The command will fail, and `Claude Code` will prevent the `currency-converter` plugin from being disabled because the enabled `invoice-parser` plugin depends on it.

**Answer: D**

According to Anthropic's documentation, Claude Code enforces plugin dependencies to maintain system integrity. Attempting to disable a plugin that is a required dependency for another enabled plugin will result in the command failing. The recommended approach is to first disable the dependent plugin (invoice-parser) before disabling its dependency (currency-converter).

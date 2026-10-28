# Inspect Plugin Anatomy

## One Required File, Everything Else Optional

A plugin is just a directory with a single mandatory file at `.claude-plugin/plugin.json`. Everything else, skills, hooks, MCP, sub-agents, scripts, exists to extend that root, and you ship only the components you actually have. The layout is deliberately flat so a contributor can read the tree once and know where every artifact lives.

```text
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # Required: manifest
├── skills/                  # Skills as <name>/SKILL.md
│   └── code-review/
│       └── SKILL.md
├── agents/                  # Sub-agent definitions
├── hooks/
│   └── hooks.json           # PreToolUse, PostToolUse, etc.
├── .mcp.json                # MCP servers
├── .lsp.json                # LSP servers
├── monitors/
│   └── monitors.json        # Background monitors
├── bin/                     # Added to Bash PATH while enabled
└── settings.json            # Default agent, applied on enable
```

## The Manifest

The manifest is short, declarative, and the only file the harness strictly requires. Name, version, and description carry the social weight; repository and author make the plugin auditable; license tells installers what they are agreeing to.

```json
{
  "name": "quality-review-plugin",
  "description": "Adds a /quality-review skill for quick code reviews",
  "version": "1.0.0",
  "author": { "name": "Your Name", "email": "you@example.com" },
  "repository": "https://github.com/you/quality-review-plugin",
  "license": "MIT"
}
```

The `name` field doubles as the skill namespace, so `quality-review-plugin` exposes its `hello` skill as `/quality-review-plugin:hello`. Pick a name that is unique on the marketplaces you publish to and stable across versions, because changing it later is a breaking rename for every installer.

## The Common Mistake

The single most frequent layout error is nesting components inside `.claude-plugin/`. Only `plugin.json` belongs in that folder; `commands/`, `agents/`, `skills/`, and `hooks/` all live at the plugin root next to it. The harness will load nothing it finds in the wrong place and will not warn you, which is why `claude plugin validate` exists as a sanity check before publishing.

## Advanced Components

Three component types go beyond what most teams build in a local `.claude/` and unlock the "plugin makes this trivial" pitch. LSP servers in `.lsp.json` add jump-to-definition and diagnostics for whatever language your agent works in, so a code-review plugin can actually navigate the code it reviews. Background monitors in `monitors/monitors.json` start with the session or the first time one of the plugin's skills is invoked, and everything they print reaches Claude as a notification, with classic uses being a CI-watcher that flags failures and a dev-server log tailer that surfaces stack traces without the user having to wire it up.

A plugin-root `settings.json` is far narrower than the project settings file it resembles: only `agent` and `subagentStatusLine` are honoured, so it can activate a default sub-agent on enable and nothing more. Model, permissions, and env keys placed there are dropped at load, which makes a plugin `settings.json` a common source of "I shipped it and nothing happened" reports. Keep those defaults in the project's `.claude/settings.json` and use the plugin for components: hooks for hard guardrails, monitors for ambient watchers.

## Declared Dependencies and Disable Order

A plugin can declare that it depends on another, and Claude Code enforces that declaration rather than trusting the installer to remember it. The practical consequence shows up at disable time, not install time.

Running `claude plugin disable currency-converter` while an enabled `invoice-parser` depends on it **fails**. The command is rejected and both plugins stay enabled. Claude Code does not disable the dependency and leave the dependent broken, and it does not cascade the disable to the dependent either; it refuses and tells you why.

```bash
claude plugin disable invoice-parser
claude plugin disable currency-converter
```

Disable the dependent first, then its dependency. The same ordering applies to uninstalls. This is the behavior to expect on any plugin whose manifest declares a dependency, and it is why a plugin tree that grows dependencies needs its removal order documented alongside its install order.

## Plugin-Scoped Environment Variables

Two variables are populated automatically inside hook and MCP configs so you can reference resources the plugin ships without hard-coding paths.

| Variable | What it points at |
|---|---|
| `${CLAUDE_PLUGIN_ROOT}` | The plugin's installation directory, used for paths to bundled scripts and assets |
| `${CLAUDE_PLUGIN_DATA}` | A persistent data directory that survives across sessions, `~/.claude/plugins/data/<plugin-id>`, used for caches and state files |

Use `CLAUDE_PLUGIN_ROOT` for anything you ship in the plugin tree and `CLAUDE_PLUGIN_DATA` for anything the plugin writes at runtime, never the other way around. Mixing them up is the bug that breaks plugins on the second machine, because the install path differs but the data path is what the plugin actually owns.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/plugin` | List currently loaded plugins and the components each one contributes so you can confirm the manifest resolved correctly |
| `/reload-plugins` | Re-read the plugin tree after editing the manifest or any component file during local development |
| `/doctor` | Health check the installation, MCP servers, and hooks after adding a component to the plugin tree |

## Key Topics covered in this module

- [Plugins Reference](https://code.claude.com/docs/en/plugins-reference): the full schema for `plugin.json`, the component locations, and the plugin-scoped variables
- [Hooks Reference](https://code.claude.com/docs/en/hooks): how plugin-shipped hooks compose with user and project hooks at runtime
- [MCP Servers](https://code.claude.com/docs/en/mcp): packaging `.mcp.json` so installs are reproducible across machines

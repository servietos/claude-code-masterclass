# Package and Distribute Plugins

Copying a `.claude/` folder between repositories is how a team ends up with five drifting versions of the same hook. A plugin makes it one install, and one version bump reaches everybody:

```shell
/plugin install pr-review-toolkit@claude-plugins-official
```

The review agents that plugin contributes then behave exactly as if someone had authored them in this repo's `.claude/agents/`, with no per-repo setup and nothing to keep in sync by hand.

A plugin is the distribution wrapper around the harness components this module builds: slash commands, hooks, MCP server configuration, skills, and sub-agents. Everything in topics 02 through 09 lives loose in a `.claude/` directory that exists in exactly one checkout, and a plugin turns that same directory into a versioned unit a team installs once and receives everywhere. Nothing about how a command, hook, or skill is authored changes when it moves into a plugin, so this topic exists only to name the wrapper.

[Module 10: Bundle and Distribute Your Config as a Plugin](../../10-distribution/readme.md) owns the full treatment. Read [01: Why Plugins Exist](../../10-distribution/01-why-plugins/readme.md) for the standalone-versus-plugin trade-off, [02: Plugin Anatomy](../../10-distribution/02-plugin-anatomy/readme.md) for the manifest and the component layout around it, [03: From .claude/ Config to Published Plugin](../../10-distribution/03-config-to-plugin/readme.md) for local testing with `--plugin-dir` and the hot-reload authoring loop, and [04: Marketplaces and Distribution](../../10-distribution/04-marketplaces/readme.md) for catalogs, pinning, and enterprise controls.

## Plugins by Anthropic

Claude Code registers the official Anthropic marketplace (`claude-plugins-official`) automatically the first time you start it interactively. If that fails because the network blocked the download or a marketplace policy denied an earlier attempt, add it yourself:

```shell
/plugin marketplace add anthropics/claude-plugins-official
```

Everything in it installs the same way, and `/plugin` shows the catalog with a context-cost estimate per plugin in the Discover tab:

```shell
/plugin install <name>@claude-plugins-official
```

These are the Anthropic-authored plugins that package the same component types this module builds:

| Plugin | What it contributes |
|--------|---------------------|
| `claude-code-setup` | Analyzes a codebase and recommends the hooks, skills, MCP servers, and sub-agents worth adding to it |
| `plugin-dev` | Toolkit for authoring your own plugins, with skills for hooks, commands, agents, and MCP integration |
| `hookify` | Turns an observed unwanted behavior into a hook, defined as a Markdown rule file |
| `skill-creator` | Creates and improves skills, and runs evals to measure whether a skill actually fires |
| `mcp-server-dev` | Skills for designing MCP servers: deployment models, tool design, and auth |
| `claude-md-management` | Audits `CLAUDE.md` quality and folds session learnings back into project memory |
| `commit-commands` | Git commit, push, and PR creation workflows |
| `pr-review-toolkit` | Review agents specialized by lens: tests, error handling, type design, simplification |
| `security-guidance` | Reviews each change Claude makes for injection, XSS, SSRF, hardcoded secrets, and related classes |
| `typescript-lsp` and siblings | Language server wiring so Claude sees type errors right after an edit; one plugin per language, binary installed separately |

Anthropic also publishes a community marketplace of screened third-party plugins, added manually and installed under the `claude-community` name:

```shell
/plugin marketplace add anthropics/claude-plugins-community
```

## Helpful Claude Slash Commands

| Command | Usage |
|---------|-------|
| `/plugin` | Browse marketplaces and list loaded plugins with the components each one contributes. |
| `/doctor` | Health check the installation, MCP servers, and hooks after adding a plugin to the session. |

## Key Topics covered in this module

- [Claude Code Plugins](https://code.claude.com/docs/en/plugins): when a plugin beats a standalone `.claude/` config, and the `--plugin-dir` development flag
- [Plugins Reference](https://code.claude.com/docs/en/plugins-reference): the manifest schema and where each component type lives inside a plugin
- [Plugin Marketplaces](https://code.claude.com/docs/en/plugin-marketplaces): catalog schema, source types, and the pinning model

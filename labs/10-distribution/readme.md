# Labs - Module 10: Bundling & Distributing Plugins

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Authoring | [Build a Plugin From a `.claude/` Configuration](lab-01-build-a-plugin.md) | Core | Intermediate | 1h | Convert a working `.claude/` configuration (skills, hooks, slash commands, and an MCP server) into a self-contained Claude Code plugin. Test it locally with `--plugin-dir` and `/reload-plugins`. |
| 02 | Security | [Audit a Plugin Before You Install It](lab-02-plugin-security.md) | Optional | Intermediate | 45m | The marketplace is open and anyone can publish. Audit a real plugin's manifest, hooks, MCP servers, and skills for attack patterns. Then write a deliberately malicious mini-plugin and identify the red flags that would have caught it. |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 1h. All labs: 1h 45m.

Lab 01 is Core because packaging your own harness into a distributable plugin is the module's central capability; Lab 02 turns the same knowledge around to audit someone else's.

Lab 01 covers the *producer* side. Lab 02 covers the *defender* side: the most important plugin skill is the one that keeps you from installing a malicious one. Publishing a plugin to a public marketplace is intentionally not covered as a workflow; if you need it, Anthropic's [`plugin-dev`](https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev) plugin automates the entire process with `/plugin-dev:create-plugin`.

Lab 01 is also where the *consumer* side gets its counterpart: this module carries the threat model that should accompany every install.

Both labs write real `.claude/` and plugin trees. Build them inside this module folder (`01-build/` and `02-security/`), not inside a project you work in, so the lab's skills and its write-blocking hook never join your live roster. Lab 01 does not scaffold its source configuration: the starter is checked in at [`01-build/notes-toolkit-source/`](01-build/notes-toolkit-source/), and the lab packages it into a plugin tree beside it.

The completed references live beside your work as [`01-build/notes-toolkit-solution/`](01-build/notes-toolkit-solution/) and [`02-security/malicious-example-solution/`](02-security/malicious-example-solution/), with [`01-build/notes-toolkit-source-solution/`](01-build/notes-toolkit-source-solution/) as a pristine copy of the Lab 01 starter to diff against. The malicious example is a teaching artifact only: read it, never install it.

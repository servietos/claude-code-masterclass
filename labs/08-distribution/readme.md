# Labs - Module 08: Bundling & Distributing Plugins

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Authoring | [Build a Plugin From a `.claude/` Configuration](lab-01-build-a-plugin.md) | Core | Intermediate | 1h | Convert a working `.claude/` configuration (skills, hooks, slash commands, and an MCP server) into a self-contained Claude Code plugin. Test it locally with `--plugin-dir` and `/reload-plugins`. |
| 02 | Security | [Audit a Plugin Before You Install It](lab-02-plugin-security.md) | Optional | Intermediate | 45m | The marketplace is open and anyone can publish. Audit a real plugin's manifest, hooks, MCP servers, and skills for attack patterns. Then write a deliberately malicious mini-plugin and identify the red flags that would have caught it. |
| 03 | Publishing | [Publish a Plugin Through a Team Catalog](lab-03-publish-to-a-team-catalog.md) | Optional | Intermediate | 1h 15m | Release the Lab 01 plugin through an `acme` team catalog: validate it, tag a release, write `marketplace.json`, install as a teammate, then repoint the entry from a branch to the release tag and a full 40-character sha. |
| 04 | Orchestration | [Route and Brief Subagents With a Mod](lab-04-orchestrate-with-a-mod.md) | Optional | Advanced | 1h 5m | Write `desk-router`, a mod that hints lookups to a read-only Haiku scout, briefs and reroutes every subagent spawn, and keeps a ledger you print with `/desk`. Pin the routing with `claude plugin test`, then install the mod from a catalog at project scope. |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 1h. All labs: 4h 5m.

Lab 01 is Core because packaging your own harness into a distributable plugin is the module's central capability; Lab 02 turns the same knowledge around to audit someone else's.

Lab 01 covers the *producer* side. Lab 02 covers the *defender* side: the most important plugin skill is the one that keeps you from installing a malicious one. Lab 03 publishes the Lab 01 plugin through a team catalog with a release tag and a sha pin; Anthropic's [`plugin-dev`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/plugin-dev) plugin automates scaffolding with `/plugin-dev:create-plugin`.

Lab 01 is also where the *consumer* side gets its counterpart: this module carries the threat model that should accompany every install.

Labs 01 and 02 write real `.claude/` and plugin trees. Build them inside this module folder (`01-build/` and `02-security/`), away from any project you work in, so the lab's skills and its write-blocking hook never join your live roster. Lab 01 does not scaffold its source configuration: the starter is checked in at [`01-build/notes-toolkit/`](01-build/notes-toolkit/), and the lab packages it into a plugin tree beside it, `01-build/notes-toolkit-plugin/`.

The completed references live beside your work as [`01-build/notes-toolkit-solution/`](01-build/notes-toolkit-solution) and [`02-security/malicious-example-solution/`](02-security/malicious-example-solution). The malicious example is a teaching artifact only: read it, never install it.

Lab 03 builds in [`03-publish/release-desk/`](03-publish/release-desk/), whose `notes-toolkit/` folder is the finished Lab 01 plugin. The completed catalog lives beside it as [`03-publish/release-desk-solution/`](03-publish/release-desk-solution). The lab registers the `acme` marketplace on your machine and its last step removes it.

Lab 04 builds in [`04-orchestrate/delegation-desk/`](04-orchestrate/delegation-desk/), which holds a small `shop-api/` and the bare `desk-router/` manifest. The completed mod and its catalog live beside it as [`04-orchestrate/delegation-desk-solution/`](04-orchestrate/delegation-desk-solution). The lab installs the mod at project scope, into the starter's own `.claude/settings.json`, and its last step removes it.

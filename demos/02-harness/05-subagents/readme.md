# Delegate Work to Sub-Agents

Delegating keeps the searching out of your own context window: the sub-agent reads fifty files and hands back the paragraph that mattered. That is what makes a long session survivable, and it is also what lets independent work run at the same time.

```text
Use the review-security-agent to check demos/07-agent-teams/02-parallel-review/catalog-service-cs
for anything an anonymous caller can reach.
```

```text
Run the security and performance reviewers over that same project in parallel and merge
their findings into one list.
```

Both agents are defined in this repo's `.claude/agents/`. The orchestrating session receives their summaries, never the file reads that produced them.

A sub-agent is a harness file type like every other one in this module: a Markdown file with YAML frontmatter under `.claude/agents/`, discovered at session start alongside the commands in `.claude/commands/`, the hooks wired in `settings.json`, the skills in `.claude/skills/`, and anything a plugin contributes. The main session spawns one through the `Agent` tool with a self-contained prompt and receives a summary back, so the delegated work never lands in the orchestrator's own context window. This topic exists to complete the harness inventory; what a sub-agent file contains and how several of them are coordinated is a module of its own.

[Module 6: Scale task execution with sub-agents](../../06-subagents/readme.md) owns the full treatment across six topics and five demos. [01: Introduction](../../06-subagents/01-introduction/readme.md) covers the frontmatter field by field, including `tools`, `disallowedTools`, `permissionMode`, and `mcpServers`, plus how the allowlist and denylist resolve against each other. [06: Orchestration Patterns](../../06-subagents/06-orchestration/readme.md) covers decomposition, orchestrator prompts, convergent loops, workflow graphs, and the schema-validated contracts that hold between agents.

## Give a Global Sub-Agent Your Repo's Facts

A sub-agent loads the same `CLAUDE.md` files and project rules as the main session. So one definition in `~/.claude/agents/` can serve every repository, and each repository keeps what differs (app root, ports, schema folder, who runs the dev server) in its own `.claude/rules/`. The global agent picks those facts up wherever it runs, and no repository needs its own copy of the agent.

```markdown
# Orders API

- Root `src/orders-api/`, `OrdersDbContext`, schema scripts in `db/deltas/`
- The user runs the API on https://localhost:5051; never restart it
- Debug login for auth-gated calls: see `.github/credentials.json`
```

Saved as `.claude/rules/orders-api.md` with no `paths:`, this rule reaches every sub-agent at start. A definition that sets `omitClaudeMd: true` skips `CLAUDE.md` and rules entirely, and the built-in Explore and Plan agents always skip them.

## Helpful Claude Slash Commands

| Command | Usage |
|---------|-------|
| `/agents` | Print where sub-agent definitions live, so you can go read the files under `.claude/agents/` or `~/.claude/agents/`. |
| `/context` | Visualize context distribution across the session, which is what delegating to a sub-agent is meant to protect. |

## Key Topics Covered in This Module

- [Sub-agents](https://code.claude.com/docs/en/sub-agents): file location, frontmatter fields, and how a sub-agent is invoked
- [Claude Code Settings](https://code.claude.com/docs/en/settings): where session-wide permission rules apply, sub-agents included

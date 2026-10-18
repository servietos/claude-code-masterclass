# Explore the Harness Elements

## What is the Claude Code Harness?

The harness is the configuration layer that surrounds Claude Code and shapes everything Claude perceives, decides, and is allowed to do in a session. The model itself is stateless; the harness is what turns a generic LLM into a project-aware, rule-following engineering assistant.

It is composed of several file types, each responsible for a distinct aspect of Claude's behavior:

| File / Location | Purpose |
|-----------------|---------|
| [`CLAUDE.md`](../02-constitution/readme.md) | Injects project rules, architecture context, and coding standards into every turn |
| `settings.json` | Controls permissions, environment variables, model choice, and the hook registrations that bind commands to events |
| [`.mcp.json`](../../04-mcp/readme.md) | Registers Model Context Protocol servers that extend Claude with external tools |
| [`.claude/commands/`](../03-commands/readme.md) | Stores custom slash commands that package reusable multi-step workflows |
| [`.claude/skills/`](../../03-skills/readme.md) | Holds installable agent skills that add domain-specific capabilities |
| [`.claude/agents/`](../../06-subagents-agent-teams/readme.md) | Defines subagents with their own prompt, tool set, and model, so domain work routes to an owning expert |
| [`.claude/hooks/`](../04-hooks-mods/readme.md) | Holds the scripts that hook registrations execute on events like `PreToolUse`, `PostToolUse`, and `Stop` |
| [`.claude/rules/`](../02-constitution/readme.md#path-scoped-rules) | Holds Markdown rule files: without `paths:` they load at session start like `CLAUDE.md`, with `paths:` only when Claude touches a matching file |
| [`MEMORY.md`](../05-memory/readme.md) | Holds the auto-memory index and the memory files Claude saves across sessions |

Together these files define the rules, context, tools, permissions, and behaviors Claude uses before it reads a single line of your codebase.

Tuning the harness is the highest-leverage investment in an agentic workflow because improvements apply to every turn in every session, not just a single prompt.

## Benefits of a Well-Configured Harness

A harness reduces the cost of every interaction. Without one, each session starts from scratch and the engineer must re-explain project conventions, tech stack, and constraints. With one, Claude arrives pre-loaded with that context and can act immediately.

Key benefits:

- Rules in `CLAUDE.md` prevent repeated mistakes and enforce coding standards automatically.
- Permission allowlists in `settings.json` cut approval prompts for safe, read-only tools.
- Custom slash commands package multi-step workflows into a single invocable phrase.
- MCP servers extend Claude with domain-specific tools (browser control, cloud APIs, documentation search) without writing agent code.
- Hooks fire shell commands on events (`PreToolUse`, `Stop`) to enforce guardrails, log actions, or run formatters.

## Where to Store Harness Files

Claude resolves harness configuration from three locations in priority order:

| Scope | Location | Who sees it |
|-------|----------|-------------|
| User (global) | `~/.claude/` | Every project on the machine |
| Project | `<repo>/.claude/` | Everyone who checks out the repo |
| Session | Passed at runtime via `--append-system-prompt` | Single session only |

`settings.json` and `.mcp.json` both support all three scopes. `CLAUDE.md` files are resolved from the working directory upward and merged, so a repo-root `CLAUDE.md` and a nested `src/CLAUDE.md` stack on top of each other. On Team and Enterprise plans a fourth scope sits above all three (see [Team and Enterprise Harness Management](#team-and-enterprise-harness-management)).

```text
~/.claude/                  ← global (user-level) harness
  settings.json
  CLAUDE.md
  commands/
  skills/

<repo>/.claude/             ← project harness (committed to git)
  settings.json
  CLAUDE.md
  commands/
  skills/
  agents/
```

## Global vs. Repo-Specific Harness

Choosing where to put a harness file is a trade-off between sharing and control.

### Global (`~/.claude/`)

Global harness files apply to every project and every session on the machine. They are ideal for personal preferences that do not belong in a shared codebase: preferred response style, personal tool permissions, API keys for private MCP servers, or keyboard shortcuts. Because they live outside any repo, they never appear in pull requests and do not affect teammates.

Use global configuration for:
- Personal productivity shortcuts (`/review`, `/security-review` triggered on demand)
- Private MCP servers with credentials that should not be committed
- Permissions for tools you trust universally (`Bash`, `Read`, common CLIs)
- `CLAUDE.md` entries about how you prefer to work

### Repo-Specific (`.claude/` committed to git)

Project harness files travel with the repository. Every teammate who checks out the repo gets the same Claude behavior: the same rules, the same commands, the same MCP servers, the same hooks. This is critical for consistency in team settings: onboarding a new developer means they automatically inherit the team's Claude conventions without any manual setup.

Use project configuration for:
- `CLAUDE.md` with architecture decisions, coding standards, and domain context
- Custom slash commands that encode team workflows (`/create-pr`, `/run-migrations`)
- MCP server registrations for shared tools (GitHub, Azure, project databases)
- Hook scripts that enforce required checks before Claude stops (linting, tests)
- Permission allowlists for tools every team member uses

### Deciding Which Scope to Use

A good rule of thumb: if a teammate would benefit from the same config, put it in the repo. If it reflects personal preference or contains secrets, put it in `~/.claude/`. When a setting appears in both scopes, the project-level file wins, allowing teams to override global defaults with repo-specific requirements.

```text
Prompt: What settings belong in global vs. project harness?
Describe the difference between ~/.claude/settings.json and .claude/settings.json,
and give me three concrete examples of configuration that belongs in each scope.
```

## Team and Enterprise Harness Management

Everything above assumes each developer owns their own harness. Organization plans add a layer on top: harness configuration an administrator ships to every machine, which no user or project file can override. Team plans cover centralized billing, admin tools, and a usage dashboard; Enterprise adds SSO, role-based permissions, and managed policy settings.

Key takeaways:

- **Managed settings are a fourth scope above all three.** They outrank local, project, and user settings, and even command line arguments, which is what makes them a security control rather than a suggestion. They live at `/Library/Application Support/ClaudeCode/managed-settings.json` (macOS), `/etc/claude-code/managed-settings.json` (Linux and WSL), or `C:\Program Files\ClaudeCode\managed-settings.json` (Windows), and can also arrive via MDM, the Windows registry, or the claude.ai admin console.
- **Policy can lock down every harness file type.** `allowManagedPermissionRulesOnly` discards user and project permission rules, `allowedMcpServers` and `deniedMcpServers` restrict MCP servers, `allowManagedHooksOnly` restricts hooks, `strictKnownMarketplaces` restricts plugin sources, and `forceLoginOrgUUID` binds the CLI to one organization.
- **Invalid policy fails safe.** A bad entry is stripped with a warning while the rest stays enforced, so a typo cannot silently disable a policy. Run `/doctor` to see what was stripped and where it came from.
- **The same system directories accept a `CLAUDE.md`** for company-wide standards, merged with the repo-level and user-level files rather than replacing them.
- **Plugin marketplaces distribute the harness across repos.** Package commands, skills, subagents, and hooks as a versioned plugin so every developer installs and updates from one source, instead of copying `.claude/` folders between repositories.
- **Ownership splits three ways.** A platform team owns the managed settings and the organization `CLAUDE.md`, each product team owns its repo `.claude/`, and individuals keep only personal preferences in `~/.claude/`.

```text
Prompt: Draft a managed-settings.json for our organization.
Deny reads of .env files and destructive shell commands, allowlist only the
github and postgres MCP servers, pin a minimum CLI version, and explain which
of these a developer could still override locally.
```

## Helpful Claude Slash Commands

| Command | Usage |
|---------|-------|
| `/update-config` | Edit `settings.json` to configure permissions, env vars, hooks, and scopes. |
| `/config` | Open the interactive settings panel to manage preferences and model selection. |
| `/doctor` | Diagnose the resolved harness: which config files loaded and which entries were stripped. |

## Key Topics Covered in This Module

- [Claude Code Settings](https://code.claude.com/docs/en/settings): settings hierarchy, scopes, and permission model
- [Enterprise Deployment](https://code.claude.com/docs/en/third-party-integrations): organization rollout, managed policy settings, and shared configuration
- [Claude Code in Action course](https://anthropic.skilljar.com/claude-code-in-action/303241)

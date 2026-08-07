# Understand the Claude Code Harness

Without a harness, every session opens by re-explaining the same project, and every safe command still waits for an approval click:

```text
We use Angular 21 with signals and standalone components, .NET 10 for the API, and
the EF Core migrations live under src/Api/Migrations. Never edit generated files.
Now add a health endpoint and wire it into the existing controller pattern.
```

With that context in `CLAUDE.md` and the read-only tools allowlisted in `settings.json`, the same work is one line, and every teammate who checks out the repo gets identical behavior:

```text
Add a health endpoint to the API.
```

## What is the Claude Code Harness?

The harness is the configuration layer that surrounds Claude Code and shapes everything Claude perceives, decides, and is allowed to do in a session. The model itself is stateless; the harness is what turns a generic LLM into a project-aware, rule-following engineering assistant.

It is composed of several file types, each responsible for a distinct aspect of Claude's behavior:

| File / Location | Purpose |
|-----------------|---------|
| `CLAUDE.md` | Injects project rules, architecture context, and coding standards into every turn |
| `settings.json` | Controls permissions, environment variables, model choice, and the hook registrations that bind commands to events |
| `.mcp.json` | Registers Model Context Protocol servers that extend Claude with external tools |
| `.claude/commands/` | Stores custom slash commands that package reusable multi-step workflows |
| `.claude/skills/` | Holds installable agent skills that add domain-specific capabilities |
| `.claude/agents/` | Defines subagents with their own prompt, tool set, and model, so domain work routes to an owning expert |
| `.claude/hooks/` | Holds the scripts that hook registrations execute on events like `PreToolUse`, `PostToolUse`, and `Stop` |
| `.claude/rules/` | Holds Markdown rule files that load only for the file paths named in their frontmatter |

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

## Path-Scoped Rules

`CLAUDE.md` is unconditional: whatever it says loads on every turn in its directory subtree. That is the right shape for architecture context and team standards, and the wrong shape for a convention that applies to a fraction of the files. Putting PCI logging rules in the root `CLAUDE.md` of a monorepo means every developer working on the unregulated app carries them for nothing.

Rules solve the scoping problem. A rule is a Markdown file under `.claude/rules/` whose YAML frontmatter names the paths it applies to, and Claude Code loads it only when it touches a matching file.

```markdown
---
paths: ["apps/retail/**/*.ts", "apps/corporate/**/*.ts"]
---

# PCI-DSS Logging

Never log a full PAN. Mask to the last four digits at the call site,
not in the log sink.
```

The glob is matched against the file path, so scope by whatever the naming convention actually encodes. Public API routes named `*public.route.ts` and scattered across dozens of domain folders are reachable with `["**/*public.route.ts"]`; scoping by directory instead would miss every one of them.

| Need | Mechanism |
|---|---|
| Applies to the whole project | Root `CLAUDE.md` |
| Applies to one subtree | Nested `CLAUDE.md` in that directory |
| Applies to files matching a pattern, wherever they live | `.claude/rules/<name>.md` with `paths:` frontmatter |

There is no `exclude:` counterpart, so express the scope positively. Naming the paths that should carry the rule is both more precise and cheaper than loading it everywhere and asking Claude to check the filename before applying it.

## Output Styles

`CLAUDE.md` and rules change what Claude knows. An output style changes how it answers, and it is the only harness file that edits the system prompt itself rather than adding a message after it. Reach for one when you keep re-prompting for the same voice or format every turn: replies that lead with a diagram, replies that never speculate, replies that stop at what changed.

A style is a Markdown file with frontmatter, saved at user scope in `~/.claude/output-styles/`, at project scope in `.claude/output-styles/`, or shipped by a plugin.

```markdown
---
name: Answer Only
description: Reply with what changed and what blocks the user, nothing else
keep-coding-instructions: true
---

Say what changed and where, and anything that blocks the user or is theirs to decide.

Do not include how you verified it, what you ruled out, caveats they did not raise,
or next steps. When you are holding detail that might matter, offer it in one clause
and stop.
```

| Field | Effect |
|---|---|
| `name` | The name shown in the picker. Defaults to the file name. |
| `description` | One line describing the style, shown beside the name. |
| `keep-coding-instructions` | Defaults to `false`, which **drops** Claude Code's built-in software engineering instructions. Set it to `true` whenever the style changes tone or format but the work is still coding. |

That default is the trap. A style written to shorten replies, saved without `keep-coding-instructions: true`, also removes the instructions covering how Claude scopes a change, comments code, and verifies its work. Leave it out only when the session is not software engineering at all, such as a writing or data-analysis assistant.

Activate a style with `/config`, which writes `outputStyle` into `.claude/settings.local.json`, or set the field directly in any settings file to choose the scope yourself:

```json
{
  "outputStyle": "Answer Only"
}
```

The system prompt is read once at session start, so a new style or an edit to an active one takes effect after `/clear` or in the next session, never mid-conversation. Styles apply to the main conversation only: a subagent runs its own system prompt and is unaffected, while a fork inherits the parent's.

Four built-in styles ship with Claude Code. **Default** is the standard engineering prompt. **Proactive** executes immediately and makes reasonable assumptions instead of pausing on routine decisions. **Explanatory** adds educational insights alongside the work, and **Learning** goes further by leaving `TODO(human)` markers for you to implement.

| Mechanism | How it reaches the model | Use it when |
|---|---|---|
| Output style | Modifies the system prompt | You want a different tone or response format every turn |
| `CLAUDE.md` | Adds a user message after the system prompt | Claude should always know your project conventions |
| `--append-system-prompt` | Appends to the system prompt for one invocation | You need a one-off addition to a single run |

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
| `/init` | Scaffold a new `CLAUDE.md` in the current repo with architecture and rules. |
| `/update-config` | Edit `settings.json` to configure permissions, env vars, hooks, and scopes. |
| `/memory` | Open the global `CLAUDE.md` for editing, the user-level harness file. |
| `/config` | Open the interactive settings panel to manage preferences and model selection. |
| `/doctor` | Diagnose the resolved harness: which config files loaded and which entries were stripped. |

## Key Topics covered in this module

- [Claude Code Settings](https://code.claude.com/docs/en/settings): settings hierarchy, scopes, and permission model
- [CLAUDE.md Memory](https://code.claude.com/docs/en/memory): how context files are discovered and merged
- [Slash Commands](https://code.claude.com/docs/en/slash-commands): built-in and custom command authoring
- [Output Styles](https://code.claude.com/docs/en/output-styles): frontmatter fields, the four built-in styles, and how a style differs from `CLAUDE.md`
- [Model Context Protocol](https://modelcontextprotocol.io/): MCP specification and tool extension model
- [Hooks](https://code.claude.com/docs/en/hooks): event-driven automation with `PreToolUse`, `PostToolUse`, `Stop`
- [Enterprise Deployment](https://code.claude.com/docs/en/third-party-integrations): organization rollout, managed policy settings, and shared configuration
- [Subagents](https://code.claude.com/docs/en/sub-agents): defining agents in `.claude/agents/` with their own prompt, tools, and model

# Build domain sub-agents for backend, frontend and QA

A domain agent is a specialized sub-agent scoped to one kind of work: `dotnet-expert` owns .NET controllers, services, repositories and EF Core migrations, `angular-expert` owns Angular v21+ components, signal-based state, Signal Forms and Vitest tests, and the qa-agent `playwright-expert` owns screenshots, Lighthouse audits, viewport checks, console error detection and interaction testing. Each runs in its own isolated context window, so no frontend, backend or test artifacts bleed into another domain, and each wires the skill and MCPs its domain needs in its own frontmatter. The qa-agent carries no implementation authority: it tests, audits, and reports findings back to the orchestrator.

## The Backend Agent File

The agent file lives at [`.claude/agents/dotnet-expert.md`](../../../.claude/agents/dotnet-expert.md). It applies the [`dotnet-conventions`](../../../.claude/skills/dotnet-conventions/SKILL.md) skill rules on every file it creates or edits, and validates API patterns against official Microsoft documentation via the `microsoft-learn` MCP. Command-level rules such as `Bash(rm:*)` are not an agent field; they live in `settings.json` under `permissions.deny` and apply to every sub-agent in the session.

```yaml
---
name: dotnet-expert
description: >-
  Implements REST API endpoints, data models, services, and EF Core migrations for .NET applications.
  Apply when the task is "implement the API", "add an endpoint", "write the backend", "scaffold a service",
  or "add a controller". Use for any .NET backend work: controllers, repositories, middleware, and data access.
model: sonnet
tools: [Read, Write, Edit, Bash, Glob, Grep, mcp__microsoft-learn__microsoft_docs_search, mcp__microsoft-learn__microsoft_code_sample_search, mcp__microsoft-learn__microsoft_docs_fetch]
mcpServers:
  microsoft-learn:
    type: http
    url: https://learn.microsoft.com/api/mcp
---
```

The agent body instructs the agent to read existing source files before writing, apply the `dotnet-conventions` skill rules, validate SDK patterns via `microsoft-learn`, and return a typed JSON object when the orchestrator requests a structured response.

## Integrating the dotnet-conventions Skill

The [`dotnet-conventions`](../../../.claude/skills/dotnet-conventions/SKILL.md) skill lives at `.claude/skills/dotnet-conventions/` and contains two reference files: [`conventions.md`](../../../.claude/skills/dotnet-conventions/references/conventions.md) for naming, architecture, DI, and async patterns, and [`dotnet-cli.md`](../../../.claude/skills/dotnet-conventions/references/dotnet-cli.md) for build and package management commands. The backend agent system prompt points to `conventions.md` so the rules are active without the orchestrator needing to pass them in the task prompt.

Key conventions the agent enforces on every file:

- Primary constructor syntax for dependency injection (`public class MyService(IRepository repo)`)
- PascalCase for public members; camelCase for private fields and locals
- `async`/`await` for all I/O with `ConfigureAwait(false)` where appropriate
- XML documentation comments on all public classes and methods
- Structured logging via `Microsoft.Extensions.Logging`, never `Console.WriteLine`

## The Frontend Agent File

The agent file lives at [`.claude/agents/angular-expert.md`](../../../.claude/agents/angular-expert.md). It wires two MCPs directly in its frontmatter: `angular-cli` for code generation and best-practice queries, and `chrome-devtools` for browser inspection and performance audits. Sub-agent frontmatter has no `permissions` field: the supported keys are `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `mcpServers`, `hooks`, `maxTurns`, `skills`, `memory`, `background`, `effort`, `isolation`, `color`, and `initialPrompt`. Tool access is scoped by the `tools` allowlist below.

```yaml
---
name: angular-expert
description: >-
  Implements Angular v21+ components, services, and state management using signal-based APIs
  and OnPush change detection. Apply when the task is "create a component", "implement a service",
  "add a route", "write unit tests", or "refactor to signals". Use for any Angular frontend work:
  standalone components, NgRx Signal Store, reactive forms, and Vitest unit tests.
model: sonnet
tools: [Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch,
        mcp__angular-cli__list_projects, mcp__angular-cli__get_best_practices,
        mcp__angular-cli__search_documentation, mcp__angular-cli__onpush_zoneless_migration,
        mcp__angular-cli__ai_tutor,
        mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__lighthouse_audit,
        mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__evaluate_script, ...]
mcpServers:
  angular-cli:
    type: stdio
    command: npx
    args: ["-y", "@angular/cli", "mcp"]
  chrome-devtools:
    type: stdio
    command: npx
    args: ["-y", "chrome-devtools-mcp@latest"]
permissionMode: default
---
```

Every MCP tool that the agent calls must also appear in the `tools` allowlist using the `mcp__<server-name>__<tool-name>` naming convention.

## The angular-cli MCP

| Tool | Purpose |
|---|---|
| `mcp__angular-cli__list_projects` | Discover projects and workspace paths |
| `mcp__angular-cli__get_best_practices` | Load current Angular coding standards |
| `mcp__angular-cli__search_documentation` | Search official Angular docs |
| `mcp__angular-cli__onpush_zoneless_migration` | Modernize components to zoneless OnPush |
| `mcp__angular-cli__ai_tutor` | Ask Angular-specific architectural questions |

## The chrome-devtools MCP

The `chrome-devtools` MCP connects the agent to a running Chrome instance so it can inspect the rendered UI without leaving the terminal. The agent uses `mcp__chrome-devtools__take_screenshot` to verify component output visually, `mcp__chrome-devtools__lighthouse_audit` to validate performance, and `mcp__chrome-devtools__evaluate_script` to assert signal values in the live DOM.

## The QA Agent File

The agent file lives at [`.claude/agents/playwright-expert.md`](../../../.claude/agents/playwright-expert.md). It wires two MCPs in its frontmatter: `playwright` for browser automation and interaction, and `chrome-devtools` for low-level inspection, performance tracing, and Lighthouse audits.

```yaml
---
name: playwright-expert
description: >-
  QA and verification specialist. Uses Playwright and Chrome DevTools to take screenshots,
  run Lighthouse audits, verify layout at multiple viewports, check accessibility, and
  diagnose visual bugs. Apply when the task is "verify", "screenshot", "run Lighthouse",
  "check accessibility", "test interactions", or "QA the page". Reports findings only;
  does not write or modify code.
model: haiku
tools: [Read, Bash, Glob, Grep,
        mcp__playwright__browser_navigate, mcp__playwright__browser_take_screenshot,
        mcp__playwright__browser_snapshot, mcp__playwright__browser_click,
        mcp__playwright__browser_hover, mcp__playwright__browser_resize,
        mcp__playwright__browser_evaluate, mcp__playwright__browser_console_messages,
        mcp__playwright__browser_network_requests, mcp__playwright__browser_wait_for,
        mcp__chrome-devtools__lighthouse_audit, mcp__chrome-devtools__take_screenshot,
        mcp__chrome-devtools__performance_start_trace, mcp__chrome-devtools__performance_stop_trace,
        mcp__chrome-devtools__performance_analyze_insight, mcp__chrome-devtools__list_console_messages, ...]
mcpServers:
  playwright:
    type: stdio
    command: npx
    args:
      - "@playwright/mcp@latest"
      - "--vision"
  chrome-devtools:
    type: stdio
    command: npx
    args:
      - "-y"
      - "chrome-devtools-mcp@latest"
disallowedTools: [Write, Edit, NotebookEdit]
---
```

## Playwright MCP vs Chrome DevTools MCP

| Task | MCP |
|---|---|
| Navigate to a URL | `mcp__playwright__browser_navigate` |
| Click a button or link | `mcp__playwright__browser_click` |
| Resize to a breakpoint | `mcp__playwright__browser_resize` |
| Take a screenshot | `mcp__playwright__browser_take_screenshot` |
| Read console errors | `mcp__playwright__browser_console_messages` |
| Run a Lighthouse audit | `mcp__chrome-devtools__lighthouse_audit` |
| Record a performance trace | `mcp__chrome-devtools__performance_start_trace` |
| Inspect network requests | `mcp__chrome-devtools__list_network_requests` |

## Spawning Domain Agents from an Orchestrator

Independent domains run in parallel:

```text
You are an orchestrator. Spawn the following agents in parallel:

1. dotnet-expert
   Task: Add a GET /users endpoint in src/Api/Users/UsersController.cs.
         Register UserService in Program.cs with Scoped lifetime.
   Return: { "status", "filesChanged", "summary" }

2. angular-expert
   Task: Create a standalone UserListComponent in src/app/users/user-list/.
         Fetch users from GET /users using resource(). Use OnPush and signals throughout.
   Return: { "status", "filesChanged", "summary" }

3. testing-agent
   Task: Write Vitest unit tests for UserListComponent in src/app/users/user-list/user-list.component.spec.ts.
         Mock the HTTP layer. Cover the happy path, empty state, and error state.
   Return: { "status", "filesChanged", "summary" }

Wait for all three to complete, then report the merged list of changed files.
```

Verification depends on the implementation, so the qa-agent runs in sequence and feeds issues back:

```text
You are an orchestrator. Spawn the following agents in sequence:

1. angular-expert
   Task: Create a standalone UserListComponent in src/app/users/user-list/.
         Fetch users from GET /users using resource(). Use OnPush and signals.
   Return: { "status", "filesChanged", "summary" }

2. playwright-expert
   Task: Navigate to http://localhost:4200/users.
         Verify the component renders at 320px, 768px, and 1280px.
         Run a Lighthouse audit and check the console for errors.
   Return: { "status", "pagesVerified", "viewportsTested", "lighthouseScores", "issues", "summary" }

If the playwright-expert reports issues, spawn angular-expert again with the issue list attached.
```

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/context` | Show what the session is carrying before delegating a large backend task |
| `/mcp` | Verify the microsoft-learn, angular-cli, chrome-devtools and playwright MCP connections before spawning the agent that needs them |
| `/tasks` | List and monitor the background tasks spawned when agents run in parallel or the playwright-expert verifies in the background |
| `/permissions` | Audit the session allow and deny shell command rules that dotnet-expert inherits when it runs `dotnet` |
| `/subtask` | Hand the angular-expert the current frontend context instead of restating the task by hand |
| `/model` | Assign Sonnet to the implementation agents and Haiku to the playwright-expert, and compare the cost |
| `/cost` | Compare what a Chrome DevTools verification loop costs against the implementation run itself |
| `/effort` | Lower the effort level for repetitive screenshot-and-audit loops to reduce per-task cost |

## Key Topics covered in this module

- [Claude Code Sub-Agents](https://code.claude.com/docs/en/sub-agents): agent frontmatter fields, tool allowlists, and permission blocks
- [Claude Code Agent Permissions](https://code.claude.com/docs/en/settings): `allow` and `deny` rules for shell commands and MCP calls
- [Claude Models Overview](https://platform.claude.com/docs/en/about-claude/models/overview): model IDs for matching models to agent roles, and when to use Haiku versus Sonnet for cost-efficient agent networks
- [.NET Dependency Injection](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection): primary constructor DI patterns enforced by `dotnet-conventions`
- [Angular Signals](https://angular.dev/guide/signals): `signal()`, `computed()`, `effect()`, and signal-based inputs and outputs
- [Angular CLI MCP](https://angular.dev/reference/configs/mcp): workspace discovery, best-practice queries, and documentation search via MCP
- [Playwright MCP](https://github.com/microsoft/playwright-mcp): browser automation tools for navigation, interaction, and screenshot capture
- [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp): Lighthouse audits, performance traces, and network inspection via Chrome DevTools Protocol

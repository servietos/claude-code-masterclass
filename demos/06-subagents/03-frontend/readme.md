# Configure a frontend sub-agent for Angular

A frontend agent is a specialized sub-agent scoped exclusively to Angular v21+ work: standalone components, signal-based state, Signal Forms, and Vitest unit tests. It runs in its own isolated context window so no backend or migration artifacts bleed into the frontend domain. The agent wires two MCPs directly in its frontmatter: `angular-cli` for code generation and best-practice queries, and `chrome-devtools` for browser inspection and performance audits.

## The Frontend Agent File

The agent file lives at [`.claude/agents/angular-expert.md`](../../../.claude/agents/angular-expert.md). Sub-agent frontmatter has no `permissions` field: the supported keys are `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `mcpServers`, `hooks`, `maxTurns`, `skills`, `memory`, `background`, `effort`, `isolation`, `color`, and `initialPrompt`. Tool access is scoped by the `tools` allowlist below, while command-level rules such as `Bash(rm:*)` live in `.claude/settings.json` under `permissions.deny` and are inherited by every sub-agent.

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

## Spawning the Frontend Agent from an Orchestrator

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

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/subtask` | Hand the angular-expert the current frontend context instead of restating the task by hand |
| `/mcp` | Inspect the angular-cli and chrome-devtools MCP connections before running the agent |
| `/model` | Assign Sonnet to the frontend agent while keeping Haiku for repetitive QA tasks |
| `/cost` | Compare what a Chrome DevTools verification loop costs against the implementation run itself |

## Key Topics covered in this module

- [Claude Code Sub-Agents](https://code.claude.com/docs/en/sub-agents): agent frontmatter fields, tool allowlists, and permission blocks
- [Claude Code Agent Permissions](https://code.claude.com/docs/en/settings): `allow` and `deny` rules for shell commands and MCP calls
- [Claude Models Overview](https://platform.claude.com/docs/en/about-claude/models/overview): model IDs for matching models to agent roles
- [Angular Signals](https://angular.dev/guide/signals): `signal()`, `computed()`, `effect()`, and signal-based inputs and outputs
- [Angular CLI MCP](https://angular.dev/reference/configs/mcp): workspace discovery, best-practice queries, and documentation search via MCP

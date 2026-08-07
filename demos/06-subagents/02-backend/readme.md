# Implement a backend sub-agent for .NET

A backend agent is a specialized sub-agent scoped exclusively to .NET work: REST controllers, services, repositories, and EF Core migrations. It runs in its own isolated context window so no frontend or test artifacts bleed into the backend domain. The agent applies the [`dotnet-conventions`](../../../.claude/skills/dotnet-conventions/SKILL.md) skill rules on every file it creates or edits, and validates API patterns against official Microsoft documentation via the `microsoft-learn` MCP.

## The Backend Agent File

The agent file lives at [`.claude/agents/dotnet-expert.md`](../../../.claude/agents/dotnet-expert.md). Command-level rules such as `Bash(rm:*)` are not an agent field; they live in `settings.json` under `permissions.deny` and apply to every sub-agent in the session.

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

## Spawning the Backend Agent from an Orchestrator

```text
You are an orchestrator. Spawn the following agents in parallel:

1. dotnet-expert
   Task: Add a POST /tasks endpoint in src/Api/Tasks/TasksController.cs.
         Register the TaskService in Program.cs with Scoped lifetime.
   Return: { "status", "filesChanged", "summary" }

2. testing-agent
   Task: Write MSTest unit tests for TaskService in tests/Api/Tasks/TaskServiceTests.cs.
         Mock ITaskRepository using Moq.
   Return: { "status", "filesChanged", "summary" }

Wait for both agents to complete, then report the merged list of changed files.
```

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/context` | Show what the session is carrying before delegating a large backend task |
| `/mcp` | Verify the microsoft-learn MCP connection is active before spawning dotnet-expert |
| `/tasks` | List background tasks spawned when the orchestrator runs backend and testing agents in parallel |
| `/permissions` | Audit the session allow and deny shell command rules that dotnet-expert inherits when it runs `dotnet` |

## Key Topics covered in this module

- [Claude Code Sub-Agents](https://code.claude.com/docs/en/sub-agents): agent frontmatter fields, tool allowlists, and permission blocks
- [Claude Code Agent Permissions](https://code.claude.com/docs/en/settings): `allow` and `deny` rules for shell commands and MCP calls
- [Claude Models Overview](https://platform.claude.com/docs/en/about-claude/models/overview): model IDs for matching models to agent roles
- [.NET Dependency Injection](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection): primary constructor DI patterns enforced by `dotnet-conventions`

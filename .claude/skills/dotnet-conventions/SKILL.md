---
name: dotnet-conventions
description: '.NET/C# coding conventions for ASP.NET Core controllers, EF Core models and migrations, unit testing with xUnit/FluentAssertions/NSubstitute, `.http` REST client files, dotnet CLI commands, MCP server development, health checks (readiness/liveness, Docker HEALTHCHECK), MSAL/Entra ID JWT auth, and local username/password login with DB RBAC. Also covers naming, architecture, DI, async, configuration, logging, and code-quality rules. Delegates each topic to the matching reference file. Use for any .NET 10 work before writing code. Triggers on "dotnet convention", "asp.net controller", "ef core migration", "xunit test", "nsubstitute", "fluentassertions", "http rest client file", "dotnet cli", "mcp server dotnet", "health check endpoint", "msal jwt dotnet", "local login rbac", "dependency injection", "async convention", "logging convention".'
---

# .NET/C# Best Practices

Authoritative conventions for any .NET 10 project. Routes build, test, and tooling requests to the appropriate reference before applying code conventions.

> ⚠️ **CRITICAL**: Always validate code practices and API usage against **Microsoft Learn** using the `microsoft-learn` MCP. Do not rely on assumptions about SDK patterns, APIs, or best practices; check the official documentation.

## Sub-skill Delegate Map

| Request type | Reference |
|---|---|
| Build, test, run, publish, format, NuGet, EF migrations CLI | [`dotnet-cli`](references/dotnet-cli.md) |
| Naming, documentation, architecture, DI, resources, async, testing, logging, code style | [`conventions`](references/conventions.md) |
| `[ApiController]` controller + CRUD endpoint patterns | [`dotnet-controllers`](references/dotnet-controllers.md) |
| EF Core models, `IEntityTypeConfiguration`, migrations, queries | [`dotnet-efcore`](references/dotnet-efcore.md) |
| Unit tests with xUnit, FluentAssertions, NSubstitute | [`dotnet-testing`](references/dotnet-testing.md) |
| `.http` REST client files | [`dotnet-rest-client`](references/dotnet-rest-client.md) |
| MSAL / Microsoft.Identity.Web JWT auth | [`dotnet-msal-auth`](references/dotnet-msal-auth.md) |
| Dual-auth: local username/password login (BCrypt + local JWT) and DB RBAC alongside MSAL | [`dotnet-local-auth-rbac`](references/dotnet-local-auth-rbac.md) |
| MCP server with `ModelContextProtocol` / `ModelContextProtocol.AspNetCore` | [`dotnet-mcp`](references/dotnet-mcp.md) |
| `/health` endpoints, readiness/liveness probes, dependency health checks, Docker `HEALTHCHECK` wiring | [`dotnet-health-checks`](references/dotnet-health-checks.md) |

Always use the dotnet CLI for package management and project operations — never edit `.csproj` files directly to add or remove packages.

---

## Naming Conventions

- Use `PascalCase` for all public classes, methods, and properties.
- Use `camelCase` for private fields and local variables.

## Design Patterns and Architecture

- Use .NET primary constructors with no private backing fields unless additional logic is required.
- Use primary constructor syntax for dependency injection: `public class MyClass(IDependency dependency)`.
- Implement the Command Handler pattern with generic base classes where applicable.
- Use interface segregation — prefix interfaces with `I`.
- Follow the Factory pattern for complex object creation.

## Dependency Injection and Services

- Use constructor dependency injection.
- Register services with appropriate lifetimes: `Singleton`, `Scoped`, `Transient`.
- Use `Microsoft.Extensions.DependencyInjection` patterns.
- Implement service interfaces for testability.

## Async/Await Patterns

- Use `async`/`await` for all I/O operations and long-running tasks.
- Return `Task` or `Task<T>` from async methods.
- Use `ConfigureAwait(false)` where appropriate.
- Handle async exceptions properly.

## Testing Standards

- Use xUnit, NSubstitute, and FluentAssertions or the project's chosen equivalents.
- Follow the AAA pattern: Arrange, Act, Assert.
- Test both success and failure scenarios.

## Configuration and Settings

- Use strongly-typed configuration classes.
- Use `IConfiguration` binding for settings.
- Support `appsettings.json` configuration files.

## JSON casing contract with SPA clients

When `PropertyNamingPolicy = null` is set (PascalCase passthrough) but the SPA's TypeScript
models expect camelCase, **every DTO consumed by the client needs explicit
`[JsonPropertyName("camelCase")]` attributes** — and the failure mode when one file misses them
is silent and misleading: the client reads `response.token` from `{"Token": ...}`, gets
`undefined`, and downstream code breaks far from the serialization boundary (here: login
"succeeded" with 200 but the session stored `{}` and the user stayed on the login page). Rules:

- Treat the casing policy as a **contract**: either camelCase globally, or attribute every
  client-facing DTO. Check sibling DTO files for the established attribute precedent before
  adding a new DTO file — the bug enters when a new file skips the pattern its siblings follow.
- When a client-side flow fails with fields mysteriously `undefined`/empty after a 200 response,
  diff the raw response body's key casing against the client interface **first** — before
  debugging the client logic.

## Error Handling and Logging

- Use structured logging with `Microsoft.Extensions.Logging`.
- Include scoped logging with meaningful context.
- Throw specific exceptions with descriptive messages.
- Use `try`-`catch` blocks for expected failure scenarios.

## Performance and Security

- Use C# 14 features and .NET 10 optimizations where applicable.
- Implement proper input validation and sanitization.
- Use parameterized queries for database operations.

## Application Lifecycle

- Before starting the application, check if an instance is already running; if it is running under `dotnet watch run`, reuse that instance instead of starting a new one.
- Never start the application as a background process.
- Always dispose of resources properly when the application closes.
- **Hot-reload limits under `dotnet watch`**: structural edits (new methods, added queries/branches in controllers or services, signature changes) are rude edits. Hot reload fails with `TypeLoadException` and the process then serves that exception for every request while stuck on its interactive restart prompt; file touches do not recover it. After any structural edit under a running watch, verify with a real HTTP request; if the response is a `TypeLoadException`, ask the user to restart the watch (`Ctrl+R` in its terminal). Never kill a watch process you did not start.

## Code Quality

- Ensure SOLID principles compliance.
- Avoid code duplication through base classes and utilities.
- Use meaningful names that reflect domain concepts.
- Keep methods focused and cohesive.
- Implement proper disposal patterns (`IDisposable` / `IAsyncDisposable`) for all resources.

## Pipeline Observability and NDJSON Streaming

- **PipelineTrace pattern** — use a static `AsyncLocal<string?>` correlation id (`NewCorrelation`/`EnsureCorrelation`) and a `Write(pipeline, stage, props)` method that appends one JSON line to `logs/<pipeline>-pipeline.jsonl`. Schema: `{ts, correlationId, pipeline, stage, ...props}`. A second `AsyncLocal<Action<string,string,string>?>` subscriber (`SetSubscriber`/`ClearSubscriber`) lets a streaming controller tap every event without modifying service code. Reference: `Services/PipelineTrace.cs`.
- **NDJSON streaming endpoint** — set `Response.ContentType = "application/x-ndjson"`, create a `Channel<T>`, install the `PipelineTrace` subscriber to feed it, then run resolution and channel draining concurrently. Emit typed lines: `{"type":"stage",...}`, `{"type":"cost",...}`, `{"type":"result",...}`. Always clear the subscriber in a `finally` block. Reference: `Controllers/ResolveController.cs` (`POST /resolve/photo/stream`).
- **Identifier validation before fan-out** — validate EAN-13/8 (Luhn checksum; reject all-equal digits, sequential runs, long zero-runs) and PZN with private static helpers before entering the product lookup fan-out. Emit a `recognize-reject` trace stage for every dropped identifier. Return `back-label-only` when vision signals `IsBackLabel=true`.
- **AI cost capture** — read `usage.estimated_cost` from DeepInfra responses (field absent for DeepSeek; treat as null); emit to `PipelineTrace.Write("ai", "ai-usage", new { Kind = "chat", ... })`. Image and video generation costs use `Kind = "image"` / `Kind = "video"` with a per-image config key (`Images:CostPerImage`) and per-second config key (`Videos:CostPerSecond`) as fallbacks.


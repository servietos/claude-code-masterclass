# Long-running MCP tools with the Tasks extension

A tool whose work outlives the client's call limits (a video render, a provider batch job, an ffmpeg
run, a large import) answers `tools/call` with a task handle and finishes in the background. The
client polls for the outcome itself, so the model never has to remember a job id or call a "check
status" tool. That start/check tool pair is the pattern Tasks replaces: models invent job ids, end
their turn "waiting", and spend tokens on every check.

Use it for work that finishes on its own and takes minutes. A start/stop control (a recording the
caller ends) is not a task; keep it as tools.

## The extension in one paragraph

Tasks is the official extension `io.modelcontextprotocol/tasks` (SEP-2663, protocol `2026-07-28`).
It replaced the experimental core tasks of `2025-11-25`: `tasks/result`, `tasks/list`, the per-call
`task` parameter and the per-tool `execution.taskSupport` flag are gone. The server decides per call
whether to return a task, and only when the request carries the client's opt-in under
`params._meta["io.modelcontextprotocol/clientCapabilities"].extensions["io.modelcontextprotocol/tasks"]`.
A client without the opt-in gets the normal result, so adding Tasks breaks no existing client.
Methods: `tasks/get` (status, and the result inline once terminal), `tasks/update` (answers to the
server's input requests, ack only), `tasks/cancel` (ack only).

## Server side in C#

```xml
<PackageReference Include="ModelContextProtocol.Extensions.Tasks" Version="2.3.0" />
```

Keep it on the same version as `ModelContextProtocol` and `ModelContextProtocol.AspNetCore`.

```csharp
builder.Services.AddMcpServer()
    .WithHttpTransport()
    .WithToolsFromAssembly()
    .WithTasks(new InMemoryMcpTaskStore());
```

- `WithTasks` maps `tasks/get`, `tasks/update` and `tasks/cancel`, advertises the extension, and
  wraps every `[McpServerTool]` so a call can be offloaded to a background task when the client
  opts in. The tool methods do not change.
- Inside a task, `ElicitAsync`, `SampleAsync` and `RequestRootsAsync` reach the client as
  `inputRequests` on the task instead of direct requests.
- The SDK refuses to return a task for a request without the opt-in.
- `WithTasks` and `CallToolWithAlternateHandler` are mutually exclusive.
- Which calls become tasks is chosen per call through `McpTasksOptions.ExecutionModeSelector`
  (`McpTaskExecutionMode`). 2.x has no per-tool attribute for it; `Tool.Execution.TaskSupport` from
  1.x was removed (csharp-sdk #1911).

## The store decides what survives a restart

- `InMemoryMcpTaskStore` is for development and tests. Every task is lost when the process restarts,
  and under `dotnet watch run` that includes every reload that rebuilds the app.
- For anything a user waits on, implement `IMcpTaskStore` over the database. When the provider
  returns its own job or operation id (a batch name, a long-running operation name), store it with
  the task so status can be re-read from the provider after a restart.
- Execution itself is a process-local `Task.Run` (csharp-sdk #1820): the store persists state, but
  there is no hook yet to hand execution to an external queue or durable runtime.

## Wire shape a client accepts

Claude Code (CLI, public beta from v2.1.304) rejects a task answer that misses any of these with
`Unsupported result type` or `returned a malformed task handle`:

| Field | Rule |
| --- | --- |
| `resultType` | `"task"` |
| `taskId` | required, at most 128 printable ASCII characters, no spaces |
| `status` | `working`, `input_required`, `completed`, `failed` or `cancelled` |
| `createdAt`, `lastUpdatedAt` | required |
| `ttlMs` | required, may be `null` |
| `pollIntervalMs` | optional, never `null`; clients clamp it (Claude Code 250 to 30000, default 2000) |

- Put the outcome in the `tasks/get` response. Claude Code never calls `tasks/result` or `tasks/list`
  and does not read task notifications.
- `failed` means a JSON-RPC error. A tool result with `isError: true` is `completed` with that result.
- The client's tool-call time limits apply until the server answers with the task handle, so create
  the task before any slow work starts.
- Clients without Tasks today: Claude Code's VS Code extension and desktop app, one-shot `claude -p`
  runs (only stream-json input with `CLAUDE_AUTO_BACKGROUND_TASKS=1` gets them), and the C# SDK client when the session declares any
  other extension (csharp-sdk #1920, the per-request opt-in is overwritten).

## Proving it by hand

- Drive it in memory first: an xUnit test that sends a `tools/call` with and without the opt-in
  through the SDK's in-memory server, with a fake provider, then `tasks/get` until terminal.
- Over HTTP on protocol `2026-07-28`, a raw client sends on every request the `Mcp-Method` header
  (plus `Mcp-Name` for `tools/call` and the task methods), `protocolVersion` in `_meta`, and the
  client capabilities with the tasks opt-in in `_meta`. Without the opt-in, `tasks/get` and
  `tasks/cancel` answer `-32021`.
- Pick a call that costs nothing (a validation error is fine: it completes the task with `isError`),
  and read the same task back from a second server process to prove the store survives a restart.
- The tool body learns its own task id only through state the store sets when it creates the task
  (an `AsyncLocal` in `CreateTaskAsync`); cover it with a test, since an SDK change can break it.

## Without Tasks

A tool that stays silent for minutes is the case SDK 2.3.0 made sharper: modern Streamable HTTP
responses send headers only with the first protocol message, so a caller's `HttpClient` timeout can
fire before anything arrives. Either make the tool a task, or send progress notifications while it
works, or raise the caller's timeout. The REST equivalent (202 plus run id and a queued worker) is
[long-running-runs](long-running-runs.md).

Sources, read 2026-10-24: SEP-2663 and the ext-tasks repository (github.com/modelcontextprotocol),
the C# SDK Tasks concept page (csharp.sdk.modelcontextprotocol.io/v2/concepts/tasks), and the
Claude Code MCP docs (code.claude.com/docs/en/mcp, section "MCP tasks").

Back to the index: [dotnet-mcp](dotnet-mcp.md)

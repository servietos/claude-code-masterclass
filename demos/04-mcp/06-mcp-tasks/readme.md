# Run Long Tool Calls as MCP Tasks

Some jobs take longer than a tool call can wait: video renders, image batches, ffmpeg runs, AI document extraction and imports, deep research, CI and workflow jobs. Holding the connection open until they finish is impractical, because many clients and the proxies between them time out after a few seconds. MCP Tasks is the official extension for these jobs, `io.modelcontextprotocol/tasks` (SEP-2663), released with MCP 2026-07-28 to replace the experimental tasks of the 2025-11-25 specification. The server answers the call with a task handle and finishes the work in the background, and the client collects the result when it is ready.

## The Tool Pair That Goes Away

Without Tasks, a server splits a long job into two tools: one starts it and returns a job id, the other reports its status. The model then has to run that loop itself. It invents job ids, ends its turn "waiting", and spends tokens on every status check. With Tasks the client polls the server, and the model keeps working on the rest of the request.

## How a Task Runs

![Claude Code sends tools/call, the MCP server answers with a task handle and runs the job in the background, Claude Code polls tasks/get, answers a question with tasks/update and gets the result inline](../pptx/images/06-01-mcp-tasks.svg)

The client opts in on each request by naming the extension in the request's capabilities. The server then decides per call whether the job becomes a task, and a client that never opted in gets the normal result.

| Message | What it does |
|---|---|
| `tools/call` | Returns a task handle (`taskId`, status `working`) when the server moves the job to the background |
| `tasks/get` | Polls the task; once it is `completed`, the response carries the tool result inline |
| `tasks/update` | Answers a task in `input_required`, for example with the user's reply to an elicitation |
| `tasks/cancel` | Asks the server to stop the job; cancellation is cooperative, so the job may still finish |

## MCP Tasks in Claude Code

Claude Code has tasks in public beta from v2.1.304, in the CLI, the Agent SDK and GitHub Actions. The VS Code extension and the desktop app do not have them. Once a server accepts a job, the tool call returns, the footer shows a count such as `1 MCP task`, and Claude carries on; when the job ends, the transcript says so and Claude gets the result.

A running task can ask you a question through an elicitation dialog, which stays hidden while `/tasks` is open. Headless runs get tasks only as an Agent SDK session or a `claude -p` run reading `--input-format stream-json`, with `CLAUDE_AUTO_BACKGROUND_TASKS=1` set. A one-shot `claude -p "<prompt>"` makes plain tool calls.

## The Server Side in C#

The C# SDK ships tasks in the `ModelContextProtocol.Extensions.Tasks` package (2.3.0), which needs protocol revision 2026-07-28 or later. `WithTasks` on the server builder wraps each `[McpServerTool]` call and moves it to a background task when the client opted in, so the tool code stays as it is.

```csharp
builder.Services.AddMcpServer()
    .WithHttpTransport()
    .WithToolsFromAssembly()
    .WithTasks(new InMemoryMcpTaskStore());
```

`InMemoryMcpTaskStore` is meant for development and tests, and it loses its tasks when the server restarts. A production server implements `IMcpTaskStore` on durable storage.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/tasks` | See the session's background work, MCP tasks included; select a task and press `x` to stop it |
| `/mcp` | Reconnect a disconnected server before you stop its task, so the cancel request reaches it |

## Key Topics covered in this module

- [MCP Tasks overview](https://modelcontextprotocol.io/extensions/tasks/overview)
- [MCP Tasks specification](https://github.com/modelcontextprotocol/ext-tasks)
- [SEP-2663 pull request](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2663)
- [Claude Code: MCP tasks that run on the server](https://code.claude.com/docs/en/mcp#mcp-tasks-that-run-on-the-server)
- [C# SDK: tasks](https://csharp.sdk.modelcontextprotocol.io/v2/concepts/tasks/tasks.html)

# New or renamed tool not showing up

## The tool catalog is built at startup, so every surface change needs a restart

`WithToolsFromAssembly()` enumerates `[McpServerTool]` methods and generates their JSON schemas
**once, at boot**. Under `dotnet watch` the code hot-reloads but the catalog does not: a new tool, a
renamed tool, a changed description, or a parameter that just became optional stays invisible.

The symptom is misleading, because everything else works. Plain controller endpoints answer with the
new behaviour, so the process looks current while `tools/list` still serves the old catalog and the
new tool appears "missing".

```bash
curl -s -X POST http://127.0.0.1:5000/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | tr ',' '\n' | grep '"name"'
```

Rules:

- Check `tools/list` for the tool name **before** debugging why the tool misbehaves. Absent from the
  catalog means restart, not a bug.
- Batch tool-surface changes: each one costs a restart, and you cannot kill a watch you did not
  start. Ask for `Ctrl+R` and state what you will verify once it is back.
- A failed rebuild keeps the previous catalog **and** the previous code with no visible error. See
  [`app-lifecycle-and-watch.md`](app-lifecycle-and-watch.md).

Back to the index: [dotnet-mcp](dotnet-mcp.md)

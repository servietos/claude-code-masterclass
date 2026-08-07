---
presents: demo-hr-mcp-server.md
budget: 5 min
beats: 5
---

# Present: Build an HR MCP Server with Streamable HTTP

An MCP server is ordinary application code plus three fluent calls, and the C# attribute text is the tool documentation the model actually reads. Five beats: the attribute registration, the three fluent calls, the generated schema, two alarming outputs that are both correct, two client files spelling one transport differently.

------

## Beats

### Beat 1: the attribute is the registration, and the method name is the wire name (1 min)

**Open:** [`hr-mcp-server/Tools/HRTools.cs`](hr-mcp-server/Tools/HRTools.cs) · the `AssignShift` attributes · [readme.md](readme.md#hr-mcp-server)
**Say:** The mental model to replace is a manifest describing a method that lives somewhere else. Here the method is the declaration: an attribute marks it, the SDK derives the wire name and the schema, and there is no second artifact.

```csharp
    [McpServerTool]
    [Description("Assigns an employee to an 8-hour shift by name, date, and position")]
    public async Task<string> AssignShift(
        [Description("Full or partial name of the employee")] string employeeName,
        [Description("Date of the shift in yyyy-MM-dd format")] string date,
        [Description("Position for the shift (e.g. bar, waiter, host, chef)")] string position,
        [Description("Hour (0-23) at which the 8-hour shift starts. Defaults to 8")] int shiftStartHour = 8)
```

**Result:** no file written; six `[McpServerTool]` methods reach the wire as `list_employees`, `add_employee`, `update_employee`, `remove_employee`, `search_employees` and `assign_shift`.

**Gotcha:** parameter names are left alone, so `shiftStartHour` stays camel case, and the `[Description]` strings are not comments but the only documentation the model ever sees.

### Beat 2: three fluent calls turn an ASP.NET Core app into an MCP server (1 min)

**Open:** [`hr-mcp-server/Program.cs`](hr-mcp-server/Program.cs) · [`hr-mcp-server/appsettings.json`](hr-mcp-server/appsettings.json) · the `Kestrel:Endpoints` section
**Say:** An MCP server is an ordinary web application with one more endpoint on it. Which line publishes that endpoint, and at which path, is what makes client configuration predictable instead of trial and error.

```csharp
builder.Services.AddMcpServer()
    .WithHttpTransport()
    .WithToolsFromAssembly();
...
app.MapMcp();
```

**Result:** [`hr.db`](hr-mcp-server-solution/hr.db) created and seeded on the first start, and the endpoint bound at the site root

```text
info: HRMCPServer.Data.EmployeeDbInitializer[0]
      Seeded 8 employees into the database.
...
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: http://[::]:47002
```

**Gotcha:** `WithToolsFromAssembly()` scans for `[McpServerToolType]` classes, so a seventh tool is a seventh method and nothing else.

### Beat 3: the schema clients discover is generated from the C# text (1 min)

**Open:** [`hr-mcp-server/Tools/HRTools.cs`](hr-mcp-server/Tools/HRTools.cs) · [Step 4: List all six tools with the MCP Inspector](demo-hr-mcp-server.md#step-4-list-all-six-tools-with-the-mcp-inspector)
**Say:** A client learns what a server can do by asking it, so somewhere there is a machine-readable answer. Deriving it from the source removes the drift everybody has met with hand-maintained API descriptions.

```bash
npx @modelcontextprotocol/inspector --config inspector.config.json --server hr-mcp --cli --method tools/list
```

**Result:** no file written; `required` names exactly the three parameters that have no C# default, and `default: 8` is `shiftStartHour`'s

```json
  "name": "assign_shift",
  "description": "Assigns an employee to an 8-hour shift by name, date, and position",
  "inputSchema": {
    "type": "object",
    "properties": {
      "employeeName": { "description": "Full or partial name of the employee", "type": "string" },
...
    "required": ["employeeName", "date", "position"]
  }
```

**Gotcha:** put it beside beat 1 and match the two line by line; this is the beat that kills the idea that MCP needs a hand-written manifest.

### Beat 4: two alarming outputs that are both correct (1 min)

**Open:** [`hr-mcp-server/Program.cs`](hr-mcp-server/Program.cs) · the `app.MapMcp()` root that answers the 400 · [Step 3: Confirm the endpoint speaks MCP and nothing else](demo-hr-mcp-server.md#step-3-confirm-the-endpoint-speaks-mcp-and-nothing-else)
**Say:** People read every surprising output as a defect in the thing they just built. Deciding which side of the wire an error belongs to, before changing any code, is the habit this beat installs.

```bash
curl -s -i http://localhost:47002/
```

**Result:** no file written; a bare GET carries no `Mcp-Session-Id`, so the 400 is the protocol answering correctly and a healthy server looks broken in a browser

```text
HTTP/1.1 400 Bad Request
Content-Type: application/json; charset=utf-8
Server: Kestrel

{"error":{"code":-32000,"message":"Bad Request: Mcp-Session-Id header is required for GET and DELETE requests when the server is using sessions. ..."},"id":"","jsonrpc":"2.0"}
```

**Gotcha:** the second trap is the inspector CLI on Windows printing correct JSON and then crashing in libuv with `Assertion failed: !(handle->flags & UV_HANDLE_CLOSING)` and `Failed with exit code: 3221226505`; read the JSON above it.

### Beat 5: one server, two client config files, two spellings of the same transport (1 min)

**Open:** [`hr-mcp-server/inspector.config.json`](hr-mcp-server/inspector.config.json) · the `hr-mcp` entry · [Step 6: Wire the server into your MCP clients](demo-hr-mcp-server.md#step-6-wire-the-server-into-your-mcp-clients)
**Say:** A server publishes an endpoint and stops there; knowing it exists is the client's problem, and every client keeps its own file. Connection failures usually live here rather than in the server.

```json
    "mcpServers": {
        "hr-mcp": {
            "type": "streamable-http",
            "url": "http://localhost:47002",
            "note": "Local HR MCP Server running on port 47002"
        },
```

**Result:** the entry the demo adds to the repo's [`.mcp.json`](../../../.mcp.json), which ships `qr-code` and no `hr-mcp`

```json
{
  "mcpServers": {
    "hr-mcp": {
      "type": "http",
      "url": "http://localhost:47002"
    }
  }
}
```

**Gotcha:** the transport string differs, `streamable-http` for the inspector and `http` for Claude Code, and that mismatch is the most common reason a working server refuses to connect.

## If the room asks

| Question | Answer |
|---|---|
| What does the run actually change on disk? | `hr.db` and its `-shm`/`-wal` siblings; no source file differs, which is what "no integration code" means in practice. |
| What happens if the model sends a bad date? | `AssignShift` returns `Invalid date format '...'. Please use yyyy-MM-dd.` as a normal tool result, so the model can read it and retry. |
| The inspector connects but lists zero tools. | `--server` selected `hr-mcp-azure-dev`, whose host no longer resolves. Pass `--server hr-mcp`. |
| Why does Kestrel log `Overriding address(es)`? | `Kestrel:Endpoints` in `appsettings.json` binds `http://*:47002` and outranks the `applicationUrl` in `launchSettings.json`. No action needed. |
| My data is stale and the log says the seed was skipped. | `hr.db` survived an earlier run; stop the server, delete it in the project folder, start again, and the eight employees are reseeded. |

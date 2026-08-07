# Build an HR MCP Server with Streamable HTTP

You start the HR MCP server against a seeded SQLite database, verify all six tools through the MCP Inspector CLI, and call two of them against real data. You end with a `.mcp.json` entry that hands those tools to Claude Code in this repository, with no integration code on the client side.

------

## Prerequisites

- .NET SDK 10.0 or later. `dotnet --version` reported `10.0.110` when this guide was verified.
- Node.js, for the MCP Inspector steps only. The inspector runs through `npx` and needs no install.
- Two terminals. The server occupies one for the whole demo.

You work in the starter folder [hr-mcp-server/](hr-mcp-server/) throughout. Its finished, already-run counterpart lives beside it as `hr-mcp-server-solution/` if you want to compare against a completed reference.

## Step 1: See how six C# methods become six MCP tools

Nothing in this project registers tools by hand. [hr-mcp-server/Tools/HRTools.cs](hr-mcp-server/Tools/HRTools.cs) is annotated `[McpServerToolType]`, each public method carries `[McpServerTool]`, and every parameter carries a `[Description]`. The SDK reads those attributes and builds the JSON Schema that clients see, so the C# description text is literally the tool documentation the model reads.

Count the registrations from the repository root:

```bash
grep -c "\[McpServerTool\]" demos/04-mcp/02-mcp/hr-mcp-server/Tools/HRTools.cs
```

```powershell
(Select-String -Path demos/04-mcp/02-mcp/hr-mcp-server/Tools/HRTools.cs -Pattern '\[McpServerTool\]').Count
```

Then look at one method to see the shape:

```csharp
[McpServerTool]
[Description("Assigns an employee to an 8-hour shift by name, date, and position")]
public async Task<string> AssignShift(
    [Description("Full or partial name of the employee")] string employeeName,
    [Description("Date of the shift in yyyy-MM-dd format")] string date,
    [Description("Position for the shift (e.g. bar, waiter, host, chef)")] string position,
    [Description("Hour (0-23) at which the 8-hour shift starts. Defaults to 8")] int shiftStartHour = 8)
```

**Expected result:** the grep prints `6`. Note the naming rule you will see confirmed in step 4: none of these methods declares a name, so the SDK derives the wire name from the method name in lower snake case. `AssignShift` becomes `assign_shift`, `ListEmployees` becomes `list_employees`. Parameter names are not converted, so `employeeName` and `shiftStartHour` stay camel case on the wire.

## Step 2: Start the server

[hr-mcp-server/Program.cs](hr-mcp-server/Program.cs) is a minimal host: it registers the SQLite `DbContext`, the employee service, then `AddMcpServer().WithHttpTransport().WithToolsFromAssembly()`, and finally calls `app.MapMcp()`. The port comes from the `Kestrel:Endpoints` section of [hr-mcp-server/appsettings.json](hr-mcp-server/appsettings.json), which binds `http://*:47002`.

In your first terminal:

```bash
cd demos/04-mcp/02-mcp/hr-mcp-server
dotnet run
```

**Expected result:** on a first start, EF Core calls `EnsureCreatedAsync()`, creates `hr.db` next to the project (this project has no migrations) and seeds eight restaurant employees. Kestrel then reports the bound address:

```text
info: HRMCPServer.Data.EmployeeDbInitializer[0]
      Seeded 8 employees into the database.
warn: Microsoft.AspNetCore.Server.Kestrel[0]
      Overriding address(es) 'http://localhost:47002'. Binding to endpoints defined via IConfiguration and/or UseKestrel() instead.
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: http://[::]:47002
info: Microsoft.Hosting.Lifetime[0]
      Application started. Press Ctrl+C to shut down.
```

The `Overriding address(es)` warning is expected and harmless: `appsettings.json` wins over the `applicationUrl` in `Properties/launchSettings.json`. On every later start the seeder logs `Employee database already contains data; skipping seed.` instead. Leave this terminal running for the rest of the demo.

## Step 3: Confirm the endpoint speaks MCP and nothing else

`app.MapMcp()` maps the Streamable HTTP endpoint at the site root, so the MCP URL is `http://localhost:47002` with no `/mcp` suffix. That root is not a web page, and proving it now saves you from misreading a healthy server as a broken one later.

From your second terminal:

```bash
curl -s -i http://localhost:47002/
```

**Expected result:** HTTP 400 with a JSON-RPC error body. This is the correct answer to a non-MCP request, not a fault:

```text
HTTP/1.1 400 Bad Request
Content-Type: application/json; charset=utf-8
Server: Kestrel

{"error":{"code":-32000,"message":"Bad Request: Mcp-Session-Id header is required for GET and DELETE requests when the server is using sessions. ..."},"id":"","jsonrpc":"2.0"}
```

Opening the same URL in a browser shows the same 400. A real MCP client sends `initialize` first and carries the session id it gets back on every subsequent request.

## Step 4: List all six tools with the MCP Inspector

The `--cli` mode performs the handshake, issues one method, prints the raw result and exits, which makes it the fastest way to see exactly what a host would discover.

Run it from the project folder so the relative config path resolves:

```bash
cd demos/04-mcp/02-mcp/hr-mcp-server
npx @modelcontextprotocol/inspector --config inspector.config.json --server hr-mcp --cli --method tools/list
```

**Expected result:** a `tools` array with six entries: `list_employees`, `add_employee`, `update_employee`, `remove_employee`, `search_employees` and `assign_shift`. Each carries the `[Description]` text from the C# source and a full `inputSchema`. The `assign_shift` entry looks like this:

```json
{
  "name": "assign_shift",
  "description": "Assigns an employee to an 8-hour shift by name, date, and position",
  "inputSchema": {
    "type": "object",
    "properties": {
      "employeeName": { "description": "Full or partial name of the employee", "type": "string" },
      "date": { "description": "Date of the shift in yyyy-MM-dd format", "type": "string" },
      "position": { "description": "Position for the shift (e.g. bar, waiter, host, chef)", "type": "string" },
      "shiftStartHour": { "description": "Hour (0-23) at which the 8-hour shift starts. Defaults to 8", "type": "integer", "default": 8 }
    },
    "required": ["employeeName", "date", "position"]
  }
}
```

> **Warning:** on Windows the inspector CLI prints the complete, correct result and then crashes during teardown with `Assertion failed: !(handle->flags & UV_HANDLE_CLOSING), file src\win\async.c, line 76` followed by `Failed with exit code: 3221226505`. That is a libuv teardown bug in the inspector, not a fault in your server. Read the JSON above the assertion; it is the real answer.

Drop `--cli --method tools/list` from the same command to open the browser UI instead, which lists the tools and lets you fill in arguments through a form.

## Step 5: Call two tools against real data

Discovery proves the schema; a call proves the wiring all the way down to SQLite. Start with the read-only tool:

```bash
npx @modelcontextprotocol/inspector --config inspector.config.json --server hr-mcp --cli --method tools/call --tool-name list_employees
```

**Expected result:** a single text content block whose payload is an `employees` array with the eight seeded staff members ordered by last name, so Marie Dubois comes first and Kenji Tanaka last. The JSON property names come from the `[JsonPropertyName]` attributes on the model, which is why you see `spoken_languages` and `current_role` rather than the C# property names:

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"employees\":[{\"firstname\":\"Marie\",\"lastname\":\"Dubois\",\"email\":\"marie.dubois@restaurant.com\",\"spoken_languages\":[\"French\",\"English\",\"Italian\"],\"skills\":[\"Pastry Chef\",\"Dessert Creation\",\"Baking\",\"Team Leadership\"],\"current_role\":\"Pastry Chef\",\"fullName\":\"Marie Dubois\"}, ...]}"
    }
  ]
}
```

Now write to the database. `assign_shift` matches on a partial name, so `Kenji` is enough:

```bash
npx @modelcontextprotocol/inspector --config inspector.config.json --server hr-mcp --cli --method tools/call --tool-name assign_shift --tool-arg employeeName=Kenji --tool-arg date=2026-08-01 --tool-arg position="sushi bar"
```

**Expected result:** one text content block with the confirmation sentence, and a matching `Assigned Kenji Tanaka to sushi bar ...` line in the server terminal:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Assigned Kenji Tanaka to 'sushi bar' on 2026-08-01 from 08:00 to 16:00."
    }
  ]
}
```

The shift row is persisted, so it survives a server restart. Passing a date that is not `yyyy-MM-dd` returns `Invalid date format ...` as a normal tool result rather than a protocol error, which is the pattern you want: the model can read the message and retry.

## Step 6: Wire the server into your MCP clients

Two client configurations matter here, and they are separate files with separate jobs. [hr-mcp-server/inspector.config.json](hr-mcp-server/inspector.config.json) is read only by the inspector and names the targets you can select with `--server`:

```json
{
  "mcpServers": {
    "hr-mcp": {
      "type": "streamable-http",
      "url": "http://localhost:47002",
      "note": "Local HR MCP Server running on port 47002"
    },
    "hr-mcp-azure-dev": {
      "type": "streamable-http",
      "url": "https://hr-mcp-server-copilot.azurewebsites.net",
      "note": "Dev deployment hosted on Azure App Service (rg-copilot-studio)"
    }
  }
}
```

> **Warning:** the `hr-mcp-azure-dev` host does not resolve; that App Service is no longer deployed. Use `--server hr-mcp` for this demo, and only select the Azure entry after you have published the server to your own App Service and replaced the hostname with yours.

To give the same tools to Claude Code in this repository, add an entry to the project-level [.mcp.json](../../../.mcp.json). Claude Code uses the transport type `http` and the same root URL with no `/mcp` suffix:

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

**Expected result:** with `dotnet run` still going, reload Claude Code's MCP connections and run `/mcp`. The `hr-mcp` entry reports connected and lists the same six tools you saw in step 4. Ask Claude something like "which employees speak French" and it calls `search_employees` on its own rather than guessing.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `Failed to connect to MCP server: fetch failed` and `Failed with exit code: 1` | The inspector was started before the server, so nothing is listening on 47002 | Start `dotnet run` first, wait for `Now listening on: http://[::]:47002`, then run the inspector in the second terminal |
| Correct JSON, then `Assertion failed: !(handle->flags & UV_HANDLE_CLOSING)` and exit code `3221226505` | Known libuv teardown crash in the inspector CLI on Windows | Ignore it and read the JSON printed above it. The server is unaffected and keeps serving |
| `curl` on `http://localhost:47002` returns HTTP 400 | Correct behaviour: the root is an MCP endpoint that requires a session, not a web page | Use an MCP client. A 400 here confirms the server is up |
| The inspector connects but reports zero tools | The `--server` flag selected an entry that is not the local one | Pass `--server hr-mcp`; the `hr-mcp-azure-dev` host does not resolve |
| `Employee database already contains data; skipping seed.` and stale data | `hr.db` survived from an earlier run | Stop the server, delete `hr.db` in the project folder, and start again to reseed the eight employees |
| Kestrel logs `Overriding address(es) 'http://localhost:47002'` | `appsettings.json` binds `http://*:47002` and outranks `launchSettings.json` | No action needed; the server is listening on the intended port |

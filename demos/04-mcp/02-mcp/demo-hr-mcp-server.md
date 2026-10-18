# Build an HR MCP Server with Streamable HTTP

You start the HR MCP server against a seeded SQLite database, verify all six tools through the MCP Inspector CLI, and call one of them against real data. You end with a `.mcp.json` entry that hands those tools to Claude Code in this repository, with no integration code on the client side.

------

You work in the starter folder [hr-mcp-server/](hr-mcp-server) throughout; its finished, already-run counterpart is [hr-mcp-server-solution/](hr-mcp-server-solution).

## Step 1: See how six C# methods become six MCP tools

[hr-mcp-server/Tools/HRTools.cs](hr-mcp-server/Tools/HRTools.cs) is annotated `[McpServerToolType]`, each public method carries `[McpServerTool]`, and every parameter carries a `[Description]`. The SDK reads those attributes and builds the JSON Schema that clients see, so the C# description text is literally the tool documentation the model reads.

```csharp
[McpServerTool]
[Description("Assigns an employee to an 8-hour shift by name, date, and position")]
public async Task<string> AssignShift(
    [Description("Full or partial name of the employee")] string employeeName,
    [Description("Date of the shift in yyyy-MM-dd format")] string date,
    [Description("Position for the shift (e.g. bar, waiter, host, chef)")] string position,
    [Description("Hour (0-23) at which the 8-hour shift starts. Defaults to 8")] int shiftStartHour = 8)
```

**Expected result:** six methods carry `[McpServerTool]`, and none of them declares a name.

The SDK derives the wire name from the method name in lower snake case, so `AssignShift` becomes `assign_shift`, while parameter names such as `shiftStartHour` stay camel case.

## Step 2: List all six tools with the MCP Inspector

[hr-mcp-server/Program.cs](hr-mcp-server/Program.cs) registers `AddMcpServer().WithHttpTransport().WithToolsFromAssembly()` and calls `app.MapMcp()`, which maps the Streamable HTTP endpoint at the site root, so a plain `curl` on `http://localhost:47002` answers HTTP 400, the correct reply to a request with no MCP session. Start the server in your first terminal, then list the tools from a second one:

```bash
cd demos/04-mcp/02-mcp/hr-mcp-server
dotnet run
```

```bash
cd demos/04-mcp/02-mcp/hr-mcp-server
npx @modelcontextprotocol/inspector --config inspector.config.json --server hr-mcp --cli --method tools/list
```

**Expected result:** a `tools` array with six entries, each carrying the `[Description]` text from the C# source and a full `inputSchema`:

```json
  "name": "assign_shift",
  "description": "Assigns an employee to an 8-hour shift by name, date, and position",
      "employeeName": { "description": "Full or partial name of the employee", "type": "string" },
      "shiftStartHour": { "description": "Hour (0-23) at which the 8-hour shift starts. Defaults to 8", "type": "integer", "default": 8 }
    "required": ["employeeName", "date", "position"]
```

`required` names exactly the three parameters that have no C# default, which proves the schema is generated from the source.

## Step 3: Wire the server into your MCP clients

Call `assign_shift` against real data, then add the entry below to the project-level [.mcp.json](../../../.mcp.json). Claude Code uses the transport type `http` and the same root URL with no `/mcp` suffix.

```bash
npx @modelcontextprotocol/inspector --config inspector.config.json --server hr-mcp --cli --method tools/call --tool-name assign_shift --tool-arg employeeName=Kenji --tool-arg date=2026-08-01 --tool-arg position="sushi bar"
```

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

**Expected result:** the call returns `Assigned Kenji Tanaka to 'sushi bar' on 2026-08-01 from 08:00 to 16:00.`, and after reloading MCP connections `/mcp` reports `hr-mcp` connected with the same six tools.

Ask Claude "which employees speak French" and it calls `search_employees` on its own, with no integration code on the client side.

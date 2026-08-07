# Serve QR Codes from a C# MCP Server

Most MCP tools return text or JSON; the `generate_qr` tool returns a picture, handing back a content block of `type: image` so a compliant host displays the QR code inline instead of printing a wall of base64. You run the C# server over Streamable HTTP, verify the tool through the MCP Inspector CLI, generate two PNGs with different parameters, and wire the same assembly for stdio through `.vscode/mcp.json`. You also end with a clear reading of what this server does not do: it ships no `ui://` view resource, so hosts render the returned image and nothing more.

------

## Prerequisites

- .NET SDK 10.0 or later. `dotnet --version` reported `10.0.110` when this guide was verified.
- Node.js, for the MCP Inspector steps only. The inspector runs through `npx` and needs no install.
- Two terminals. The server occupies one for most of the demo.

You work in the starter folder [qr-mcp-app-cs/](qr-mcp-app-cs/) throughout. Its finished, already-run counterpart lives beside it as `qr-mcp-app-cs-solution/` if you want to compare against a completed reference.

## Step 1: Read the tool that returns an image

[qr-mcp-app-cs/Tools/QrTools.cs](qr-mcp-app-cs/Tools/QrTools.cs) holds a single static method. Unlike the HR server, this one names its tool explicitly with `[McpServerTool(Name = "generate_qr")]`, so the wire name is fixed rather than derived from the method name. The important line is the return type: `IEnumerable<ImageContentBlock>` instead of a string or a model class.

```csharp
[McpServerTool(Name = "generate_qr")]
[Description("Generate a QR code PNG image from text or URL. Returns a base64-encoded PNG image.")]
public static IEnumerable<ImageContentBlock> GenerateQr(
    [Description("Text or URL to encode in the QR code")] string text,
    [Description("Size in pixels of each QR module (box). Default: 5")] int box_size = 5,
    [Description("Width of the quiet zone border in modules. Default: 4")] int border = 4,
    [Description("Error correction level: L, M, Q, or H. Default: M")] string error_correction = "M",
    [Description("Foreground color as CSS name or hex (e.g. 'black', '#000000'). Default: black")] string fill_color = "black",
    [Description("Background color as CSS name or hex (e.g. 'white', '#ffffff'). Default: white")] string back_color = "white")
```

QRCoder renders the modules and ImageSharp paints the quiet zone around them, then the method returns one `ImageContentBlock` with `MimeType = "image/png"`. Note that the parameters are already snake case in the C# source, so the wire schema matches the source names exactly.

**Expected result:** you can name the six parameters and the one required one. Only `text` has no default, so every other argument is optional. `box_size` is clamped to 1 through 20 and `border` to 0 through 10 inside the method, which means an out-of-range value is silently corrected rather than rejected.

## Step 2: Start the server over Streamable HTTP

[qr-mcp-app-cs/Program.cs](qr-mcp-app-cs/Program.cs) branches on the command line. Without `--stdio` it builds a Kestrel host, registers `AddMcpServer().WithHttpTransport().WithToolsFromAssembly()`, adds a permissive CORS policy so a browser-based host can reach it, and calls `app.MapMcp()` before binding the port. The port is read from the `PORT` environment variable and falls back to 3002.

In your first terminal:

```bash
cd demos/04-mcp/03-mcp-apps/qr-mcp-app-cs
dotnet run
```

**Expected result:** Kestrel binds all interfaces on 3002 and the host reports it started:

```text
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: http://0.0.0.0:3002
info: Microsoft.Hosting.Lifetime[0]
      Application started. Press Ctrl+C to shut down.
```

The MCP endpoint is the site root, `http://localhost:3002/`, with no `/mcp` suffix. Leave this terminal running.

To bind another port instead, set `PORT` before the run command:

```bash
PORT=3010 dotnet run
```

```powershell
$env:PORT=3010; dotnet run
```

## Step 3: Confirm the root is an MCP endpoint, not a web page

A quick `curl` here tells you whether the process is up and speaking MCP, and it prevents a healthy server from looking broken the first time you open the URL in a browser.

From your second terminal:

```bash
curl -s -i http://localhost:3002/
```

**Expected result:** HTTP 400 with a JSON-RPC error body. That is the correct answer to a plain GET, because the server keeps MCP sessions and a browser sends no session header:

```text
HTTP/1.1 400 Bad Request
Content-Type: application/json; charset=utf-8
Server: Kestrel

{"error":{"code":-32000,"message":"Bad Request: Mcp-Session-Id header is required for GET and DELETE requests when the server is using sessions. ..."},"id":"","jsonrpc":"2.0"}
```

## Step 4: Discover the tool with the MCP Inspector

[qr-mcp-app-cs/inspector.config.json](qr-mcp-app-cs/inspector.config.json) holds a single target, `qr-server-cs`, pointing at `http://localhost:3002`. Because there is exactly one entry, the `--server` flag is optional for this project.

```bash
cd demos/04-mcp/03-mcp-apps/qr-mcp-app-cs
npx @modelcontextprotocol/inspector --config inspector.config.json --cli --method tools/list
```

**Expected result:** a `tools` array with exactly one entry. The schema is generated from the `[Description]` attributes you read in step 1, and `text` is the only required property:

```json
{
  "name": "generate_qr",
  "description": "Generate a QR code PNG image from text or URL. Returns a base64-encoded PNG image.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "text": { "description": "Text or URL to encode in the QR code", "type": "string" },
      "box_size": { "description": "Size in pixels of each QR module (box). Default: 5", "type": "integer", "default": 5 },
      "border": { "description": "Width of the quiet zone border in modules. Default: 4", "type": "integer", "default": 4 },
      "error_correction": { "description": "Error correction level: L, M, Q, or H. Default: M", "type": "string", "default": "M" },
      "fill_color": { "description": "Foreground color as CSS name or hex (e.g. 'black', '#000000'). Default: black", "type": "string", "default": "black" },
      "back_color": { "description": "Background color as CSS name or hex (e.g. 'white', '#ffffff'). Default: white", "type": "string", "default": "white" }
    },
    "required": ["text"]
  }
}
```

> **Warning:** on Windows the inspector CLI prints the complete, correct JSON and then crashes during teardown with `Assertion failed: !(handle->flags & UV_HANDLE_CLOSING), file src\win\async.c, line 76` followed by `Failed with exit code: 3221226505`. That is a libuv teardown bug in the inspector, not a fault in your server. The JSON printed above the assertion is the real answer.

## Step 5: Generate a QR code and read the content block

Call the tool with only the required argument:

```bash
npx @modelcontextprotocol/inspector --config inspector.config.json --cli --method tools/call --tool-name generate_qr --tool-arg text=https://modelcontextprotocol.io
```

**Expected result:** one content block with three keys, `type`, `data` and `mimeType`. The `data` value is base64 and begins `iVBORw0KGgo`, which is the PNG magic number, so you can confirm the payload is a real image without decoding it:

```json
{
  "content": [
    {
      "type": "image",
      "data": "iVBORw0KGgoAAAANSUhEUgAAALkAAAC5...",
      "mimeType": "image/png"
    }
  ]
}
```

With the defaults (`box_size` 5, `border` 4) that URL produces a 185 by 185 pixel PNG from a 29 module QR code: 29 modules at 5 pixels each, plus a 4 module quiet zone on both sides. Now change the geometry and the colour:

```bash
npx @modelcontextprotocol/inspector --config inspector.config.json --cli --method tools/call --tool-name generate_qr --tool-arg text=https://modelcontextprotocol.io --tool-arg box_size=10 --tool-arg border=2 --tool-arg error_correction=H --tool-arg fill_color=#0B5FFF
```

**Expected result:** a visibly longer `data` string for the same URL. The PNG is now 370 by 370 pixels: raising the error correction level to H pushes the code from 29 to 33 modules, `box_size` 10 doubles the pixels per module, and `border` 2 trims the quiet zone. Paste either base64 string into a data URL in a browser (`data:image/png;base64,` followed by the value) to see the code and scan it.

## Step 6: Wire the same server for stdio

The same assembly serves both transports, selected by one flag.

```bash
cd demos/04-mcp/03-mcp-apps/qr-mcp-app-cs
dotnet run -- --stdio
```

**Expected result:** the process starts and waits for input, and every log line goes to stderr so stdout carries JSON-RPC only. That routing is what `LogToStandardErrorThreshold = LogLevel.Trace` in `Program.cs` buys you; a single stray `Console.WriteLine` would corrupt the protocol stream. You see lines like these on stderr:

```text
info: ModelContextProtocol.Server.StdioServerTransport[857250842]
      Server (stream) (qr-mcp-app-cs) transport reading messages.
info: Microsoft.Hosting.Lifetime[0]
      Application started. Press Ctrl+C to shut down.
```

> **Note:** `dotnet run` prints its own launch and build messages (`Using launch settings from ...`, `Building...`) on stdout before your code starts. Those come from the CLI, not the server. Add `--no-launch-profile` when you want to drive the stdio stream by hand from a script.

The shipped client wiring for this mode is [qr-mcp-app-cs/.vscode/mcp.json](qr-mcp-app-cs/.vscode/mcp.json), which lets VS Code start the project on demand:

```json
{
  "servers": {
    "qr-code-cs": {
      "type": "stdio",
      "command": "dotnet",
      "args": ["run", "--project", "${workspaceFolder}/demos/04-mcp/03-mcp-apps/qr-mcp-app-cs", "--", "--stdio"]
    }
  }
}
```

For Claude Code in this repository the HTTP mode is already registered in the project-level [.mcp.json](../../../.mcp.json) under the name `qr-code`, pointing at `http://localhost:3002`. Start the server, reload MCP connections, and `/mcp` reports it connected with `generate_qr` available.

## Step 7: Check what this server does not expose

This C# project registers a tool only, so it is worth proving the absence rather than assuming it.

With the HTTP server still running:

```bash
npx @modelcontextprotocol/inspector --config inspector.config.json --cli --method resources/list
```

**Expected result:** the request is rejected, because the server never declared a resources capability during `initialize`:

```text
Failed to list resources: MCP error -32601: Method 'resources/list' is not available.
```

There is no `ui://` view here, so a host shows the returned PNG and nothing else. The reference implementation that adds the missing half is the Python sibling in [src/qr-mcp-app-py/readme.md](../../../src/qr-mcp-app-py/readme.md), which pairs `@mcp.tool(meta={"ui/resourceUri": VIEW_URI})` with `@mcp.resource(VIEW_URI)` where `VIEW_URI` is `ui://qr-server/view.html`.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `Failed to connect to MCP server: fetch failed` and `Failed with exit code: 1` | The inspector was started before the server, so nothing is listening on 3002 | Start `dotnet run` first, wait for `Now listening on: http://0.0.0.0:3002`, then run the inspector in the second terminal |
| Correct JSON, then `Assertion failed: !(handle->flags & UV_HANDLE_CLOSING)` and exit code `3221226505` | Known libuv teardown crash in the inspector CLI on Windows | Ignore it and read the JSON printed above it. The server is unaffected and keeps serving |
| `MCP error -32601: Method 'resources/list' is not available.` | Expected: this server registers a tool and no resources | Nothing to fix. Use the Python sibling for the `ui://` view pattern |
| `curl` on `http://localhost:3002` returns HTTP 400 | Correct behaviour: the root is an MCP endpoint that requires a session, not a web page | Use an MCP client. A 400 here confirms the server is up |
| The port is already taken and the host fails to bind | Another process holds 3002, often an earlier run that was never stopped | Stop the old process, or start this one with `PORT=3010 dotnet run` (PowerShell: `$env:PORT=3010; dotnet run`) and update the client URL |
| A stdio client reports a protocol parse error | Something wrote to stdout instead of stderr | Keep all logging on stderr; never add `Console.WriteLine` to a stdio server |

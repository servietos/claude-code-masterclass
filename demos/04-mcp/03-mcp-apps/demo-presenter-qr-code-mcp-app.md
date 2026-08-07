---
presents: demo-qr-code-mcp-app.md
budget: 5 min
beats: 5
---

# Present: Serve QR Codes from a C# MCP Server

A tool that returns a picture is not an MCP App: the difference is one content block type plus a `ui://` resource this C# server never declares. Five beats: the image return type, the three keys the host receives, one assembly on two transports, arguments clamped rather than rejected, the proof that the view resource is absent.

------

## Beats

### Beat 1: returning an image is a return type, not a protocol feature (1 min)

**Open:** [`qr-mcp-app-cs/Tools/QrTools.cs`](qr-mcp-app-cs/Tools/QrTools.cs) · [`../02-mcp/hr-mcp-server/Tools/HRTools.cs`](../02-mcp/hr-mcp-server/Tools/HRTools.cs) · the string-returning tools this is compared against
**Say:** The natural assumption is that a server whose output a person looks at is a different category of thing. It is the same server: registration, discovery and transport are untouched.

```csharp
    [McpServerTool(Name = "generate_qr")]
    [Description("Generate a QR code PNG image from text or URL. Returns a base64-encoded PNG image.")]
    public static IEnumerable<ImageContentBlock> GenerateQr(
        [Description("Text or URL to encode in the QR code")] string text,
...
            new ImageContentBlock
            {
                MimeType = "image/png",
                Data = Encoding.UTF8.GetBytes(b64)
            }
```

**Result:** no file written; the discovered schema names one tool and its inputs, and says nothing about the image

```json
  "name": "generate_qr",
  "description": "Generate a QR code PNG image from text or URL. Returns a base64-encoded PNG image.",
...
    "required": ["text"]
```

**Gotcha:** two differences from the HR server and only two: an explicit tool name, and an `IEnumerable<ImageContentBlock>` return.

### Beat 2: what the host receives is three keys (1 min)

**Open:** [`qr-mcp-app-cs/Tools/QrTools.cs`](qr-mcp-app-cs/Tools/QrTools.cs) · the `ImageContentBlock` these keys serialize from · [Step 5: Generate a QR code and read the content block](demo-qr-code-mcp-app.md#step-5-generate-a-qr-code-and-read-the-content-block)
**Say:** The protocol has no concept of pictures, only of typed content blocks, and the type is what tells a host to render rather than to read. Rich output is agreed in a single field.

```bash
npx @modelcontextprotocol/inspector --config inspector.config.json --cli --method tools/call --tool-name generate_qr --tool-arg text=https://modelcontextprotocol.io
```

**Result:** no file written; `data` opens with `iVBORw0KGgo`, the base64 PNG magic number, so the block is a real image before anything decodes it

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

**Gotcha:** pasting that `data` string after `data:image/png;base64,` in a browser is the fastest way to prove it in the room.

### Beat 3: one assembly, two transports, one flag, and stdout stays sacred (1 min)

**Open:** [`qr-mcp-app-cs/Program.cs`](qr-mcp-app-cs/Program.cs) · the `--stdio` branch · [`qr-mcp-app-cs/.vscode/mcp.json`](qr-mcp-app-cs/.vscode/mcp.json)
**Say:** Transport is a hosting decision, not a rewrite. The catch with stdio is that the process's own stdout becomes the wire, so anything printed for a human corrupts the protocol.

```csharp
	hostBuilder.Logging.AddConsole(options =>
	{
		options.LogToStandardErrorThreshold = LogLevel.Trace;
	});

	hostBuilder.Services.AddMcpServer()
		.WithStdioServerTransport()
		.WithToolsFromAssembly();
```

**Result:** no file written; started with `dotnet run -- --stdio`, the same assembly puts every log line on stderr

```text
info: ModelContextProtocol.Server.StdioServerTransport[857250842]
      Server (stream) (qr-mcp-app-cs) transport reading messages.
info: Microsoft.Hosting.Lifetime[0]
      Application started. Press Ctrl+C to shut down.
```

**Gotcha:** below `if (args.Contains("--stdio"))` the only difference is `WithStdioServerTransport()` where the HTTP branch has `WithHttpTransport()`.

### Beat 4: arguments are clamped, never rejected (1 min)

**Open:** [`qr-mcp-app-cs/Tools/QrTools.cs`](qr-mcp-app-cs/Tools/QrTools.cs) · the `Math.Clamp` pair and the `eccLevel` switch · [`qr-mcp-app-cs/readme.md`](qr-mcp-app-cs/readme.md)
**Say:** A model guesses at values and does not go back to check the documentation. Correcting quietly means the call always succeeds, until nobody can explain why the result does not match what was asked for.

```csharp
        var safeBoxSize = Math.Clamp(box_size, 1, 20);
        var safeBorder = Math.Clamp(border, 0, 10);

        var eccLevel = error_correction.ToUpperInvariant() switch
        {
            "L" => QRCodeGenerator.ECCLevel.L,
            "Q" => QRCodeGenerator.ECCLevel.Q,
            "H" => QRCodeGenerator.ECCLevel.H,
            _ => QRCodeGenerator.ECCLevel.M
        };
```

**Result:** no file written; the defaults give 29 modules at 5 pixels plus a 4 module quiet zone, so 185 by 185, while `error_correction=H` with `box_size=10` and `border=2` gives 33 modules at 370 by 370.

**Gotcha:** the model is never told that its `box_size` was clamped or its `error_correction` letter unrecognised.

### Beat 5: a tool-only server is not an MCP App, and you prove the absence (1 min)

**Open:** [`src/qr-mcp-app-py/server.py`](../../../src/qr-mcp-app-py/server.py) · the paired decorators that add the missing half · [Step 7: Check what this server does not expose](demo-qr-code-mcp-app.md#step-7-check-what-this-server-does-not-expose)
**Say:** An App needs a view the host can fetch and a tool that points at it, and either half alone is still just a tool. A capability never declared at handshake is genuinely missing, so the absence can be proved rather than asserted.

```bash
npx @modelcontextprotocol/inspector --config inspector.config.json --cli --method resources/list
```

**Result:** no file written; the string `ui://` appears nowhere under [`qr-mcp-app-cs/`](qr-mcp-app-cs/), and the server rejects a method it never declared

```text
Failed to list resources: MCP error -32601: Method 'resources/list' is not available.
```

**Gotcha:** the `-32601` is not a bug: this demo ships the image half of an App and nothing more.

## If the room asks

| Question | Answer |
|---|---|
| What would make it a real App? | The Python sibling pairs `@mcp.tool(meta={"ui/resourceUri": VIEW_URI})` with `@mcp.resource(VIEW_URI)` where `VIEW_URI` is `ui://qr-server/view.html`. |
| What does the run change on disk? | Only paths pointing at themselves: `.vscode/mcp.json` and `readme.md` differ between starter and solution, and `types.txt` exists in the starter alone. |
| The inspector printed the right JSON and then crashed. | Known libuv teardown bug in the inspector CLI on Windows (`UV_HANDLE_CLOSING`, exit code `3221226505`); read the JSON printed above the assertion. |
| Port 3002 is already taken. | `PORT=3010 dotnet run`, or `$env:PORT=3010; dotnet run` in PowerShell; update the client URL to match. |
| Is it registered for Claude Code in this repo? | Yes, HTTP mode is in the project-level [.mcp.json](../../../.mcp.json) as `qr-code` on `http://localhost:3002`. |

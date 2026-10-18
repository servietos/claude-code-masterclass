# Serve QR Codes from a C# MCP Server

Most MCP tools return text or JSON; the `generate_qr` tool returns a picture, handing back a content block of `type: image` so a compliant host displays the QR code inline. You run the C# server over Streamable HTTP, verify the tool through the MCP Inspector CLI, generate a PNG, and wire the same assembly for stdio through `.vscode/mcp.json`.

------

You work in the starter folder [qr-mcp-app-cs/](qr-mcp-app-cs) throughout; its finished, already-run counterpart is [qr-mcp-app-cs-solution/](qr-mcp-app-cs-solution).

## Step 1: Read the tool that returns an image

[qr-mcp-app-cs/Tools/QrTools.cs](qr-mcp-app-cs/Tools/QrTools.cs) names its tool explicitly with `[McpServerTool(Name = "generate_qr")]`, so the wire name is fixed. The important line is the return type, `IEnumerable<ImageContentBlock>`:

```csharp
[McpServerTool(Name = "generate_qr")]
[Description("Generate a QR code PNG image from text or URL. Returns a base64-encoded PNG image.")]
public static IEnumerable<ImageContentBlock> GenerateQr(
    [Description("Text or URL to encode in the QR code")] string text,
```

**Expected result:** you can name the six parameters and the one required one. Only `text` has no default, so every other argument is optional.

`box_size` is clamped to 1 through 20 and `border` to 0 through 10 inside the method, which means an out-of-range value is silently corrected.

## Step 2: Discover the tool with the MCP Inspector

[qr-mcp-app-cs/Program.cs](qr-mcp-app-cs/Program.cs) registers `AddMcpServer().WithHttpTransport().WithToolsFromAssembly()` and calls `app.MapMcp()`, so the MCP endpoint is the site root on port 3002, and a plain `curl` there answers HTTP 400 because a browser sends no session header. Start the server in your first terminal, then discover the tool from a second one:

```bash
cd demos/04-mcp/03-mcp-apps/qr-mcp-app-cs
dotnet run
```

```bash
cd demos/04-mcp/03-mcp-apps/qr-mcp-app-cs
npx @modelcontextprotocol/inspector --cli --config inspector.config.json --method tools/list
```

**Expected result:** a `tools` array with exactly one entry, generated from the `[Description]` attributes you read in step 1:

```json
  "name": "generate_qr",
  "description": "Generate a QR code PNG image from text or URL. Returns a base64-encoded PNG image.",
      "text": { "description": "Text or URL to encode in the QR code", "type": "string" },
      "box_size": { "description": "Size in pixels of each QR module (box). Default: 5", "type": "integer", "default": 5 },
    "required": ["text"]
```

The schema says nothing about the image: returning a picture changes the return type and leaves registration and discovery untouched.

## Step 3: Generate a QR code and read the content block

Call the tool with only the required argument, then start the same assembly for stdio, the mode [qr-mcp-app-cs/.vscode/mcp.json](qr-mcp-app-cs/.vscode/mcp.json) launches on demand.

```bash
npx @modelcontextprotocol/inspector --cli --config inspector.config.json --method tools/call --tool-name generate_qr --tool-arg text=https://modelcontextprotocol.io
```

**Expected result:** one content block with three keys; the `data` value is base64 and begins `iVBORw0KGgo`, which is the PNG magic number:

```json
      "type": "image",
      "data": "iVBORw0KGgoAAAANSUhEUgAAALkAAAC5...",
      "mimeType": "image/png"
```

```bash
cd demos/04-mcp/03-mcp-apps/qr-mcp-app-cs
dotnet run -- --stdio
```

The stdio process waits for input and writes every log line to stderr, because `LogToStandardErrorThreshold = LogLevel.Trace` keeps stdout for JSON-RPC alone.

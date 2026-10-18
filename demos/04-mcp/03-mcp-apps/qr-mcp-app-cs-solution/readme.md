# Build a QR Code Generator MCP Server in C#

A .NET 10 MCP server that exposes one tool, `generate_qr`, which encodes text or a URL into a QR code and returns it as a base64 PNG image block. It speaks Streamable HTTP on port 3002 and stdio with the `--stdio` flag.

This folder is the completed reference for the starter at `qr-mcp-app-cs/`.

## Prerequisites

- .NET SDK 10.0 or later (`dotnet --version`)
- Node.js, only for the MCP Inspector step

## Run over HTTP

```bash
cd demos/04-mcp/03-mcp-apps/qr-mcp-app-cs-solution
dotnet run
```

Kestrel logs `Now listening on: http://0.0.0.0:3002`. The MCP endpoint is the site root, `http://localhost:3002/`, with no `/mcp` suffix. A plain browser GET answers HTTP 400 by design, with JSON-RPC error `-32000` and the message `Mcp-Session-Id header is required for GET and DELETE requests when the server is using sessions`. The server runs in session mode, so a GET only succeeds once a client has completed `initialize` and can echo the session id back; adding an `Accept` header alone does not change the response. Set `PORT` to bind another port.

## Run over stdio

```bash
dotnet run -- --stdio
```

Use this mode from `.vscode/mcp.json`, which starts the project with `dotnet run --project ... -- --stdio`. Logging goes to stderr so the server's stdout carries JSON-RPC only; `dotnet run` prints its own two status lines (`Using launch settings`, `Building...`) to stdout before the server starts.

## Tool reference

| Parameter | Type | Default | Purpose |
| --- | --- | --- | --- |
| `text` | string | required | Text or URL to encode |
| `box_size` | integer | 5 | Pixels per QR module, clamped to 1-20 |
| `border` | integer | 4 | Quiet zone width in modules, clamped to 0-10 |
| `error_correction` | string | M | L, M, Q or H |
| `fill_color` | string | black | Foreground, CSS name or hex |
| `back_color` | string | white | Background, CSS name or hex |

## Test with MCP Inspector

Keep `dotnet run` going in one terminal, then in a second terminal:

```bash
cd demos/04-mcp/03-mcp-apps/qr-mcp-app-cs-solution
npx @modelcontextprotocol/inspector --config inspector.config.json
```

The inspector opens on `http://localhost:6274` and connects to the streamable-http endpoint declared in `inspector.config.json`. The config holds a single server, so the `--server` flag is optional here. Calling `generate_qr` returns a content block with `type: image` and `mimeType: image/png`.

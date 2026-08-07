# Build a QR Code Generator MCP Server in C#

A .NET 10 MCP server that exposes one tool, `generate_qr`, which encodes text or a URL into a QR code and returns it as a base64 PNG image block. It speaks Streamable HTTP on port 3002 and stdio with the `--stdio` flag.

This folder is the starter you work in. The completed reference lives beside it in `qr-mcp-app-cs-solution/`.

## Prerequisites

- .NET SDK 10.0 or later (`dotnet --version`)
- Node.js, only for the MCP Inspector step

## Tool reference

| Parameter | Type | Default | Purpose |
| --- | --- | --- | --- |
| `text` | string | required | Text or URL to encode |
| `box_size` | integer | 5 | Pixels per QR module, clamped to 1-20 |
| `border` | integer | 4 | Quiet zone width in modules, clamped to 0-10 |
| `error_correction` | string | M | L, M, Q or H |
| `fill_color` | string | black | Foreground, CSS name or hex |
| `back_color` | string | white | Background, CSS name or hex |

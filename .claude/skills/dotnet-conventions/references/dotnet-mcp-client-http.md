# Connecting an MCP client over HTTP

## Explicit StreamableHttp skips the discovery probe

`HttpClientTransportOptions.TransportMode = HttpTransportMode.StreamableHttp` makes the 2.x client
go straight to `POST initialize`. Leave the mode unset and it probes `GET /mcp` first, which is the
source of the "MCP calls got slower after the upgrade" report: a server that does not answer that
GET can leave the client waiting on a timeout.

Measured on a server that rejects the GET outright (405 in 65ms, no hang): a client constructed
**per call** costs roughly 65-70ms over a plain REST call to the same host, which is one extra
round trip for the handshake. That is worth caching only if the path is hot. Measure before caching:
the per-call construction is visible in a profiler and invisible in a stopwatch at low volume.

## MCP Client Configuration for HTTP Transport

```json
{
  "mcpServers": {
    "my-server": {
      "url": "http://localhost:47000/mcp"
    }
  }
}
```

The `/mcp` path is the default mount point set by `app.MapMcp()`.

Back to the index: [dotnet-mcp](dotnet-mcp.md)

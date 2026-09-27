# .NET MCP Server Reference

General-purpose reference for building a .NET MCP (Model Context Protocol) server using `ModelContextProtocol` and `ModelContextProtocol.AspNetCore`. Use this file when creating or extending any .NET MCP server project.

| You want to... | Read |
| --- | --- |
| Pin a ModelContextProtocol version, and see what changed silently in 2.x. | [dotnet-mcp-packages](dotnet-mcp-packages.md) |
| Stand up an MCP server on Kestrel: AddMcpServer, WithHttpTransport, WithToolsFromAssembly, MapMcp, and choosing the port. | [dotnet-mcp-http-host](dotnet-mcp-http-host.md) |
| Author a tool: McpServerToolType, McpServerTool, the mandatory Description on every parameter, return types, optional and nullable parameters. | [dotnet-mcp-tool-class](dotnet-mcp-tool-class.md) |
| Fix a tool missing from `tools/list`, or a surface change with no effect: the catalog is built at boot. | [dotnet-mcp-catalog-restart](dotnet-mcp-catalog-restart.md) |
| Configure a client for an HTTP server, and see why calls got slower after the 2.x upgrade. | [dotnet-mcp-client-http](dotnet-mcp-client-http.md) |
| Target Claude Desktop or GitHub Copilot instead of an HTTP client: the console host and the `mcp.json` command/args entry. | [dotnet-mcp-stdio](dotnet-mcp-stdio.md) |

`HttpServerTransportOptions.Stateless` now defaults to **true**.

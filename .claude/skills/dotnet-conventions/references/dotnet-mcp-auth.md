# .NET MCP Server: auth, trust levels and the reverse proxy

Routing table for authenticating and authorizing an ASP.NET Core MCP server: proxy-aware OAuth discovery, per-tool trust levels in one process, and dual schemes on `/mcp`.

The trust boundary is the **data**, not the transport.

| You want to... | Read |
| --- | --- |
| Claude says "Automatic client registration isn't supported", or the 401 advertises an http:// resource_metadata URL on an https site. | [dotnet-mcp-auth-forwarded-headers](dotnet-mcp-auth-forwarded-headers.md) |
| How do I serve public and admin tools from one MCP process instead of splitting into two projects? | [dotnet-mcp-auth-per-tool-authorize](dotnet-mcp-auth-per-tool-authorize.md) |
| The [Authorize] filter is wired but an X-API-Key caller reads as anonymous, or the guard test passes while measuring nothing. | [dotnet-mcp-auth-per-tool-pitfalls](dotnet-mcp-auth-per-tool-pitfalls.md) |
| What must the tools/list guard test assert, and when is splitting into two MCP projects still the right call? | [dotnet-mcp-auth-guard-tests](dotnet-mcp-auth-guard-tests.md) |
| How do I gate /mcp for both OAuth clients and header-only clients, and why does the API-key handler break JWT? | [dotnet-mcp-auth-dual-scheme](dotnet-mcp-auth-dual-scheme.md) |

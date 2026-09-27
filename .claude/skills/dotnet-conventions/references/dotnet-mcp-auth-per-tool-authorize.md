# Per-tool [Authorize] on one MCP server (2.2)

## Two trust levels on one server: `[Authorize]` per tool, from 2.2

Before `ModelContextProtocol.AspNetCore` 2.2 this was a hard split: `AddMcpServer()` is a single DI
registration and `MapMcp` takes only a route pattern, so `/mcp` and `/mcp/admin` in one process
served **the same tools twice** with two auth decisions in front of identical capability, and the
remedy was two projects.

2.2 removes the constraint. `IMcpServerBuilder.AddAuthorizationFilters()` honours
`[Authorize]` and `[AllowAnonymous]` on individual tools, prompts and resources, and its
`FilterAuthorizedItemsAsync` filters **list** operations too, so a protected tool is invisible to a
caller who may not call it. Tool authorization runs before background dispatch, so a refused call
never executes.

```csharp
builder.Services.AddMcpServer()
    .WithHttpTransport()
    .AddAuthorizationFilters()
    .WithTools<PublicTools>()
    .WithTools<AdminTools>();

app.MapMcp("/mcp").AllowAnonymous();   // the endpoint stays open; each tool decides
```

```csharp
[McpServerTool]
[Authorize(Policy = "McpAdmin")]
[Description("...")]
public async Task<InquiryListResult> list_inquiries(...) => ...
```


Back to the index: [dotnet-mcp-auth](dotnet-mcp-auth.md)

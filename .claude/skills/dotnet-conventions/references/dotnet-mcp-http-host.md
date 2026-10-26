# Program.cs for the HTTP-transport MCP host

## Program.cs — HTTP Transport

```csharp
using ModelContextProtocol.Server;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddDbContext<MyDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("MyDb")));
builder.Services.AddScoped<IMyService, MyService>();

builder.Services.AddMcpServer()
    .WithHttpTransport()
    .WithToolsFromAssembly();

var app = builder.Build();

app.MapMcp();

app.Run();
```

- `AddMcpServer()` registers MCP protocol infrastructure.
- `.WithHttpTransport()` uses ASP.NET Core Kestrel as the transport — no stdio.
- `.WithToolsFromAssembly()` auto-discovers every class marked `[McpServerToolType]`.
- `app.MapMcp()` mounts the MCP routes onto the HTTP pipeline at `/mcp`.

## Kestrel Port Configuration

```json
{
  "Kestrel": {
    "Endpoints": {
      "Http": { "Url": "http://*:47000" }
    }
  }
}
```

Choose an unused port (e.g., 47001, 47002, 3001) that does not conflict with other services running on the host.

## Rate limiting a public endpoint

`app.MapMcp("/mcp").RequireRateLimiting("mcp")` puts every JSON-RPC call (initialize, tools/list, each tools/call) in one bucket. Size it for a real agent session, not for single calls: 10 per minute ran out after one connect, one list and a handful of calls. The default rejection is an empty 429, which clients and MCP Inspector show as an empty result. Return a readable body:

```csharp
options.OnRejected = async (ctx, ct) =>
{
    var seconds = ctx.Lease.TryGetMetadata(MetadataName.RetryAfter, out var ra) ? (int)ra.TotalSeconds : 60;
    ctx.HttpContext.Response.Headers.RetryAfter = seconds.ToString();
    await ctx.HttpContext.Response.WriteAsJsonAsync(new { error = "rate_limited", message = $"Too many requests. Retry after {seconds} seconds.", retryAfterSeconds = seconds }, ct);
};
```

Verify by looping `tools/list` past the limit and checking the status, `Retry-After` and body of the first 429.

Back to the index: [dotnet-mcp](dotnet-mcp.md)

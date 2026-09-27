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

Back to the index: [dotnet-mcp](dotnet-mcp.md)

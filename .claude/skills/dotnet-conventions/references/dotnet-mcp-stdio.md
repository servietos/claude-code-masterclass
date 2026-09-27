# Stdio transport for Claude Desktop and Copilot

## Stdio Transport

Use a console host when targeting Claude Desktop or GitHub Copilot instead of an HTTP client:

```csharp
var builder = Host.CreateApplicationBuilder(args);

builder.Services.AddMcpServer()
    .WithStdioServerTransport()
    .WithToolsFromAssembly();

builder.Services.AddScoped<IMyService, MyService>();

await builder.Build().RunAsync();
```

Client config in `.vscode/mcp.json` or `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "dotnet",
      "args": ["run", "--project", "src/my-mcp-server"]
    }
  }
}
```

Back to the index: [dotnet-mcp](dotnet-mcp.md)

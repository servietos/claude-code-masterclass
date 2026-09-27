# Writing an MCP tool class

## Tool Class Structure

```csharp
using System.ComponentModel;
using ModelContextProtocol.Server;

[McpServerToolType]
internal class MyTools
{
    private readonly IMyService _service;
    private readonly ILogger<MyTools> _logger;

    public MyTools(IMyService service, ILogger<MyTools> logger)
    {
        _service = service;
        _logger = logger;
    }

    [McpServerTool]
    [Description("Short description of what this tool does")]
    public async Task<string> DoSomething(
        [Description("What this parameter controls")] string input,
        [Description("Optional flag with a default")] bool flag = false)
    {
        var result = await _service.ProcessAsync(input, flag);
        return result;
    }
}
```

- One `[McpServerToolType]` per class; one `[McpServerTool]` per method.
- Every parameter must have a `[Description("...")]` attribute — MCP clients use this for introspection.
- Return `string` for simple text results; return a typed DTO for structured data.
- Optional parameters use default values (`= false`, `= 8`, etc.).
- Nullable parameters (`string?`) accept absent values from the MCP client.
- All tools should be `async Task<T>` unless computation is truly synchronous.

Back to the index: [dotnet-mcp](dotnet-mcp.md)

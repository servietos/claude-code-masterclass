# What crosses the wire: return types and snake_case tool names

## Returning Structured Data

```csharp
public class ItemCollection
{
    public List<Item> Items { get; set; } = [];
}

public class Item
{
    [JsonPropertyName("id")]
    public int Id { get; set; }

    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
}

[McpServerTool]
[Description("Returns all items")]
public async Task<ItemCollection> ListItems()
{
    var items = await _service.GetAllAsync();
    return new ItemCollection { Items = items };
}
```

MCP tools can return plain strings or any JSON-serializable type. Use DTOs whenever the response has more than one field.

## Tool names are snake_case on the wire

`WithToolsFromAssembly()` exposes `GetPeriodSummary` as `get_period_summary`. Scripting `/mcp` with
the C# method name fails at the JSON-RPC layer, not in your code. Read the names off `tools/list`.

Back to the index: [dotnet-mcp-tool-design](dotnet-mcp-tool-design.md)

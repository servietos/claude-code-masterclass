# A2UI Component Node Model

### Component Nodes

A2UI v0.9 uses a flat adjacency-list model. Every entry in `updateComponents.components` has:

- `id`: unique string within the surface
- `component`: catalog type name (`"Text"`, `"Button"`, `"Column"`, etc.)
- Exactly one component per message must carry `"id": "root"` to anchor the tree
- Component-specific properties (`text`, `children`, `action`, `value`, ...) sit at the same JSON level as `id` and `component`

Use `[JsonExtensionData]` to carry the variable per-type properties without defining per-component records:

```csharp
public record A2UiComponentNode
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("component")]
    public required string Component { get; init; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement>? Properties { get; init; }
}
```

Back to the index: [dotnet-a2ui-messages](dotnet-a2ui-messages.md)

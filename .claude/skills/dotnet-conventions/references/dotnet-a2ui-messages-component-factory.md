# A2UI Component Factory

### Component Factory

Build component nodes via static factory methods:

```csharp
public static class A2UiComponent
{
    private static readonly JsonSerializerOptions s_opts = new(JsonSerializerDefaults.Web);
    private static JsonElement E<T>(T value) => JsonSerializer.SerializeToElement(value, s_opts);

    public static A2UiComponentNode Column(string id, params string[] childIds) =>
        new() { Id = id, Component = "Column", Properties = new() { ["children"] = E(childIds) } };

    public static A2UiComponentNode Row(string id, params string[] childIds) =>
        new() { Id = id, Component = "Row", Properties = new() { ["children"] = E(childIds) } };

    public static A2UiComponentNode Card(string id, params string[] childIds) =>
        new() { Id = id, Component = "Card", Properties = new() { ["children"] = E(childIds) } };

    public static A2UiComponentNode Text(string id, object textBinding, string? usageHint = null)
    {
        var props = new Dictionary<string, JsonElement> { ["text"] = E(textBinding) };
        if (usageHint is not null) props["usageHint"] = E(usageHint);
        return new() { Id = id, Component = "Text", Properties = props };
    }

    public static A2UiComponentNode Button(string id, string childId, string actionName,
        object? context = null) =>
        new()
        {
            Id = id,
            Component = "Button",
            Properties = new()
            {
                ["child"] = E(childId),
                ["action"] = E(new { @event = new { name = actionName, context = context ?? (object)new { } } })
            }
        };

    public static A2UiComponentNode TextField(string id, string dataPath, string? placeholder = null)
    {
        var props = new Dictionary<string, JsonElement> { ["value"] = E(new { path = dataPath }) };
        if (placeholder is not null) props["placeholder"] = E(placeholder);
        return new() { Id = id, Component = "TextField", Properties = props };
    }

    public static A2UiComponentNode DateTimeInput(string id, string dataPath,
        bool enableDate = true, bool enableTime = false) =>
        new()
        {
            Id = id,
            Component = "DateTimeInput",
            Properties = new()
            {
                ["value"] = E(new { path = dataPath }),
                ["enableDate"] = E(enableDate),
                ["enableTime"] = E(enableTime)
            }
        };
}
```

Usage:

```csharp
var components = new[]
{
    A2UiComponent.Column("root", "title", "date-input", "lbl-confirm", "submit-btn"),
    A2UiComponent.Text("title", "Reserve a Table", usageHint: "h1"),
    A2UiComponent.DateTimeInput("date-input", "/reservation/date"),
    A2UiComponent.Text("lbl-confirm", "Confirm"),
    A2UiComponent.Button("submit-btn", "lbl-confirm", "submit_booking",
        context: new { date = A2UiBind.Path("/reservation/date"), partySize = A2UiBind.Path("/reservation/partySize") })
};
```

Back to the index: [dotnet-a2ui-messages](dotnet-a2ui-messages.md)

# A2UI Data Binding Helpers

### Data Binding Helpers

A2UI v0.9 data bindings are plain JSON objects. Provide helpers to avoid magic anonymous-type literals at call sites:

```csharp
public static class A2UiBind
{
    public static object Path(string jsonPointer) => new { path = jsonPointer };

    public static object FormatString(string template) =>
        new { call = "formatString", args = new { value = template } };
}
```

Binding patterns:

| Source | C# | Serialized JSON |
|---|---|---|
| Literal string | `"Hello"` | `"Hello"` |
| Data model path | `A2UiBind.Path("/user/name")` | `{"path":"/user/name"}` |
| Interpolated | `A2UiBind.FormatString("Hi, ${/user/name}!")` | `{"call":"formatString","args":{"value":"Hi, ${/user/name}!"}}` |

Paths starting with `/` resolve from the data model root. Paths without a leading `/` resolve relative to the current collection item (inside templated `children`).

Back to the index: [dotnet-a2ui-messages](dotnet-a2ui-messages.md)

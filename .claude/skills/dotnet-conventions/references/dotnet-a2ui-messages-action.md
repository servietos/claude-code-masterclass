# A2UI Client Action Messages

### Client-to-Server Action

The Angular client POSTs an action event when the user interacts with a component. Deserialize it:

```csharp
public record A2UiActionMessage(
    [property: JsonPropertyName("version")] string Version,
    [property: JsonPropertyName("action")] A2UiActionPayload Action);

public record A2UiActionPayload(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("surfaceId")] string SurfaceId,
    [property: JsonPropertyName("sourceComponentId")] string SourceComponentId,
    [property: JsonPropertyName("timestamp")] string Timestamp,
    [property: JsonPropertyName("context")] JsonElement Context);
```

Wire format the client sends:

```json
{
  "version": "v0.9",
  "action": {
    "name": "submit_booking",
    "surfaceId": "main",
    "sourceComponentId": "submit-btn",
    "timestamp": "2026-07-01T18:30:00Z",
    "context": {
      "date": "2026-07-15",
      "partySize": 4
    }
  }
}
```

The context values are fully resolved by the renderer before dispatch: all `{"path":"..."}` references in the component's action definition are replaced with their current data model values.

Back to the index: [dotnet-a2ui-messages](dotnet-a2ui-messages.md)

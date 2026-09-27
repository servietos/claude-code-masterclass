# A2UI Envelope and Payload Records

## C# Message Types

### Envelope and Payloads

All server-to-client A2UI v0.9 messages share `"version": "v0.9"` and carry exactly one payload property.

```csharp
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.Json.Serialization;

namespace MyApp.A2Ui;

public record A2UiEnvelope
{
    [JsonPropertyName("version")]
    public string Version { get; init; } = "v0.9";

    [JsonPropertyName("createSurface")]
    public CreateSurfacePayload? CreateSurface { get; init; }

    [JsonPropertyName("updateComponents")]
    public UpdateComponentsPayload? UpdateComponents { get; init; }

    [JsonPropertyName("updateDataModel")]
    public UpdateDataModelPayload? UpdateDataModel { get; init; }

    [JsonPropertyName("deleteSurface")]
    public DeleteSurfacePayload? DeleteSurface { get; init; }
}

public record CreateSurfacePayload(
    [property: JsonPropertyName("surfaceId")] string SurfaceId,
    [property: JsonPropertyName("catalogId")] string CatalogId,
    [property: JsonPropertyName("theme")] A2UiTheme? Theme = null,
    [property: JsonPropertyName("sendDataModel")] bool? SendDataModel = null);

public record A2UiTheme(
    [property: JsonPropertyName("primaryColor")] string? PrimaryColor = null,
    [property: JsonPropertyName("agentDisplayName")] string? AgentDisplayName = null);

public record UpdateComponentsPayload(
    [property: JsonPropertyName("surfaceId")] string SurfaceId,
    [property: JsonPropertyName("components")] A2UiComponentNode[] Components);

public record UpdateDataModelPayload(
    [property: JsonPropertyName("surfaceId")] string SurfaceId,
    [property: JsonPropertyName("path")] string? Path = null,
    [property: JsonPropertyName("value")] JsonNode? Value = null);

public record DeleteSurfacePayload(
    [property: JsonPropertyName("surfaceId")] string SurfaceId);
```

Back to the index: [dotnet-a2ui-messages](dotnet-a2ui-messages.md)

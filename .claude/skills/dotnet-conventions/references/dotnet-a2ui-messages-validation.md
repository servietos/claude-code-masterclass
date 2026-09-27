# A2UI Schema Validation

## Validation

Validate the LLM output against the catalog schema before sending it to the client. This catches hallucinated component names and malformed bindings at the server boundary.

```csharp
using Json.Schema;

public class A2UiValidator(A2UiCatalogService catalog)
{
    private readonly JsonSchema _schema = JsonSchema.FromText(catalog.Json);

    public void ValidateOrThrow(string json)
    {
        var node = JsonNode.Parse(json);
        var result = _schema.Evaluate(node, new EvaluationOptions
        {
            OutputFormat = OutputFormat.Basic
        });

        if (result.IsValid) return;

        var errors = string.Join("; ", result.Details
            .Where(d => !d.IsValid && d.HasErrors)
            .SelectMany(d => d.Errors ?? [])
            .Select(e => e.Value));

        throw new InvalidOperationException($"A2UI schema validation failed: {errors}");
    }
}
```

Scope note: the A2UI catalog (`catalog.json`) defines component schemas. The message envelope schema lives in a separate file (`server_to_client.json`) in the specification repository. For full envelope validation, load `server_to_client.json` as a second schema and run a second pass. Deserializing through `JsonSerializer.Deserialize<List<A2UiEnvelope>>` already catches envelope structural errors, so envelope schema validation is optional.

Back to the index: [dotnet-a2ui-messages](dotnet-a2ui-messages.md)

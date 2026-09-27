# A2UI Agent Service: LLM Call, Parse and Validate

## Agent Endpoint

### Service

The agent service calls an OpenAI-compatible chat completion endpoint, parses the LLM output, validates it, and returns the typed envelope list.

```csharp
using System.Net.Http.Headers;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Extensions.Options;

public class A2UiAgentService(
    HttpClient http,
    IOptions<A2UiOptions> opts,
    A2UiCatalogService catalog,
    A2UiValidator validator)
{
    private static readonly JsonSerializerOptions s_json = new(JsonSerializerDefaults.Web)
    {
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
    };

    private const string JsonDelimiter = "---a2ui_JSON---";

    public async Task<IReadOnlyList<A2UiEnvelope>> QueryAsync(
        string naturalLanguageQuery, CancellationToken ct = default)
    {
        var o = opts.Value;
        var body = new
        {
            model = o.LlmModel,
            messages = new[]
            {
                new { role = "system", content = BuildSystemPrompt(o) },
                new { role = "user", content = naturalLanguageQuery }
            }
        };

        using var req = new HttpRequestMessage(
            HttpMethod.Post, $"{o.LlmEndpoint.TrimEnd('/')}/chat/completions");
        req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", o.LlmApiKey);
        req.Content = JsonContent.Create(body, options: s_json);

        using var resp = await http.SendAsync(req, ct);
        resp.EnsureSuccessStatusCode();

        var doc = await resp.Content.ReadFromJsonAsync<JsonElement>(cancellationToken: ct);
        var raw = doc.GetProperty("choices")[0]
                     .GetProperty("message")
                     .GetProperty("content")
                     .GetString() ?? string.Empty;

        return ParseAndValidate(raw);
    }

    private IReadOnlyList<A2UiEnvelope> ParseAndValidate(string llmOutput)
    {
        var json = llmOutput.Contains(JsonDelimiter)
            ? llmOutput[(llmOutput.IndexOf(JsonDelimiter) + JsonDelimiter.Length)..].Trim()
            : llmOutput.Trim();

        if (json.StartsWith("```json", StringComparison.OrdinalIgnoreCase))
            json = json[7..json.LastIndexOf("```")].Trim();
        else if (json.StartsWith("```"))
            json = json[3..json.LastIndexOf("```")].Trim();

        validator.ValidateOrThrow(json);

        return JsonSerializer.Deserialize<List<A2UiEnvelope>>(json, s_json)
            ?? throw new InvalidOperationException("LLM returned no parseable A2UI messages.");
    }

}
```

Back to the index: [dotnet-a2ui-endpoint](dotnet-a2ui-endpoint.md)

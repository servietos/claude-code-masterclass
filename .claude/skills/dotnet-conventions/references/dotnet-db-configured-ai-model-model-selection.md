# Model selection: the DB is the source of truth, not config

## Model selection: the DB is the source of truth, not config

The admin maintains multiple `AiModel` rows and flags exactly one `IsDefault = 1`. The service reads
that row per call, with no cached client and no `IOptions<T>`:

```csharp
var model = await db.AiModels.AsNoTracking().SingleOrDefaultAsync(m => m.IsDefault, ct);
if (model is null || string.IsNullOrWhiteSpace(model.ApiKey) || string.IsNullOrWhiteSpace(model.BaseUrl))
    throw new SuggestionUnavailableException(NoDefaultModelDetail);
```

Every field on that row is a per-model setting the request must honour, not a fallback to a global
default: `Provider` (log/telemetry label), `BaseUrl` (see normalisation below), `ApiKey` (bearer
token), `ModelName` (the `model` field in the chat-completions payload), `Temperature`, `MaxTokens`,
`TopP`. Pass the numeric ones straight through:

```csharp
var payload = new ChatCompletionRequest
{
    Model = model.ModelName,
    Messages = [new ChatMessage("system", systemPrompt), new ChatMessage("user", userPrompt)],
    Temperature = model.Temperature,
    MaxTokens = model.MaxTokens,
    TopP = model.TopP
};
```

`MaxTokens`/`TopP` are `int?`/`decimal?` on the DTO with
`[JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]`: an unset admin field must not
serialize as `null` into a provider that rejects the key outright rather than treating it as "use the
provider default".

Back to the index: [dotnet-db-configured-ai-model](dotnet-db-configured-ai-model.md)

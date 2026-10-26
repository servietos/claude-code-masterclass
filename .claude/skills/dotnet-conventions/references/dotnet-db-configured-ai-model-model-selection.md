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

## Variant: the default lives on the agent, models are chosen by capability

When several agents share one catalogue, a single `IsDefault` row stops fitting: a vision agent and
a text agent need different defaults. Move the default from the model to the agent and resolve by
capability:

- Each agent declares its required capabilities in code (`Text`, `Vision`, `Image`), derived from
  the model fields (`SupportsVision`, `TaskType`), never a new flag on the model.
- A model is **eligible** for an agent only when it fulfils **every** required capability and its
  provider has an API key. "At least one" lets a text-only model into a vision agent's picker.
  Apply the same predicate in the UI filter and in the save endpoint's validation.
- Each agent stores one default model or a set of defaults. At run time take the first default that
  has the needed capability and a key, else fall back to the first catalogue model that does, else
  throw.
- When the per-agent defaults come from an upstream service that may not be deployed yet, fall back
  to the agent's pre-existing single model column so the agent list never renders empty.

Verify: a unit test where a Vision+Text agent's eligible list excludes a text-only model, an
embeddings model and a model whose provider has no key; and a resolution test for default hit,
capability fallback and throw.

Back to the index: [dotnet-db-configured-ai-model](dotnet-db-configured-ai-model.md)

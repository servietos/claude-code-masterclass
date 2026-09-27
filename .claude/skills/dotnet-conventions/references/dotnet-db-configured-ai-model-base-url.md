# BaseUrl normalisation

## BaseUrl normalisation

Admins type `BaseUrl` by hand from each provider's docs, so the same tenant legitimately has
`https://api.deepseek.com`, `https://api.deepinfra.com/v1`, and `https://api.deepinfra.com/v1/openai`,
with or without a trailing slash. A naive `$"{baseUrl}/v1/chat/completions"` produces
`https://api.deepinfra.com/v1/v1/chat/completions` for the second provider and
`https://api.deepseek.com/chat/completions` (wrong, missing `/v1`) for the first. Normalise to exactly
one `/v1/chat/completions` by trimming, then only appending `/v1` if it is not already the last
segment:

```csharp
internal static string BuildChatCompletionsUrl(string baseUrl)
{
    var trimmed = baseUrl.Trim().TrimEnd('/');
    if (!trimmed.EndsWith("/v1", StringComparison.OrdinalIgnoreCase))
        trimmed += "/v1";
    return $"{trimmed}/chat/completions";
}
```

This does not fully solve `.../v1/openai` (that provider's own `/v1` alias is a third shape some
providers ship), so treat this as "normalise the two common shapes", not "handles every provider
forever": check the concrete `BaseUrl` values in the `AiModels` table before trusting a new provider
against it, and extend the helper's unit tests rather than special-casing it inline in the call site.

Back to the index: [dotnet-db-configured-ai-model](dotnet-db-configured-ai-model.md)

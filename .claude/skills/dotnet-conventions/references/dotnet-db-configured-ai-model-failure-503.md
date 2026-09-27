# Failure shape: everything collapses to one 503

## Failure shape: everything collapses to one 503

No default model, a missing key, a provider HTTP error, a timeout, and an unparsable completion body
are five different causes that must all surface as the same `503` `ProblemDetails`, with `detail` set
to one complete sentence in the product's own language that the UI prints verbatim (never the
provider's raw error, the API key, or a stack trace):

```csharp
public class SuggestionUnavailableException(string detail) : Exception(detail);

private const string NoDefaultModelDetail =
    "Kein Standard-KI-Modell konfiguriert. Bitte in der Verwaltung ein Modell als Standard festlegen.";

private const string ProviderUnavailableDetail =
    "Der KI-Dienst ist aktuell nicht erreichbar. Bitte versuche es später erneut oder schreibe die Antwort manuell.";
```

Point the "no default model" sentence at the exact admin screen that fixes it: this error is a
configuration state, not a fault, and the recipient is the one person who can resolve it in one click.

Every failure path logs the real detail server-side, then throws the exception carrying only the safe
sentence:

```csharp
catch (HttpRequestException ex)
{
    logger.LogError(ex, "AI suggestion call to {Provider} failed for model {ModelName}", model.Provider, model.Name);
    throw new SuggestionUnavailableException(ProviderUnavailableDetail);
}
```

The controller maps the exception to the response, and nothing else:

```csharp
catch (SuggestionUnavailableException ex)
{
    return Problem(detail: ex.Message, statusCode: StatusCodes.Status503ServiceUnavailable);
}
```

A non-success HTTP status from the provider also logs the response body (for diagnosis) but never
forwards it into `detail`:

```csharp
if (!response.IsSuccessStatusCode)
{
    var errorBody = await response.Content.ReadAsStringAsync(ct);
    logger.LogError(
        "AI provider {Provider} returned {StatusCode} (model {ModelName}) after {ElapsedMs}ms: {Body}",
        model.Provider, (int)response.StatusCode, model.Name, elapsedMs, errorBody);
    throw new SuggestionUnavailableException(ProviderUnavailableDetail);
}
```

Back to the index: [dotnet-db-configured-ai-model](dotnet-db-configured-ai-model.md)

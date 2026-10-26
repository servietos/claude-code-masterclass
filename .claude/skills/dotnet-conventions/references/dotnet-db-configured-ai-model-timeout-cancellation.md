# Timeout and cancellation

## Timeout and cancellation

Layer a fixed request timeout on top of the caller's own cancellation token with a linked CTS, and
distinguish "we timed out" from "the caller cancelled" so only the former gets classified as a
provider failure:

```csharp
private static readonly TimeSpan RequestTimeout = TimeSpan.FromSeconds(30);

using var timeoutCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
timeoutCts.CancelAfter(RequestTimeout);

try
{
    response = await client.SendAsync(request, timeoutCts.Token);
}
catch (OperationCanceledException) when (!ct.IsCancellationRequested)
{
    logger.LogError(
        "AI suggestion call to {Provider} timed out after {Timeout}s for model {ModelName}",
        model.Provider, RequestTimeout.TotalSeconds, model.Name);
    throw new SuggestionUnavailableException(ProviderUnavailableDetail);
}
```

The `when (!ct.IsCancellationRequested)` guard matters: if the *caller's* token fired (the user
navigated away), that is a normal ASP.NET Core request-abort, not a provider outage, so do not classify
it as a 503.

## Slow is not hung: read the usage line first

A reasoning model can take minutes on an ordinary call. Kimi K2.6 on DeepInfra answered a PDF
extraction with 5,136 output tokens after about 5 minutes, and the request was first reported as a
hang. Before calling a provider hung, read the completion's usage log line (prompt and completion
tokens, provider and model): tokens mean it answered slowly, and the fix is a faster model for that
call or a timeout sized to it. No line after the timeout window means it really hung. Also confirm
which model actually served the call: a fallback model can stand in silently for the configured one.

Back to the index: [dotnet-db-configured-ai-model](dotnet-db-configured-ai-model.md)

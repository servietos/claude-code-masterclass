# Anti-patterns

## Anti-patterns

| Anti-pattern | Why it fails | Fix |
| --- | --- | --- |
| Reading provider/key/model from `appsettings.json` | Tenants swap providers and rotate keys via the admin UI, not a redeploy | Read the `IsDefault` `AiModel` row per call |
| `$"{baseUrl}/v1/chat/completions"` with no normalisation | Breaks for any `BaseUrl` that already ends in `/v1` | Trim trailing slash, append `/v1` only if not already present |
| Returning `errorBody`/`ex.Message`/a provider status text in `Problem(detail: ...)` | Leaks provider internals (and risks leaking the key from a request-echo error) to the browser | Log the real detail; throw a canned safe sentence |
| Trusting `ct` alone for the outbound HTTP call | A slow or hanging provider blocks the request indefinitely if the client's own token never fires | Layer `CancellationTokenSource.CreateLinkedTokenSource(ct)` + `CancelAfter(fixedTimeout)` |
| Assuming the model always returns the requested `Betreff: / --- / body` shape | Providers occasionally ignore format instructions or wrap output in code fences | Strip fences, parse defensively, fall back to the caller's subject and the raw text as body |
| Letting the model state a fact (address, price, date) that was not supplied in the prompt | A correct-by-luck hallucination passes review; an incorrect one reaches a customer | Put every fact the model may state in the prompt; require bracketed placeholders otherwise |
| Adding a togglable enrichment as a new intent enum value | Multiplies the enum with every future toggle and intent combination | Model it as an additive instruction (bool) layered on the chosen intent |

Back to the index: [dotnet-db-configured-ai-model](dotnet-db-configured-ai-model.md)

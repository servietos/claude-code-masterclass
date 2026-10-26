# Calling a DB-Configured AI Model for Customer-Facing Copy

Reference for endpoints that call an OpenAI-compatible chat-completions API whose provider, key and
parameters are **rows in the application's own database**, not `appsettings.json`, and that use the
completion to draft text a human will send to a real customer. This differs from `dotnet-maf.md`
(Azure AI Foundry agents): here the model is one of several customer-managed OpenAI-compatible
providers (DeepSeek, DeepInfra, ...) selected at runtime from an `AiModel` table that an admin
maintains through the app's own UI.

The shapes below are extracted from a working implementation; keep the structure and swap the entity
and DTO names for the ones in your project.

The admin maintains multiple `AiModel` rows and flags exactly one `IsDefault = 1`.

| You want to... | Read |
| --- | --- |
| Which provider, key, model name and sampling parameters does a call use, and why is none of it read from appsettings.json? | [dotnet-db-configured-ai-model-model-selection](dotnet-db-configured-ai-model-model-selection.md) |
| The request URL came out as /v1/v1/chat/completions, or lost its /v1 entirely: normalising an admin-typed BaseUrl. A Foundry call fails with "Missing required query parameter: api-version". | [dotnet-db-configured-ai-model-base-url](dotnet-db-configured-ai-model-base-url.md) |
| No default model, a provider HTTP error or an unparsable body: making every cause surface as one safe 503 ProblemDetails. | [dotnet-db-configured-ai-model-failure-503](dotnet-db-configured-ai-model-failure-503.md) |
| The provider hangs forever, or a user navigating away is being logged as an outage: linked CTS with a fixed timeout. A call that looks hung may be a slow reasoning model. | [dotnet-db-configured-ai-model-timeout-cancellation](dotnet-db-configured-ai-model-timeout-cancellation.md) |
| The completion came back in code fences or without the Betreff/--- shape: parsing defensively and truncating the body. A JSON-mode reply came back empty. | [dotnet-db-configured-ai-model-response-parsing](dotnet-db-configured-ai-model-response-parsing.md) |
| The model stated an address, price or date nobody supplied: grounding every hard fact and forcing bracketed placeholders. | [dotnet-db-configured-ai-model-prompt-grounding](dotnet-db-configured-ai-model-prompt-grounding.md) |
| The generated text shipped markdown or dashes, or the model discarded what the operator had already typed in the textarea. | [dotnet-db-configured-ai-model-prompt-style-and-draft](dotnet-db-configured-ai-model-prompt-style-and-draft.md) |
| Should an "also include the offering and pricing" toggle be another intent enum value or a bool layered on the chosen intent? | [dotnet-db-configured-ai-model-additive-toggle](dotnet-db-configured-ai-model-additive-toggle.md) |
| Reviewing an existing implementation: the seven known ways this feature goes wrong, why each fails, and the fix. | [dotnet-db-configured-ai-model-anti-patterns](dotnet-db-configured-ai-model-anti-patterns.md) |

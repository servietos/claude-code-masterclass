# A2UI Catalog and Agent Endpoint

When to use: you are serving the component catalog or implementing the agent endpoint.
Setup and wiring live in [`dotnet-a2ui`](dotnet-a2ui.md); message types in
[`dotnet-a2ui-messages`](dotnet-a2ui-messages.md); SSE in [`dotnet-a2ui-streaming`](dotnet-a2ui-streaming.md).

This topic covers the whole server side of an A2UI endpoint: the catalog, the agent service, the
system prompt it sends, and the query/action controller.

| You want to... | Read |
| --- | --- |
| How do I serve the component catalog to the client renderer, embedded in the assembly or proxied from a2ui.org? | [dotnet-a2ui-endpoint-catalog](dotnet-a2ui-endpoint-catalog.md) |
| How does the agent service call the chat-completions endpoint and turn the raw LLM text into typed A2UI envelopes? | [dotnet-a2ui-endpoint-agent-service](dotnet-a2ui-endpoint-agent-service.md) |
| What must the system prompt tell the LLM: the v0.9 message rules, the delimiter contract and the full reservation-form example? | [dotnet-a2ui-endpoint-system-prompt](dotnet-a2ui-endpoint-system-prompt.md) |
| How do the /query and /action endpoints look, and how does a client action get mapped back to a natural-language query? | [dotnet-a2ui-endpoint-action-controller](dotnet-a2ui-endpoint-action-controller.md) |

Keep `MapActionToQuery` purely declarative: each arm produces a natural-language query and nothing else.

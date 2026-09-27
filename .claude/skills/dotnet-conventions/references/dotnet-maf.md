# .NET — Microsoft Agent Framework (MAF) via Azure AI Foundry SDK

Reference for calling MAF hosted agents and prompt-based agents from a .NET ASP.NET Core application using the Azure AI Foundry SDK. Extracted from a working production .NET 10 API. All patterns are general — no project-specific names.

| You want to... | Read |
| --- | --- |
| Know which packages, which conflict, and what goes in appsettings. | [dotnet-maf-setup](dotnet-maf-setup.md) |
| Register more than one agent in Program.cs and inject its config into a service. | [dotnet-maf-di](dotnet-maf-di.md) |
| Make one call to a hosted Foundry agent and read its text back. | [dotnet-maf-call-agent](dotnet-maf-call-agent.md) |
| Keep context across turns, stateful with ProjectConversation or stateless via PreviousResponseId. | [dotnet-maf-multi-turn](dotnet-maf-multi-turn.md) |
| Route to a local agent server when Foundry is not deployed, and skip the call safely. | [dotnet-maf-fallbacks](dotnet-maf-fallbacks.md) |
| Pull the source URLs a web-search agent annotated onto its response. | [dotnet-maf-citations](dotnet-maf-citations.md) |
| Diagnose AmbiguousMatchException, a 401, an empty GetOutputText(), a hub-endpoint throw, or OPENAI001. | [dotnet-maf-gotchas](dotnet-maf-gotchas.md) |

Do NOT install `Azure.AI.Projects.OpenAI` (old preview) alongside `Azure.AI.Extensions.OpenAI` — they define conflicting types.

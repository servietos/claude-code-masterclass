# MAF: calling a hosted prompt-based agent

## Calling a Hosted (Prompt-Based) Foundry Agent

A hosted agent is deployed and named in the Azure AI Foundry portal. Call it with `ProjectResponsesClient`:

```csharp
using Azure.AI.Extensions.OpenAI;
using Azure.AI.Projects;
using Azure.Identity;

var projectClient = new AIProjectClient(
    new Uri(_config.ProjectEndpoint),
    new DefaultAzureCredential());

var responsesClient = projectClient.ProjectOpenAIClient
    .GetProjectResponsesClientForAgent(_config.AgentName);

var result = await responsesClient.CreateResponseAsync(userInput);
var outputText = result.Value.GetOutputText();
```

- `GetProjectResponsesClientForAgent(agentName)` looks up the agent by the name registered in Foundry.
- `GetOutputText()` is a convenience extension that concatenates all text output items from the response.
- Use `DefaultAzureCredential` for development; `ManagedIdentityCredential` for production App Service to avoid credential-chain latency.
- `#pragma warning disable OPENAI001` is required for multi-turn `ProjectConversation` types (marked experimental in the GA package).

Back to the index: [dotnet-maf](dotnet-maf.md)

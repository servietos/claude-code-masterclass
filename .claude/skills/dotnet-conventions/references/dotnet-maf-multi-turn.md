# MAF: multi-turn conversations

## Multi-Turn Conversation

For stateful multi-turn conversations, use `ProjectConversation`:

```csharp
#pragma warning disable OPENAI001

var projectClient = new AIProjectClient(new Uri(_config.ProjectEndpoint), new DefaultAzureCredential());

var conversation = projectClient.ProjectOpenAIClient
    .GetProjectConversationsClient()
    .CreateProjectConversation();

var responsesClient = projectClient.ProjectOpenAIClient
    .GetProjectResponsesClientForAgent(
        defaultAgent: _config.AgentName,
        defaultConversationId: conversation.Id);

var response1 = await responsesClient.CreateResponseAsync("First question");
var response2 = await responsesClient.CreateResponseAsync("Follow-up question");

await projectClient.ProjectOpenAIClient
    .GetConversationClient()
    .DeleteConversationAsync(conversation.Id);
```

Stateless alternative — chain via `PreviousResponseId`:

```csharp
var r1 = await responsesClient.CreateResponseAsync("First question");
var r2 = await responsesClient.CreateResponseAsync(
    new CreateResponseOptions
    {
        PreviousResponseId = r1.Value.Id,
        InputItems = { ResponseItem.CreateUserMessageItem("Follow-up") }
    });
```

Back to the index: [dotnet-maf](dotnet-maf.md)

# MAF: local agent server fallback and the unconfigured guard

## Local Development Fallback

When `LocalAgentUrl` is set, POST to the local agent server instead of calling Foundry:

```csharp
private async Task<string> CallAgentAsync(string input)
{
    if (!string.IsNullOrWhiteSpace(_config.LocalAgentUrl))
    {
        using var request = new HttpRequestMessage(
            HttpMethod.Post,
            $"{_config.LocalAgentUrl.TrimEnd('/')}/responses")
        {
            Content = JsonContent.Create(new { model = _config.AgentName, input, stream = false })
        };
        request.Headers.Accept.ParseAdd("text/event-stream");

        using var response = await _httpClient.SendAsync(
            request, HttpCompletionOption.ResponseHeadersRead);
        response.EnsureSuccessStatusCode();
        return await ReadSseResponseAsync(response.Content);
    }

    var projectClient = new AIProjectClient(
        new Uri(_config.ProjectEndpoint), new DefaultAzureCredential());

    var responsesClient = projectClient.ProjectOpenAIClient
        .GetProjectResponsesClientForAgent(_config.AgentName);

    var result = await responsesClient.CreateResponseAsync(input);
    return result.Value.GetOutputText();
}
```

- The local agent server (Python `ResponsesHostServer`) sends SSE.
- Read `response.output_text.delta` events for streaming text.
- Read `response.workflow_output` for final structured output from a WorkflowBuilder agent.

## Guarding Against Unconfigured Agents

Always guard before calling — Foundry config may be absent in environments where the agent is not deployed:

```csharp
private bool IsConfigured() =>
    !string.IsNullOrWhiteSpace(_config.AgentName)
    && (!string.IsNullOrWhiteSpace(_config.LocalAgentUrl)
        || !string.IsNullOrWhiteSpace(_config.ProjectEndpoint));

public async Task<string?> RunAsync(string input)
{
    if (!IsConfigured())
    {
        logger.LogWarning("Skipping agent call — Foundry is not configured.");
        return null;
    }
    // production path follows
}
```

Back to the index: [dotnet-maf](dotnet-maf.md)

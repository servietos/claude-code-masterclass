# MAF: DI registration of named agent options

## DI Registration (Program.cs)

Register named options for each agent; share the project endpoint via `PostConfigure`:

```csharp
var sharedEndpoint = builder.Configuration["Foundry:ProjectEndpoint"] ?? "";

builder.Services.Configure<FoundryAgentConfig>(
    "ResearchAgent",
    builder.Configuration.GetSection("Foundry:Agents:ResearchAgent"));

builder.Services.Configure<FoundryAgentConfig>(
    "ContentAgent",
    builder.Configuration.GetSection("Foundry:Agents:ContentAgent"));

builder.Services.PostConfigure<FoundryAgentConfig>("ResearchAgent", cfg => cfg.ProjectEndpoint = sharedEndpoint);
builder.Services.PostConfigure<FoundryAgentConfig>("ContentAgent", cfg => cfg.ProjectEndpoint = sharedEndpoint);
```

Inject in services with `IOptionsSnapshot<FoundryAgentConfig>` (scoped):

```csharp
public class ResearchService(IOptionsSnapshot<FoundryAgentConfig> agentOptions)
{
    private readonly FoundryAgentConfig _config = agentOptions.Get("ResearchAgent");
}
```

Back to the index: [dotnet-maf](dotnet-maf.md)

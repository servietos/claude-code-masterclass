# MAF: NuGet packages and Foundry configuration

## NuGet Packages

```xml
<PackageReference Include="Azure.AI.Projects" Version="2.0.1" />
<PackageReference Include="Azure.AI.Extensions.OpenAI" Version="2.0.0" />
<PackageReference Include="Azure.Identity" Version="1.21.0" />
```

- Do NOT install `Azure.AI.Projects.OpenAI` (old preview) alongside `Azure.AI.Extensions.OpenAI` — they define conflicting types.
- `Azure.AI.Projects.Agents` (for CRUD on agent definitions) is separate from `Azure.AI.Extensions.OpenAI` (for running conversations).
- The old `Azure.AI.Agents.Persistent` (thread/run pattern) is deprecated and retires March 2027 — do not use for new code.

## Configuration

Define one typed options class per agent:

```csharp
public class FoundryAgentConfig
{
    public string ProjectEndpoint { get; set; } = string.Empty;

    [Required]
    public string AgentName { get; set; } = string.Empty;

    public string? LocalAgentUrl { get; set; }
}
```

`appsettings.json` structure — shared endpoint, per-agent names:

```json
{
  "Foundry": {
    "ProjectEndpoint": "https://<resource>.services.ai.azure.com/api/projects/<project>",
    "Agents": {
      "ResearchAgent": {
        "AgentName": "social-profiler"
      },
      "ContentAgent": {
        "AgentName": "content-creator-team",
        "LocalAgentUrl": "http://localhost:8088"
      }
    }
  }
}
```

- The project endpoint format is `https://<resource>.services.ai.azure.com/api/projects/<project>` — hub-based endpoints (`InferenceEndpoint=...`) are incompatible with SDK 2.x.
- Use `LocalAgentUrl` to route to a locally running agent server during development without changing production config.

Back to the index: [dotnet-maf](dotnet-maf.md)

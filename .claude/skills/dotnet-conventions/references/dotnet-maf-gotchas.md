# MAF: symptoms, causes and fixes

## Gotchas

| Symptom | Cause | Fix |
| --- | --- | --- |
| `AmbiguousMatchException` or type conflicts | Both `Azure.AI.Projects.OpenAI` (old) and `Azure.AI.Extensions.OpenAI` (new) installed | Remove `Azure.AI.Projects.OpenAI` |
| `401` from Foundry even with valid identity | Caller lacks Foundry User RBAC role | Assign `Azure AI User` at the project scope |
| `GetOutputText()` returns empty string | Agent produced structured output with no text item | Check `OutputItems` directly or ensure the agent instructions produce text output |
| `CreateResponseAsync` throws on a hub-based endpoint | Old connection string format; SDK 2.x requires Foundry project endpoint | Update endpoint to `https://<resource>.services.ai.azure.com/api/projects/<project>` |
| `OPENAI001` compile warning | `ProjectConversation` is marked experimental in the GA package | Add `#pragma warning disable OPENAI001` above the usage site |

Back to the index: [dotnet-maf](dotnet-maf.md)

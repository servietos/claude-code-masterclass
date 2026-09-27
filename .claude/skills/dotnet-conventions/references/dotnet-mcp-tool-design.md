# .NET MCP Tools: designing the surface a model calls

What the model sees and chooses from: parameter shape, descriptions, return payloads, tool naming,
and the multi-call patterns. Building and hosting the server is [dotnet-mcp](dotnet-mcp.md); auth is
[dotnet-mcp-auth](dotnet-mcp-auth.md); proving it works is [dotnet-mcp-verify](dotnet-mcp-verify.md).

| You want to... | Read |
| --- | --- |
| Designing a tool argument: should it take listId or the list name, and where does name resolution live? | [keys](dotnet-mcp-tool-design-natural-key.md) |
| The client lists the tool but answers a call with "Tool not found", or you are adding a ui:// form to a write. | [ui://](dotnet-mcp-tool-design-ui-apps.md) |
| A write needs human confirmation but the client is Claude Desktop or a phone with no UI: what shape does the preview take? | [preview](dotnet-mcp-tool-design-preview-no-ui.md) |
| The confirmed write saved a different amount than the proposal showed, or the caller's arguments can contradict each other. | [values](dotnet-mcp-tool-design-write-values.md) |
| Exposing something a controller already does: where do the validation, the guards and the read/write split live? | [shared](dotnet-mcp-tool-design-shared-implementation.md) |
| The model keeps calling the neighbouring tool, or two tools both say "returns totals" and it guesses. | [wording](dotnet-mcp-tool-design-descriptions.md) |
| What type should a tool return, and why does calling GetPeriodSummary by its C# method name fail at the JSON-RPC layer? | [wire](dotnet-mcp-tool-design-wire-shape.md) |

Default everywhere: Use DTOs whenever the response has more than one field.

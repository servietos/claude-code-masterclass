# MCP Apps (ui://) tools are listed but not model-callable

## MCP Apps (`ui://`) tools are not model-callable on every client

A tool that links an interactive form via MCP Apps carries `_meta.ui.resourceUri`:

```csharp
[McpServerTool]
[McpMeta("ui", JsonValue = """{"resourceUri":"ui://myapp/some-form"}""")]
public async Task<string> OpenSomeDraft(...) { ... }
```

**Some clients list such a tool but refuse to let the model invoke it.** claude.ai registers it as an "Interactive UI tool" and answers a direct call with:

```
Tool '<Server>:open_some_draft' not found.
```

while every plain tool on the same server works normally. The tool name showing up in the client's tool list is therefore not evidence that the model can call it.

Rules:

- **Never make a `ui://`-linked tool the only entrance to a capability.** Ship a plain, model-callable tool that completes the job in one call; treat the form as an optional nicety for clients that render it. Otherwise the feature silently does not exist for half your clients.
- **Once the plain path works everywhere, delete the form rather than keeping it as that nicety.** Two entrances to one write mean two `[Description]` contracts telling the model different things, two test surfaces, and docs that drift apart while both look maintained. A form that no client in actual use renders is not a fallback, it is a second specification nobody reads. Removing it is a deletion of the tool, its `ui://` resource and its tests in one pass.
- The plain tool must carry the **full domain shape**, not the demo shape the form happened to collect. A form-backed `save_*` written for a walkthrough tends to hardcode things (a zero VAT rate, a default account, no document reference) that make it wrong for real data.
- "Listed but not found on invoke" is a client-side client-type restriction, never a server fault. Prove the server first — a direct `tools/call` over curl (see *Verifying an HTTP MCP server*) will return the tool's payload happily.

## The typed package and its traps (ModelContextProtocol.Extensions.Apps 2.3.0, read 2026-10-24)

`ModelContextProtocol.Extensions.Apps` replaces the hand-written `[McpMeta("ui", ...)]`: `[McpAppUi(ResourceUri = "ui://app/view.html", Visibility = [...])]` on the tool, `.WithMcpApps()` on the builder, `McpApps.HtmlMimeType` (`text/html;profile=mcp-app`) on the resource. Every type is `[Experimental("MCPEXP003")]`. Read from the SDK source, four traps:

- **Two typed classes serialize names the spec does not use.** `McpUiResourceCsp.BaseUris` writes `baseUris` (spec: `baseUriDomains`) and `McpUiResourcePermissions` writes an `allow` array (spec: keyed `camera`, `microphone`, `geolocation`, `clipboardWrite` objects). Write those two as raw JSON; `connectDomains` and `resourceDomains` are safe typed.
- **`[McpMeta]` on a resource reaches `resources/list` only** (csharp-sdk #1228). For `resources/read`, return a `ReadResourceResult` whose content carries `Meta`; hosts check the UI metadata on both.
- **`McpApps.GetUiCapability` returns null on a stateless server** for a client still on the `initialize` handshake, because each request gets a fresh server without capabilities. Attach the tool's `_meta.ui` unconditionally and always return text `content` that answers on its own; the spec requires that fallback anyway.
- **`visibility: ["app"]` hides a tool from the model only.** Anyone can still `tools/call` it on an anonymous endpoint, so validation and rate limits stay server-side.

Proves it still holds: `resources/read` on the `ui://` URI over curl shows `_meta.ui` on the content, and a grep of the response for `baseUris` or `"allow"` prints nothing.

Back to the index: [dotnet-mcp-tool-design](dotnet-mcp-tool-design.md)

# .NET MCP Server Reference

General-purpose reference for building a .NET MCP (Model Context Protocol) server using `ModelContextProtocol` and `ModelContextProtocol.AspNetCore`. Use this file when creating or extending any .NET MCP server project.

## NuGet Packages

Core MCP packages:

```xml
<PackageReference Include="ModelContextProtocol" Version="1.4.0" />
<PackageReference Include="ModelContextProtocol.AspNetCore" Version="1.4.0" />
```

Optional — add when the server needs a database:

```xml
<PackageReference Include="Microsoft.EntityFrameworkCore" Version="10.0.x" />
<PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="10.0.x" />
<PackageReference Include="Microsoft.EntityFrameworkCore.Design" Version="10.0.x" />
```

## Program.cs — HTTP Transport

```csharp
using ModelContextProtocol.Server;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddDbContext<MyDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("MyDb")));
builder.Services.AddScoped<IMyService, MyService>();

builder.Services.AddMcpServer()
    .WithHttpTransport()
    .WithToolsFromAssembly();

var app = builder.Build();

app.MapMcp();

app.Run();
```

- `AddMcpServer()` registers MCP protocol infrastructure.
- `.WithHttpTransport()` uses ASP.NET Core Kestrel as the transport — no stdio.
- `.WithToolsFromAssembly()` auto-discovers every class marked `[McpServerToolType]`.
- `app.MapMcp()` mounts the MCP routes onto the HTTP pipeline at `/mcp`.

## Tool Class Structure

```csharp
using System.ComponentModel;
using ModelContextProtocol.Server;

[McpServerToolType]
internal class MyTools
{
    private readonly IMyService _service;
    private readonly ILogger<MyTools> _logger;

    public MyTools(IMyService service, ILogger<MyTools> logger)
    {
        _service = service;
        _logger = logger;
    }

    [McpServerTool]
    [Description("Short description of what this tool does")]
    public async Task<string> DoSomething(
        [Description("What this parameter controls")] string input,
        [Description("Optional flag with a default")] bool flag = false)
    {
        var result = await _service.ProcessAsync(input, flag);
        return result;
    }
}
```

- One `[McpServerToolType]` per class; one `[McpServerTool]` per method.
- Every parameter must have a `[Description("...")]` attribute — MCP clients use this for introspection.
- Return `string` for simple text results; return a typed DTO for structured data.
- Optional parameters use default values (`= false`, `= 8`, etc.).
- Nullable parameters (`string?`) accept absent values from the MCP client.
- All tools should be `async Task<T>` unless computation is truly synchronous.

## Writing Tool Descriptions for LLM Disambiguation

Once a server has more than a couple of tools that touch related data (e.g. an aggregate total, a per-entity breakdown, and a derived/net figure), a client LLM will regularly pick the wrong one unless each `[Description]` earns its keep. A description that only states what the tool does is not enough once a near-neighbor tool exists — it must also say what it is *not*, so the model can rule out the alternative on the same pass:

- **State the disambiguation explicitly, by tool name.** "Returns the single aggregate total (not per-customer) — for a per-entity breakdown use `GetXByCategory` instead" beats two descriptions that both independently say "returns totals" and leave the model to guess which one is the aggregate.
- **Include the natural user question verbatim**, not just the technical operation. Users ask "how much was my revenue in 2022," not "aggregate income query" — echo the former in the description so embedding/keyword matching on the tool list actually surfaces it.
- **Name domain near-synonyms that map to different fields.** Many business domains have two or more terms that sound interchangeable to a general model but are computed differently server-side (e.g. gross turnover vs. net income; a domain's internal jargon vs. the everyday word a user would type, possibly in a different language than the codebase). If the underlying query already returns both, say so explicitly (`GrossX is the turnover figure, NetX is the income figure`) instead of leaving the model to infer which field answers which phrasing.
- **Verify the semantic claim against the query/service implementation before writing it** — don't guess which field maps to which business term; open the underlying `*Query`/`*Service` method and confirm what it actually aggregates. A confidently wrong disambiguation is worse than a vague one.
- **Prefer fixing descriptions over adding a new tool.** A new tool is only justified when the underlying data genuinely isn't computable from an existing tool's return shape — if two "different" questions already resolve to the same query with different wording, that's a description gap, not a coverage gap.

## Returning Structured Data

```csharp
public class ItemCollection
{
    public List<Item> Items { get; set; } = [];
}

public class Item
{
    [JsonPropertyName("id")]
    public int Id { get; set; }

    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
}

[McpServerTool]
[Description("Returns all items")]
public async Task<ItemCollection> ListItems()
{
    var items = await _service.GetAllAsync();
    return new ItemCollection { Items = items };
}
```

MCP tools can return plain strings or any JSON-serializable type. Use DTOs whenever the response has more than one field.

## Securing the /mcp endpoint (dual auth)

`app.MapMcp("/mcp")` returns an endpoint you gate explicitly — it sits **outside** `MapControllers()`, so a blanket `MapControllers().RequireAuthorization()` does **not** cover it. To accept both an Entra ID JWT (for OAuth clients like Claude.ai) **and** a static API key (for header-capable clients like Claude Desktop/Code via `mcp-remote`), combine two schemes under one policy:

```csharp
var mcp = app.MapMcp("/mcp");
if (cfg.App.AuthEnabled) mcp.RequireAuthorization("Mcp");   // leave open in dev
```

```csharp
// JWT: accept both the API's own audience and the MCP resource URI
builder.Services.Configure<JwtBearerOptions>(JwtBearerDefaults.AuthenticationScheme, o =>
{
    o.TokenValidationParameters.ValidAudiences = [ $"api://{cfg.EntraId.ClientId}", cfg.Mcp.ResourceUri ];
    o.Events = new JwtBearerEvents { OnChallenge = ctx => { /* emit WWW-Authenticate below */ } };
});
// API key: a custom handler that DEFERS (NoResult) when its header is absent, so JWT can still run
builder.Services.AddAuthentication().AddScheme<AuthenticationSchemeOptions, McpApiKeyAuthHandler>("ApiKey", _ => { });
builder.Services.AddAuthorization(o => o.AddPolicy("Mcp", p =>
    p.AddAuthenticationSchemes(JwtBearerDefaults.AuthenticationScheme, "ApiKey").RequireAuthenticatedUser()));
```

- The key handler **must return `AuthenticateResult.NoResult()` when its header is missing** (not `Fail()`), or the two schemes can't coexist — `Fail()` short-circuits the whole policy. Return `Fail()` only when a key is present but wrong.
- Expose an **anonymous** RFC 9728 discovery endpoint so OAuth clients can find the auth server:
  `GET /.well-known/oauth-protected-resource` → `{ resource, authorization_servers, scopes_supported, bearer_methods_supported: ["header"] }`.
- On a 401 for `/mcp`, emit `WWW-Authenticate: Bearer resource_metadata="{scheme}://{host}/.well-known/oauth-protected-resource", error="invalid_token"` so clients auto-discover it.
- For the OAuth `resource`/scope byte-match gotcha (AADSTS9010010), custom-domain requirement, and which clients support header auth vs. OAuth-only, see the `mcp-keybased-auth` / `mcp-claude` skills — those own the client side.

## Verifying an HTTP MCP server (dev)

The transport is **streamable HTTP** — a session handshake, and responses come back as SSE (`data: {json}` lines), not plain JSON. Verify by hand with `curl` (more reliable than the Inspector for a quick check):

```bash
MCP=https://127.0.0.1:5001/mcp
# 1. initialize — grab the session id from the RESPONSE HEADER
SID=$(curl -sk -D - -o /dev/null -X POST $MCP \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"c","version":"1"}}}' \
  | grep -i "mcp-session-id" | tr -d '\r' | awk '{print $2}')
H=(-H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -H "Mcp-Session-Id: $SID")
# 2. required notification, THEN list/call (every call carries the session header)
curl -sk -o /dev/null -X POST $MCP "${H[@]}" -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'
curl -sk -X POST $MCP "${H[@]}" -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'          | sed -n 's/^data: //p'
curl -sk -X POST $MCP "${H[@]}" -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"my_tool","arguments":{}}}' | sed -n 's/^data: //p'
```

Gotchas that waste time:

- **`/mcp` may be HTTPS-only.** If `UseHttpsRedirection()` is active (often when a `Testing`/prod flag is set even in the dev profile), `http://…:5000/mcp` returns a **307 redirect** to `https://…:5001/mcp`. Hit the HTTPS URL directly with `-k` (self-signed dev cert).
- **The MCP Inspector's node `fetch` fails on that redirect** (`Failed to connect: fetch failed`) and rejects the self-signed cert. Use the HTTPS URL and `NODE_TLS_REJECT_UNAUTHORIZED=0`, or just use the `curl` handshake above.
- A missing `Accept: application/json, text/event-stream` header, or forgetting the `Mcp-Session-Id` on follow-ups, yields opaque 400/406s — both are mandatory.

## Kestrel Port Configuration

```json
{
  "Kestrel": {
    "Endpoints": {
      "Http": { "Url": "http://*:47000" }
    }
  }
}
```

Choose an unused port (e.g., 47001, 47002, 3001) that does not conflict with other services running on the host.

## Stdio Transport

Use a console host when targeting Claude Desktop or GitHub Copilot instead of an HTTP client:

```csharp
var builder = Host.CreateApplicationBuilder(args);

builder.Services.AddMcpServer()
    .WithStdioServerTransport()
    .WithToolsFromAssembly();

builder.Services.AddScoped<IMyService, MyService>();

await builder.Build().RunAsync();
```

Client config in `.vscode/mcp.json` or `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "dotnet",
      "args": ["run", "--project", "src/my-mcp-server"]
    }
  }
}
```

## MCP Client Configuration for HTTP Transport

```json
{
  "mcpServers": {
    "my-server": {
      "url": "http://localhost:47000/mcp"
    }
  }
}
```

The `/mcp` path is the default mount point set by `app.MapMcp()`.

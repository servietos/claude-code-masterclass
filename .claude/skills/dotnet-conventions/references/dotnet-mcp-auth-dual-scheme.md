# Dual auth on /mcp: Entra JWT plus API key

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

Back to the index: [dotnet-mcp-auth](dotnet-mcp-auth.md)

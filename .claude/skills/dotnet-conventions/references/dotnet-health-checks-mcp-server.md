# Health on an Auth-Gated MCP Server

## Adding `/health` to an MCP server (or anything auth-gated)

An MCP server has no controllers to hang a health route off: the whole surface is one transport
endpoint carrying the auth policy. Map health as its own endpoint beside it:

```csharp
builder.Services.AddHealthChecks();

app.UseAuthentication();
app.UseAuthorization();

app.MapMcp("/mcp").RequireAuthorization("Mcp");
app.MapHealthChecks("/health").AllowAnonymous();
```

**`AllowAnonymous()` is endpoint metadata, and only the authorization middleware reads it.** It
correctly bypasses `RequireAuthorization("...")`, a `FallbackPolicy`, and an
`AuthenticationHandler` such as an API-key scheme. It does **nothing** against a hand-rolled
`app.Use(async (ctx, next) => ...)` that checks a header on every request: that middleware runs
before routing has selected an endpoint and never sees the metadata. Read the pipeline before
claiming the endpoint is reachable unauthenticated, and prove it with an unauthenticated request
rather than by reading the `.AllowAnonymous()` call.

Verify: `curl -i http://127.0.0.1:<port>/health` with no credentials returns `200 Healthy`, while
the same call to the MCP route returns `401`.

Back to the index: [dotnet-health-checks](dotnet-health-checks.md)

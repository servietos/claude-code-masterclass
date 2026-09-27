# MCP behind a reverse proxy: X-Forwarded-Proto

## Behind a reverse proxy: honour X-Forwarded-Proto or OAuth discovery breaks

An MCP server's 401 challenge carries the absolute URL of its protected-resource
metadata, and ASP.NET Core builds that from **its own** scheme. Kestrel behind Caddy /
nginx / App Gateway sees plain HTTP, so it advertises
`resource_metadata="http://host/.well-known/oauth-protected-resource"` while the site
is https. Clients follow that URL, discovery dead-ends, and Claude reports *"Automatic
client registration isn't supported"* — an auth-shaped message with a transport cause.

```csharp
var forwarded = new ForwardedHeadersOptions
{
    ForwardedHeaders = ForwardedHeaders.XForwardedProto | ForwardedHeaders.XForwardedHost | ForwardedHeaders.XForwardedFor
};
forwarded.KnownNetworks.Clear();   // the proxy is the only hop in front of Kestrel
forwarded.KnownProxies.Clear();
app.UseForwardedHeaders(forwarded);   // before UseRouting and any auth middleware
```

Check it from outside, not from the container:

```bash
curl -sD - -o /dev/null -X POST https://<host>/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"p","version":"1"}}}' \
  | grep -i www-authenticate
```

Optional — add when the server needs a database:

```xml
<PackageReference Include="Microsoft.EntityFrameworkCore" Version="10.0.x" />
<PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="10.0.x" />
<PackageReference Include="Microsoft.EntityFrameworkCore.Design" Version="10.0.x" />
```

Back to the index: [dotnet-mcp-auth](dotnet-mcp-auth.md)

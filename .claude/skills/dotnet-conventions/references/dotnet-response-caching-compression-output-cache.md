# Output caching one anonymous GET, and evicting it

## 3. Output caching

Scope it to the one anonymous `GET`. Never a base policy: that would put admin and MCP responses in
the same store.

```csharp
builder.Services.AddOutputCache(options =>
    options.AddPolicy(ContentCachePolicy, policy => policy
        .Expire(TimeSpan.FromMinutes(5))
        .Tag(ContentCacheTag)));
```

```csharp
[HttpGet]
[OutputCache(PolicyName = PerformanceSetup.ContentCachePolicy)]
public async Task<IActionResult> Get() { ... }
```

The default policy, which a named policy inherits unless excluded, already refuses to cache non-GET,
non-200, cookie-setting, and **authenticated** responses (an `Authorization` header alone is enough).
That is what makes a single named policy safe next to admin endpoints.

The cache key is scheme + host + port + path + query, so a multi-slot deployment that embeds its own
base URL in the payload varies correctly with no extra configuration.

### Evict on every write, not per controller

Wiring `EvictByTagAsync` into each writing action means every future writer must remember. One
pipeline-wide filter cannot be forgotten:

```csharp
public static IApplicationBuilder UseContentCacheEviction(this IApplicationBuilder app)
{
    return app.Use(async (context, next) =>
    {
        await next(context);

        var method = context.Request.Method;
        if (HttpMethods.IsGet(method) || HttpMethods.IsHead(method) || HttpMethods.IsOptions(method))
            return;
        if (context.Response.StatusCode >= StatusCodes.Status400BadRequest)
            return;

        await context.RequestServices
            .GetRequiredService<IOutputCacheStore>()
            .EvictByTagAsync(ContentCacheTag, CancellationToken.None);
    });
}
```

Evicting a tag with no entries is cheap, so the over-broad match (a login POST also evicts) costs
nothing. Keep a modest absolute expiry anyway: it bounds staleness from writes that bypass the API,
such as a SQL delta applied straight to the database.

Back to the index: [dotnet-response-caching-compression](dotnet-response-caching-compression.md)

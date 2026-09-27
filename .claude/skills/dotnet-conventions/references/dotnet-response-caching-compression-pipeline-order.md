# Middleware order: compression outer, output cache inner

## 4. Pipeline order, and the one that is a trap

```csharp
app.UseResponseCompression();   // OUTER
app.UseCors();
app.UseAuthentication();
app.UseAuthorization();
app.UseOutputCache();           // INNER, after CORS/routing/auth
app.UseContentCacheEviction();
app.MapControllers();
```

**Compression must be registered before (outer of) output caching.** With caching outer, a cache hit
short-circuits and never reaches the compression middleware, so every hit ships uncompressed and the
two features silently cancel out. Compression outer means the cache stores uncompressed bytes and the
hit is compressed on its way out, which also keeps the cache from needing to vary by `Accept-Encoding`.

Note this is the opposite of the ordering shown in the docs for the older *response* caching
middleware. `UseOutputCache` must still come after `UseCors`, after routing, and after
`UseAuthentication`/`UseAuthorization`.

Back to the index: [dotnet-response-caching-compression](dotnet-response-caching-compression.md)

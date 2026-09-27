# Wiring Brotli and Gzip response compression

## 2. Compression

```csharp
builder.Services.AddResponseCompression(options =>
{
    options.EnableForHttps = true;
    options.Providers.Add<BrotliCompressionProvider>();
    options.Providers.Add<GzipCompressionProvider>();
    options.MimeTypes = ResponseCompressionDefaults.MimeTypes
        .Where(t => !t.StartsWith("image/", StringComparison.OrdinalIgnoreCase))
        .ToArray();
});
builder.Services.Configure<BrotliCompressionProviderOptions>(o => o.Level = CompressionLevel.Optimal);
builder.Services.Configure<GzipCompressionProviderOptions>(o => o.Level = CompressionLevel.Optimal);
```

**`EnableForHttps` is off by default and that silently disables compression in production.** Behind a
reverse proxy with `ASPNETCORE_FORWARDEDHEADERS_ENABLED`, `Request.IsHttps` is true, so the default
skips compression on exactly the deployment you care about while local HTTP looks fine. Turn it on
where the payload is public content with no per-user secret; the BREACH concern needs a secret in the
response reflecting attacker-controlled input.

**Pick the level from a measurement, not from the name.** Measured on 108,890 bytes of JSON:

| `CompressionLevel` | bytes | added latency |
| --- | --- | --- |
| `Fastest` (the provider default) | 34,964 | ~1 ms |
| `Optimal` | 25,297 | ~2 ms |
| `SmallestSize` | 21,304 | **~70 ms** |

`Optimal` is the sweet spot. `SmallestSize` costs 35x the CPU for a further 15%, on every response,
including cache hits.

**Exclude `image/*`.** Already-compressed WebP/JPEG/PNG gain nothing and pay the CPU.

Back to the index: [dotnet-response-caching-compression](dotnet-response-caching-compression.md)

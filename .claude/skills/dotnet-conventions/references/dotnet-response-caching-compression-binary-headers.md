# Cache-Control and ETag for binary endpoints

## 5. Binary endpoints: version decides the header

| URL shape | Header | Why |
| --- | --- | --- |
| Versioned (`/photo?v=<length>`) | `public, max-age=31536000, immutable` | a new image is a new URL |
| Unversioned (`/flags/{country}/image`) | `public, max-age=3600` + strong `ETag` | `immutable` would pin a stale image forever after an admin replaces one |

```csharp
var bytes = Convert.FromBase64String(row.ImageData);
var tag = new EntityTagHeaderValue($"\"{Convert.ToHexString(SHA256.HashData(bytes))[..32]}\"");
Response.Headers.CacheControl = "public, max-age=3600";
return File(bytes, "image/webp", null, tag);
```

Passing the tag to `File(...)` gets conditional-request handling (`If-None-Match` → 304) for free. The
four-argument overload's third parameter is `DateTimeOffset? lastModified`, so a literal `null` there
is unambiguous.

Back to the index: [dotnet-response-caching-compression](dotnet-response-caching-compression.md)

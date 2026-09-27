# dotnet-response-caching-compression

Make an ASP.NET Core JSON endpoint fast without changing a byte of its contract: stop reading columns
the response never emits, compress what is left, cache the assembled result, and prove all three.

Use when a read endpoint is slow and the payload is small; when a page waits on one aggregate
`GET`; when `AddResponseCompression` / `AddOutputCache` need wiring; when an image endpoint is
re-downloaded on every page view.

**Measure before assuming the order.**

| You want to... | Read |
| --- | --- |
| A read endpoint is slow and you do not yet know why: which of the four fixes pays, and in what order. | [dotnet-response-caching-compression-triage](dotnet-response-caching-compression-triage.md) |
| The query materialises MBs but the JSON emits KBs: how to Select only what ships, including blob lengths. | [dotnet-response-caching-compression-projection](dotnet-response-caching-compression-projection.md) |
| Wiring AddResponseCompression: EnableForHttps, which CompressionLevel, and why image/* is excluded. | [dotnet-response-caching-compression-brotli-gzip](dotnet-response-caching-compression-brotli-gzip.md) |
| Adding AddOutputCache to a single public GET without exposing admin responses, and evicting on every write. | [dotnet-response-caching-compression-output-cache](dotnet-response-caching-compression-output-cache.md) |
| Compression and output caching are both on but cache hits ship uncompressed: the middleware ordering trap. | [dotnet-response-caching-compression-pipeline-order](dotnet-response-caching-compression-pipeline-order.md) |
| An image or file endpoint is re-downloaded every page view: immutable versus max-age plus a strong ETag. | [dotnet-response-caching-compression-binary-headers](dotnet-response-caching-compression-binary-headers.md) |
| Proving a caching or projection change worked: byte-identical contract, forced cache miss, eviction, server think time. | [dotnet-response-caching-compression-verification](dotnet-response-caching-compression-verification.md) |

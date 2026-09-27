# Response performance triage: which win to take first

## The four wins, in the order they pay

| Symptom | Fix | Typical effect |
| --- | --- | --- |
| Endpoint reads MBs, emits KBs | Project the unread columns away in the `Select` | the whole win; everything below is a rounding error next to it |
| Payload ships uncompressed | `AddResponseCompression` | 4x on JSON |
| Same aggregate rebuilt per request | `AddOutputCache` on the one anonymous `GET` | server time to ~0 |
| Binary endpoint re-fetched every page | `Cache-Control` + `ETag` | the request disappears |

**Measure before assuming the order.** A 2.6 s endpoint returning 109 KB is not a bandwidth problem.
Find what the query materialises versus what the response emits before reaching for a cache.

Back to the index: [dotnet-response-caching-compression](dotnet-response-caching-compression.md)

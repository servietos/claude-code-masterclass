# Proving the optimisation: byte diff, forced miss, server time

## Verification, and why each step exists

**1. Byte-identical contract.** The only acceptance test for a projection change:

```bash
curl -s -H "Accept-Encoding: identity" http://localhost:5157/api/content | python -m json.tool --sort-keys > after.json
diff before.json after.json
```

Capture `before.json` *before* touching anything. Request `identity` or the compression confuses the
comparison. An empty diff is the criterion; do not rationalise a difference.

**2. Force a cache miss without mutating data.** The key includes the query string, so a unique
`?nocache=$RANDOM` per request measures the real work every time. This is how you separate the
projection win from the cache win.

**3. Prove eviction without changing a row.** Issue a `PUT` that writes the current values back and
omits the blob field (the handler's `if (!string.IsNullOrEmpty(dto.Data))` guard preserves it). EF
detects no change and emits no UPDATE, but the request is a genuine successful write, so the tag is
evicted. Then watch the next `GET` fall back to miss timing and recover.

**4. Server time on a remote slot.** Wall clock from a dev machine is mostly your own round trip.
Subtract it:

```bash
FMT='tls=%{time_appconnect} ttfb=%{time_starttransfer} total=%{time_total} size=%{size_download}\n'
curl -s -o /dev/null -w "$FMT" https://host/health          # the floor
curl -s -o /dev/null -w "$FMT" https://host/api/content     # the endpoint
```

`ttfb(endpoint) - ttfb(/health)` on the same connection is the server think time. Reporting the raw
total instead makes a fixed endpoint look slow and a fast network look like an optimisation.

**5. Expect one slow first request per deploy.** JIT plus EF model build plus the first pooled
connection cost seconds on the first hit after a container restart. Warm it before quoting a number.

Back to the index: [dotnet-response-caching-compression](dotnet-response-caching-compression.md)

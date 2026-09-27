# NDJSON streaming into a signal store

## NDJSON Streaming into Signal Store


When a store feature must consume a server-sent NDJSON stream:

1. Use `fetch` (not `HttpClient`) to POST and obtain `response.body.getReader()`.
2. Decode chunks with `new TextDecoder()` in streaming mode; split on `\n`; parse each non-empty line as JSON.
3. Drive `patchState` for each event type (`stage`, `cost`, `result`) as lines arrive.
4. Fall back to an `HttpClient` call on any `fetch` rejection, non-200 response, or absent body.
5. Put the fallback in a separate async function and call it from both the `catch` block and the non-ok guard.
6. Revoke any object-URL (`URL.revokeObjectURL`) in both success and error paths.

Reference implementation: `src/inventory-ui/src/app/store/features/with-scan.feature.ts` (`resolvePhotoStream`).

Back to the index: [angular-conventions](../SKILL.md)

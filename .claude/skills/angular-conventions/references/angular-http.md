# Angular HTTP & Data Fetching

Fetch data in Angular using signal-based `resource()`, `httpResource()`, and the traditional `HttpClient`.

TypeScript HTTP types are wishes, not guarantees: guard array responses with `Array.isArray` before storing them.

| You want to... | Read |
| --- | --- |
| Declare a signal HTTP resource; status() and the @switch over it | [http-resource](angular-http-http-resource.md) |
| Async fetch with a custom loader instead of HttpClient | [generic-resource](angular-http-generic-resource.md) |
| Observables, toSignal(), GET/POST/PUT/PATCH/DELETE, options | [httpclient](angular-http-httpclient.md) |
| Bearer token, global 401 catch, logging, registration | [interceptors](angular-http-interceptors.md) |
| retry/catchError, or Symbol.iterator is not a function | [error-handling](angular-http-error-handling.md) |
| Structure an injectable data service with CRUD calls | [service-layer](angular-http-service-layer.md) |
| TTL Map cache or signal-backed cache, and invalidation | [caching](angular-http-caching.md) |
| Page signals, or append pages behind a Load More button | [pagination](angular-http-pagination.md) |
| Post FormData, HttpEventType progress, multiple files | [file-upload](angular-http-file-upload.md) |
| Abort in-flight requests, takeUntilDestroyed, debounce | [cancellation](angular-http-cancellation.md) |
| HttpTestingController, expectOne, flush, verify | [testing](angular-http-testing.md) |

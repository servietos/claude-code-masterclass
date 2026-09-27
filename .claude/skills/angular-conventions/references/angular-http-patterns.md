# Angular HTTP Patterns

How an Angular app talks to a backend.

## Table of Contents

| You want to... | Read |
| --- | --- |
| Wrap HttpClient in a service: CRUD plus a reactive httpResource | [service-layer](angular-http-patterns-service-layer.md) |
| Stop refetching: TTL Map cache, or signal cache with invalidation | [caching](angular-http-patterns-caching.md) |
| Page-at-a-time results with Previous/Next and page/pageSize params | [pagination](angular-http-patterns-pagination.md) |
| Accumulate pages into one growing list behind a Load More button | [infinite-scroll](angular-http-patterns-infinite-scroll.md) |
| IntersectionObserver sentinel never fires and nothing ever loads | [sentinel-traps](angular-http-patterns-sentinel-traps.md) |
| POST a FormData file with upload progress, or several files | [file-upload](angular-http-patterns-file-upload.md) |
| Cancel the previous in-flight request, debounce and switchMap | [cancellation](angular-http-patterns-cancellation.md) |
| Test with HttpTestingController, expectOne, flush and verify | [testing](angular-http-patterns-testing.md) |

Feature roots must not set `h-full`.

# What stays out of the store

## What stays OUT of the store

- **Auth** — MSAL / `AuthStateService` (the sanctioned exception).
- **Cross-cutting utility services** — download/blob export (`download.service.ts`), telemetry (`app-insights.service.ts`), client-IP utility (`ip-service`). These are stateless helpers, not domain state.
- **Deliberately backend-less caches** — e.g. `home-chat-history.service.ts` (localStorage only, no API). Document each such exception explicitly.

A stateless HTTP proxy service that the store's `rxMethod`s call (e.g. `PlanningService`, `ResourcesService`, `task-chat.service.ts`) is correct — it is the HTTP layer *for* the store, not a competitor to it.

Back to the index: [angular-signal-store-design](angular-signal-store-design.md)

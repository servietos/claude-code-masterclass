# HTTP variant choice

## Two HTTP variants — pick per repo convention

**(a) Inject `HttpClient` directly in the feature** (citythong `with-members.feature.ts`). Feature owns the endpoint URLs. Good for greenfield / no existing service.

**(b) Wrap an existing feature service** (this repo — `with-planning.feature.ts` wraps `PlanningService`). Keep the service as the HTTP layer (it owns base URL + endpoints); the slice only manages state and wraps the service methods in `rxMethod`s. **New maintenance-planner slices use (b).**

Both use `rxMethod` + `tapResponse` (`@ngrx/operators`) for async; choose the flattening operator deliberately — `switchMap` (cancel prior), `exhaustMap` (ignore while in-flight, e.g. saves — see `with-planning.feature.ts`), `concatMap` (queue).

Back to the index: [angular-signal-store-design](angular-signal-store-design.md)

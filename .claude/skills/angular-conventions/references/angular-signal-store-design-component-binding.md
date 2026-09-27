# Component binding to the store

## Component binding

Components consume the store; they do not own domain state.

- **Direct bind:** `private store = inject(AppStore);` then read `store.entries()` / call `store.loadTimesheet(param)`.
- **Container/presenter:** a container `inject`s the store and passes signals down via `input()` to presentational children (reference: `schedule-container` → `scheduler.component` → `scheduler-row`). Presentational children take `input()/output()` only and never inject the store.
- **Resolvers** may patch the store before a route activates (reference: `resources/resolvers/resource.resolvers.ts`).

Anti-patterns this replaces (see `references/angular-antipatterns.md`): plain non-signal class fields for domain data, bare `.subscribe()` in components, manual `ChangeDetectorRef.markForCheck()`, per-component `BehaviorSubject` services, duplicate fetches of the same endpoint from two components (share one slice instead).

Back to the index: [angular-signal-store-design](angular-signal-store-design.md)

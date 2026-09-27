# Slice granularity: one per domain

### Getting the granularity right — one slice per DOMAIN, not per screen

A "domain" is a cohesive area of the app, not an individual view. Over-splitting is as wrong as under-binding:

- **Don't split one domain across several slices.** The task *planner* is part of the *tasks* domain → it belongs in `withTasks`, not a separate `withTaskPlanner`. The *timesheet* is part of *planning* → it belongs in `withPlanning`, not a separate `withTimesheet`. If two slices only ever change together or one wraps a subset of the other's service, they are one domain — merge them. (Merging is a pure internal move: because every method lives on the single composed `AppStore`, moving definitions between feature functions does **not** change the public API, so component consumers need no changes — the build proves it.)
- **Don't split a domain across a feature slice AND a companion service.** State that belongs in the store must not live in a `providedIn: 'root'` service that mutates the store from the outside. The sidenav was state (`sideNavVisible/Position/Collapsed`) sitting inline in base state with a separate `SideNavService` doing the responsive bootstrap — the correct shape is a single `withSidenav()` slice that owns both the state and the bootstrap (see `withHooks` below). Once the slice owns it, the service is dead code — delete it.

Back to the index: [angular-signal-store-design](angular-signal-store-design.md)

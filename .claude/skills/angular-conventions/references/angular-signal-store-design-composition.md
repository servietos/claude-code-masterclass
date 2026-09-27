# Root store composition

How to design application state so a **single composed signal store fully serves the app** — state *and* data access — with components binding to it directly or through a container/presenter split. The only things that stay outside the store are auth (MSAL), cross-cutting utility services, and deliberately backend-less caches.

Reference implementations: `src/ui/src/app/store/app.store.ts` (this repo), `citythong-members/.../store/members.store.ts`, `vouchers-ai/.../store/vouchers.store.ts`.

## Core shape

One `signalStoreFeature()` per domain, composed into a single root `signalStore({ providedIn: 'root' })`.

```ts
// store/app.store.ts
export const AppStore = signalStore(
  { providedIn: 'root', protectedState: false },
  withState(initialAppState),   // base shell state (testing, invited, …)
  withMethods(/* base methods */),
  withActivity(),               // cross-cutting slices first (see angular-activity-indicator)
  withSidenav(),
  withTasks(),                  // task authoring AND the task planner live in ONE slice
  withPlanning(),               // scheduling grid, mailing AND timesheet — one planning domain
  withResources(),
  // …one with<Domain>() per feature area
);
```

Rules:
- **One file per domain:** `store/features/with-<domain>.feature.ts`, colocated `with-<domain>.spec.ts`.
- Each feature = `withState` (+ `withComputed` for derived signals) + `withMethods`.
- State mutations go through `patchState(store, { … })` — never assign signals directly.
- Compose everything into ONE root store. Do **not** create parallel `providedIn: 'root'` domain stores or services-with-`BehaviorSubject`.

Back to the index: [angular-signal-store-design](angular-signal-store-design.md)

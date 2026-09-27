# Angular Signal Store Design (`@ngrx/signals`)

Routing table for state built as one composed `@ngrx/signals` store.

Hard rule:

- State mutations go through `patchState(store, { … })` — never assign signals directly.

| You want to... | Read |
| --- | --- |
| Shape the root store, one feature per domain | [composition](angular-signal-store-design-composition.md) |
| Decide if something is its own slice | [slice-granularity](angular-signal-store-design-slice-granularity.md) |
| Bootstrap a slice (responsive, seed, subscribe) | [lifecycle-hooks](angular-signal-store-design-lifecycle-hooks.md) |
| Write a new `with-<domain>.feature.ts` | [slice-template](angular-signal-store-design-slice-template.md) |
| Choose HttpClient vs service, and the operator | [http-variants](angular-signal-store-design-http-variants.md) |
| Fix `NG0200: Circular dependency` | [circular-dependency](angular-signal-store-design-circular-dependency.md) |
| Bind a component, container/presenter | [component-binding](angular-signal-store-design-component-binding.md) |
| Debug a saved value absent on screen | [race-resets](angular-signal-store-design-race-resets.md) |
| Debug the same GET firing forever | [effect-loops](angular-signal-store-design-effect-loops.md) |
| Check if a service stays out of the store | [outside-the-store](angular-signal-store-design-outside-the-store.md) |
| Place specs, run the checklist | [testing-and-checklist](angular-signal-store-design-testing-and-checklist.md) |

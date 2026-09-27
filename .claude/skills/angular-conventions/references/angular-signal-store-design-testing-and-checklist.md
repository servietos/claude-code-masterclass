# Spec placement and review checklist

## Testing

Colocate `with-<domain>.spec.ts` next to each feature (reference: `store/features/with-planning.spec.ts`, `with-resources.spec.ts`). Instantiate the feature in a store, mock the injected service, drive methods, assert on the resulting signals.

## Checklist

- [ ] One `with-<domain>.feature.ts` per domain, composed into the single root store.
- [ ] State via `withState` + `patchState`; derived via `withComputed`.
- [ ] Async via `rxMethod` + `tapResponse`, correct flattening operator.
- [ ] New slices wrap the existing feature service (variant b).
- [ ] Components bind to the store (direct or container/presenter); presentational children stay `input()/output()`-only.
- [ ] No domain state in plain class fields, no bare `.subscribe()`, no manual `markForCheck()`.
- [ ] Colocated `*.spec.ts`.
- [ ] Only auth / utility services / documented localStorage caches remain outside the store.

Back to the index: [angular-signal-store-design](angular-signal-store-design.md)

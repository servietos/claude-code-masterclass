# NG0200 circular dependency

### Circular dependency gotcha (variant b)

If the service you wrap **itself injects `AppStore`** (e.g. `ResourcesService` calls `patchState` on the store), the usual eager default-parameter shape `withMethods((store, svc = inject(ResourcesService)) => …)` throws at bootstrap:

```
NG0200: Circular dependency: AppStore -> ResourcesService -> AppStore
```

Resolve the service **lazily** so it isn't constructed until the first method call, which breaks the cycle:

```ts
withMethods((store) => {
  const injector = inject(Injector);
  return {
    saveHouse: rxMethod<{ house: House; onSuccess?: () => void }>(
      pipe(exhaustMap(({ house, onSuccess }) =>
        injector.get(ResourcesService).saveHouse(house).pipe(
          tapResponse({
            next: (saved) => { patchState(store, /* upsert */); onSuccess?.(); },
            error: () => {},
          }),
        ),
      )),
    ),
  };
})
```

Reference: `store/features/with-mail-templates.feature.ts` and `with-resources.feature.ts`. Prefer moving the save→upsert step into the slice (as above) over leaving a `service.save().subscribe(saved => store.upsertX(saved))` in each edit component.

Back to the index: [angular-signal-store-design](angular-signal-store-design.md)

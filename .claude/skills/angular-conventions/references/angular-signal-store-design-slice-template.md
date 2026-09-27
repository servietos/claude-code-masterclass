# Feature slice template

## Feature slice template

```ts
// Generic illustration of slice shape (a made-up "reports" domain).
export interface ReportsState {
  reports: Report[];
  reportsLoading: boolean;
  selected: Report | null;
}

export function withReports() {
  return signalStoreFeature(
    withState<ReportsState>({ reports: [], reportsLoading: false, selected: null }),

    withComputed((store) => ({
      hasReports: computed(() => store.reports().length > 0),
    })),

    // Repo convention: inject the existing feature SERVICE and wrap it.
    withMethods((store, svc = inject(ReportsService)) => ({
      loadReports: rxMethod<ReportsParam>(
        pipe(
          switchMap((param) => {
            patchState(store, { reportsLoading: true });
            return svc.getReports(param).pipe(
              tapResponse({
                next: (reports) => patchState(store, { reports, reportsLoading: false }),
                error: () => patchState(store, { reportsLoading: false }),
              }),
            );
          }),
        ),
      ),
    })),
  );
}
```

Back to the index: [angular-signal-store-design](angular-signal-store-design.md)

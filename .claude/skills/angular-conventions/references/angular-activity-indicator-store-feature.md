# withActivity store slice and explicit AI activity

A global activity indicator driven by the **signal store**: an HTTP request counter *plus* an explicit `aiActive` flag, combined into one `isBusy` signal. Any in-flight request **or** any long-running non-HTTP work (e.g. an AI agent streaming/thinking) shows the bar. No per-component `loading` booleans for global chrome.

> Formerly "loading indicator" (`withLoading`/`isLoading`). Generalized to `withActivity`/`isBusy` so the same bar can signal AI activity, not just HTTP loading.

Reference: `src/ui/src/app/store/features/with-activity.feature.ts` + `src/ui/src/app/store/activity.interceptor.ts`.

## 1. The `withActivity` feature slice

```ts
// store/features/with-activity.feature.ts
type ActivityState = { pendingRequests: number; aiActive: boolean };

export function withActivity() {
  return signalStoreFeature(
    withState<ActivityState>({ pendingRequests: 0, aiActive: false }),
    withComputed((store) => ({
      // busy when any HTTP request is in flight OR explicit activity is set
      isBusy: computed(() => store.pendingRequests() > 0 || store.aiActive()),
    })),
    withMethods((store) => ({
      requestStarted(): void {
        patchState(store, { pendingRequests: store.pendingRequests() + 1 });
      },
      requestFinished(): void {
        patchState(store, { pendingRequests: Math.max(0, store.pendingRequests() - 1) });
      },
      // explicit, non-HTTP activity (AI agent run, long compute, etc.)
      setAiActive(active: boolean): void {
        patchState(store, { aiActive: active });
      },
    })),
  );
}
```

Compose it into the root store early (before domain slices):

```ts
export const AppStore = signalStore(
  { providedIn: 'root', protectedState: false },
  withState(initialAppState),
  withActivity(),
  // …domain slices
);
```

## 4. Drive the AI/activity side explicitly

For work the interceptor can't see (an AI agent run, a long client-side compute), wrap it:

```ts
store.setAiActive(true);
try {
  await runAgent();
} finally {
  store.setAiActive(false);   // always clear, even on error
}
```

Back to the index: [angular-activity-indicator](angular-activity-indicator.md)

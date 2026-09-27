# Bootstrap logic in withHooks

### Lifecycle/bootstrap logic → `withHooks(onInit)`, not a service constructor

Bootstrap side-effects a slice needs (responsive layout, a one-time seed, a subscription) go in the slice's `withHooks({ onInit })`, which runs when the store is first constructed — you can `inject()` inside it:

```ts
withHooks({
  onInit(store) {
    const destroyRef = inject(DestroyRef);
    const mq = window.matchMedia('(max-width: 959.98px)');
    const apply = (mobile: boolean) => patchState(store, {
      sideNavVisible: !mobile, sideNavPosition: mobile ? 'over' : 'side',
    });
    apply(mq.matches);
    const listener = (e: MediaQueryListEvent) => apply(e.matches);
    mq.addEventListener('change', listener);
    destroyRef.onDestroy(() => mq.removeEventListener('change', listener));
  },
})
```

**jsdom test gotcha:** once a root slice's `onInit` touches `window.matchMedia`, that runs on **every** `AppStore` construction across the whole spec suite, and jsdom has no `matchMedia` — add a guarded polyfill to `src/test-setup.ts` (specs that assert responsive behavior override it with `vi.stubGlobal`).

Back to the index: [angular-signal-store-design](angular-signal-store-design.md)

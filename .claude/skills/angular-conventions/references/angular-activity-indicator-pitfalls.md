# Activity indicator pitfalls and tests

## Notes / pitfalls

- **Global, not per-view.** For a *specific* long operation you still want a local `xLoading` flag in the owning slice (e.g. `membersLoading`); `withActivity` is only for the app-wide bar.
- **Always clear `aiActive`** in a `finally` — a thrown error mid-run must not leave the bar stuck on.
- **Excludes.** If polling / telemetry requests should not trip the bar, branch in the interceptor on `req.url` / a custom `req.context` token before `requestStarted()`.
- **Constant footprint (no jump).** The indicator must occupy identical layout idle vs. active or neighbors shift when busy toggles. Two traps hit `gen-loader` and were fixed: (1) an a11y text node inserted only while active (`@if (active()) { <span class="sr-only">…</span> }`) — this app has **no** global `.sr-only`, so it rendered in-flow and its removal on deactivate jumped the wallet/badges left; keep the node always-present, component-scoped-hidden, and toggle only its text. (2) `animation-play-state: paused` for the idle state froze the dots on a random bright frame; use `animation: none` idle and attach the animation only under `--active`. See `angular-antipatterns` → "Visually-hidden text & CSS animation". Verify by sampling a neighbor's `getBoundingClientRect().left` across idle→active→idle.
- **Test:** drive `requestStarted()` × n then `requestFinished()` × n and assert `isBusy()` flips true→false only at zero; separately assert `isBusy()` is true when `aiActive` is set with zero pending requests (reference: `with-activity.spec.ts`).

Back to the index: [angular-activity-indicator](angular-activity-indicator.md)

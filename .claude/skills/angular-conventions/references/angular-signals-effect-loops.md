# Effect Request Storms

### Gotcha: effects track EVERY synchronous read, including hidden ones inside called methods

An `effect()`/`computed()` records a dependency on **every** signal read during its synchronous run — not just the ones you named at the top, but any incidental read deep inside a method, service, or HTTP interceptor it calls on the same call stack. If that same signal is then written as a side effect, the effect reschedules itself → **infinite loop** (under zoneless change detection this hangs the browser).

Classic trigger: an `effect()` that fires an HTTP request, where a global "activity"/"loading" interceptor reads-then-writes a shared `pendingRequests` (or `isBusy`) signal on every request. The effect silently takes a dependency on that counter; its own request bumps it, which reschedules the effect, which fires another request — a self-sustaining request storm independent of the data.

**Rule:** read your intended dependency signals explicitly at the top of the effect, then wrap any side-effecting call (anything that issues HTTP or otherwise touches shared store signals) in `untracked()`:

```typescript
onChange = effect(() => {
  const id = this.selectedId();          // real deps, read tracked
  if (id) {
    untracked(() => this.loadDetails());  // side effect — do NOT track its internal reads
  }
});
```

Symptom to recognize: an endless stream of identical requests in the network/API console after a component with an `effect()` mounts, where the effect's named dependencies never actually change value.

Back to the index: [angular-signals](angular-signals.md)

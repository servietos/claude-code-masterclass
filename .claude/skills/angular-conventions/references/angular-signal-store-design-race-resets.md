# Resets and parallel races

## Resets never live in a parallel request's handler

Two `rxMethod`s dispatched together are a race decided by payload size, not by call order. A reset
written into one response handler will stomp state the other has already loaded.

```ts
// WRONG — details is the fatter payload, so it always lands last and wipes the loaded rule
loadDetails: rxMethod<string>(pipe(switchMap(id => service.getDetails(id).pipe(tapResponse({
  next: d => patchState(store, { current: d, currentRule: null, pendingRule: null }),
})))))

// RIGHT — clear synchronously before dispatching, in the one entry path that needs it
onNew() { this.store.clearEdit(); this.store.loadDetails(id); }
```

Symptom: a saved value is present in the network tab and absent on screen, reproducibly, and
"works" whenever the other endpoint is slow. Rules:

- A response handler patches what its own response carries, nothing else.
- A reset that exists to protect one entry path is fixed at that entry path, not on every response.
- Pin it with a spec that flushes the two responses in **both** orders; only the real-world order
  fails, so a single-order test passes against the bug.

Back to the index: [angular-signal-store-design](angular-signal-store-design.md)

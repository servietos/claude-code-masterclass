# Infinite load-on-input loops

## A store method must not read store signals in its `patchState` arguments

A component that loads on an input change writes `effect(() => this.store.load(this.id()))`. Every
signal the method reads **synchronously** becomes a dependency of that effect, so a method that reads
the state it is about to write turns the effect into an infinite request loop.

```ts
// WRONG — store.versionsOf() and store.versions() are read inside the effect's reactive context,
// and the same call writes both. Each response re-runs the effect and fires the next request.
loadVersions(name: string) {
  patchState(store, {
    versions: store.versionsOf() === name ? store.versions() : [],
    versionsOf: name,
    versionsLoading: true
  });
  return service.getVersions(name).pipe(tap(v => patchState(store, { versions: v, versionsLoading: false })), ...);
}

// RIGHT — the updater's `state` is a plain object, not a tracked read
patchState(store, (state) => ({
  versions: state.versionsOf === name ? state.versions : [],
  versionsOf: name,
  versionsLoading: true
}));
```

```ts
// AND at the call site: the effect depends on its inputs only
effect(() => {
  const name = this.secretName();
  untracked(() => this.store.loadVersions(name).subscribe());
});
```

Both halves. The updater form fixes this method; `untracked` at the call site stops the next method
that forgets. Symptom: the page renders correctly and nothing errors — the only evidence is the
network panel filling with the same GET, so check it after wiring any load-on-input effect.

Back to the index: [angular-signal-store-design](angular-signal-store-design.md)

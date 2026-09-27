# File Drop Zone: Global Store-Event Variant

### Store-event variant (shared/global drop target)

For a drop zone that lives in a shared shell (e.g. a global sidebar or the home shell) and must route to whichever feature is active, don't use a local `output` — fire a **store event** instead and let features react in an `effect()`:

```ts
// in the drop handler
onDrop(e: DragEvent) {
  e.preventDefault(); this.dragging.set(false);
  const files = Array.from(e.dataTransfer?.files ?? []);
  if (files.length) this.store.fireFileDrop({ files });     // { seq, files } event on the store
}
```

```ts
// in the active feature
constructor() {
  effect(() => {
    const evt = this.store.fileDropEvent();
    if (!evt || evt.seq === this.lastSeq) return;
    this.lastSeq = evt.seq;
    this.categorizeAndRoute(evt.files[0]);   // e.g. API /documents/categorize → open the right wizard
  });
}
```

Back to the index: [angular-file-dropzone](angular-file-dropzone.md)

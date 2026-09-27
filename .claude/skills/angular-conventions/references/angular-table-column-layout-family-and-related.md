# The data-table leaf family and where its state lives

## The data-table family, in order

These three leaves are meant to be applied in sequence. Each one assumes the
previous is already in place, and later leaves tighten earlier rules.

1. **`angular-table-column-layout`** (this file): pin the geometry so columns stop
   moving. Prerequisite for the other two.
2. **`angular-table-column-resize`**: let the user drag column widths, persist them,
   and stop the flexible column from collapsing. **Supersedes the fit invariant
   stated here** with a stronger one.
3. **`angular-table-column-visibility`**: let the user show and hide columns, which
   changes which columns compete for width, so it must be built on the sizing model
   from leaf 2.

Skipping ahead does not work: resizing on an unpinned table reintroduces the jump,
and visibility on a naive sizing model produces a column crushed to a few pixels.

## Related

- `angular-draggable-splitter.md` for the Pointer Events plus `setPointerCapture`
  drag pattern, which is the same mechanism a column-resize handle uses.
- `angular-signal-store-design.md` for where per-user layout state belongs.
  Persisted column geometry is per-user UI preference: it goes in a
  `signalStoreFeature` slice backed by `localStorage` under a namespaced key,
  with reads and writes wrapped in `try/catch` so blocked storage degrades to
  non-persistent instead of throwing. It does not belong in any DB-backed
  application settings layer, which is app-wide config and a different concern.

Back to the index: [angular-table-column-layout](angular-table-column-layout.md)

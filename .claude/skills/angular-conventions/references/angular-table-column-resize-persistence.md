# Persisting column widths per user

## Persistence

Per-user UI preference: a `signalStoreFeature` slice backed by `localStorage`
under a namespaced key, reads and writes wrapped in `try/catch` so blocked storage
degrades to non-persistent. Not a DB-backed app-settings layer, which is app-wide
config and a different concern.

Two rules that were each learned the hard way:

- **Version the payload**: `{ v: 2, widths: { ... } }`. Discard the whole payload
  on a version mismatch (and on a payload with no version at all). Without this,
  changing a default is a silent no-op for every existing user. This actually
  happened: a stale `{"date":160,"type":158,...}` from a previous build overrode
  every new default and reintroduced a 141px overflow, while the same build
  verified clean in a browser profile that had no key.
- **Store only what the user actually changed.** Do not pre-fill storage with the
  defaults on load. A sparse map means a future defaults change reaches everyone
  who never touched that column, with nothing to migrate, and it makes reset a
  uniform "delete the override" for every column including the flexible one.

Commit widths to storage on drag end, not on every pointermove.

Back to the index: [angular-table-column-resize](angular-table-column-resize.md)

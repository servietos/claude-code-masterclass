# Persisting the visibility choice

## Persistence

Its own namespaced key, separate from the widths, with the **same versioned
envelope** (`{ v: 1, visibility: { ... } }`) and the same tolerate-anything read
that falls back to defaults on malformed or wrong-version payloads. Skipping the
version here reproduces the stale-storage bug documented in
`angular-table-column-resize.md` in a second place.

Store a sparse map of only the columns the user actually touched, so a later change
to which columns ship hidden reaches everyone who never touched them. Persist
immediately on toggle: unlike a drag, it is a discrete action with no stream of
intermediate values.

Back to the index: [angular-table-column-visibility](angular-table-column-visibility.md)

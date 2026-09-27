# Changing the stored unit

## Changing the stored unit needs a new storage key

The pixel and ratio variants persist under the same kind of key, and a value written by one is a
plausible value for the other: a stored `440` from the px build parses as a finite number, clamps into
a ratio's `[0.25, 0.6]`, and silently opens the pane at the maximum. The layout, the CSS and the
component are all correct while the split is visibly wrong, and only for people who used the earlier
build — which is everyone except a fresh browser.

- Change the key with the unit (`…-split` -> `…-split-ratio`), so an old value is simply absent.
- Validate the parsed value against the new domain, not just `Number.isFinite`: for a ratio, reject
  `parsed <= 0 || parsed >= 1` and fall back to the default.
- Verify a changed default by measuring the rendered panes after clearing the key, never on the
  browser you developed in.

Back to the index: [angular-draggable-splitter](angular-draggable-splitter.md)

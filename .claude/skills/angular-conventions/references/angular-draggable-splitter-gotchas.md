# Splitter field gotchas

## Gotchas learned in the field

- **A component named `split`/`ux-split` may be a *static* grid, not a splitter.**
  Grep the implementation before reusing — a `grid-template-columns: auto 240px`
  with an empty TS is not draggable. Don't assume the name implies drag.
- **`aria-valuenow` won't update unless bound to the live signal.** If a keyboard/
  drag resize "does nothing" in a snapshot, first check the attribute is
  `[attr.aria-valuenow]="rightWidth()"`, not a static/initial value.
- **When verifying in a browser, a click may only *hover* the divider** (shows the
  focus/hover color) without giving it keyboard focus — a keyboard-resize test can
  read as broken when it's the harness, not the code. Verify the primary
  interaction (pointer drag) directly; it exercises the real
  pointerdown→move→up→capture path.
- Persisted width survives reloads — when done testing, **clear the storage key**
  (or reset to default) so you don't leave a maxed/min width behind for the user.

## Field gotchas

- **Verify the pointer drag, not just keyboard,** in the browser: a click may only
  *hover* the divider (gold shows) without giving it keyboard focus, so a keyboard
  test can read as broken when it's the harness. `aria-valuenow` in a snapshot is
  the reliable read of the current width.
- Persisted width survives reloads — after testing a drag, **clear the storage
  key** (`localStorage.removeItem('edit-task-split')`) so you don't leave a
  maxed/min width behind for the user.

For the full generic pattern (edge-anchored width, `linkedSignal` seed, pointer
capture, CSS-var grid, testing shape), the global copy of this reference carries a
project-agnostic version.

Back to the index: [angular-draggable-splitter](angular-draggable-splitter.md)

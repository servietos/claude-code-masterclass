# Resize handle directive: pointer capture, sort suppression, minimums, keyboard

## The handle

A small attribute directive on a `<span>` inside each resizable `<th>`, using
Pointer Events plus `setPointerCapture` (same mechanism as
`angular-draggable-splitter.md`: no document-level listeners, no `Renderer2`,
no manual add/removeEventListener).

Non-obvious requirements, each of which is a real bug if missed:

- **The drag must not trigger the column's sort.** Sort headers are click
  activated, and a drag ends in a click. Track whether the pointer actually moved
  (a small threshold, a couple of px, so a jittery click still counts as a click),
  and on the trailing `click` call `preventDefault()`/`stopPropagation()` when it
  moved. Verify by asserting `aria-sort` is unchanged after a drag.
- **Read the drag-start width from the live `<th>`**, via its rendered box, not
  from the bound input value. A flexible column's bound value can be a nominal
  placeholder rather than its real rendered width, and starting from that makes the
  column jump on the first drag. Reading the element is also correct for every
  other column, so there is no reason to special-case it.
- **`touch-action: none`** on the handle so touch drags do not scroll the page.
- **Clamp to a per-column minimum** chosen from real measured content, not guessed
  character counts. Columns that cannot ellipsize (a date, a badge or pill) need a
  minimum that fits their content exactly, because below it they visibly bleed.
  Columns with `truncate` can go much smaller safely.
- **Keyboard**: the handle is focusable, `role="separator"`,
  `aria-orientation="vertical"`, live `aria-valuemin`/`valuemax`/`valuenow`, and
  Left/Right arrows adjust by a step. Label it in the app's UI language.
- **Double-click resets that column** to its default. Keep the defaults in code as
  the single source of truth so a reset is always possible.

Back to the index: [angular-table-column-resize](angular-table-column-resize.md)

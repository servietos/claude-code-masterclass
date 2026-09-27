# Reorder drop affordances

### Reorder affordances — indicate *where* it lands

Reordering needs *more* drop feedback than a cell-move, not less: a cell-move
highlights the target cell, but a reorder must show the **insertion position**.
Three affordances, all proven necessary in practice — a reorder with only a
`cursor: grab` handle reads to users as "nothing is happening":

- **Grip handle at rest.** Put a visible drag-grip glyph (six-dot ⠿) on the
  handle so it reads as draggable — `cursor: grab` is discovered only on hover.
  With no icon library, an inline six-dot SVG works; mute it at rest, brighten
  on hover/focus/dragging. Hide it on the non-draggable (empty/placeholder) row.
- **Insertion-line indicator.** Render a thin accent-colored bar at the boundary
  where the row will land — not a full-row outline. Derive the edge from
  source-vs-target index: hovering a row *above* the dragged one means "insert
  before it" (top edge); *below* means "insert after it" (bottom edge), because
  an index-rewrite reorder drops the strip exactly at the target's position.
  Drive it from a `dragOverIndex` **signal** (a plain field never re-renders the
  view) and clear it on drop **and** `pointercancel`.
- **Whole-row dragging state.** Apply the dragging class to the *entire* row, not
  just the handle cell, so the whole strip visibly lifts (opacity + shadow).
  Dimming only the small handle looks like a rendering glitch.


Back to the index: [angular-drag-drop](angular-drag-drop.md)

# Disabled sources and blocked cells

## Disabled and not-allowed, end to end

| State | Source behavior | Target behavior |
| --- | --- | --- |
| Disabled item | `disabled()` input short-circuits `onPointerDown` before `pointerId`/`startPoint` are set — no drag can start | n/a |
| Disabled item, visual | `.is-disabled` host class sets `cursor: not-allowed`, dimmed opacity; `disabledReason` renders as `title`/tooltip | n/a |
| Occupied/blocked cell | n/a | `data-blocked="true"` flows into `cellAtPoint()`'s `blocked` flag; `dragOverCell` still resolves the cell (for the red highlight) but `onDragDropped` refuses to call `moveItem()` when `cell.blocked` is true |
| Occupied cell, visual | n/a | `drag-grid__cell--drag-over-invalid` (red ring) instead of `--drag-over` (gold ring); container cursor becomes `not-allowed` while hovering a blocked cell |


Back to the index: [angular-drag-drop](angular-drag-drop.md)

# Angular Table Column Resize

User-draggable column widths for a data table, persisted per user. Standalone
Angular 22, signals, `OnPush`, no CDK and no third-party grid.

Read `angular-table-column-layout.md` first. Resizing only makes sense on a table
that is already `table-fixed` with a stable geometry, and the auto-fill rule below
is what keeps resizing from breaking that stability.

The governing invariant, whichever leaf you land in: **Never crush a column.**

| You want to... | Read |
| --- | --- |
| Building or fixing the drag handle: pointer capture, the drag that fires the column sort, per-column minimums, keyboard resize, dblclick reset. | [angular-table-column-resize-handle](angular-table-column-resize-handle.md) |
| A column renders 4px wide, or min-width is ignored under table-layout: fixed: why the unsized soak-up column collapses and what to compute instead. | [angular-table-column-resize-flexible-column](angular-table-column-resize-flexible-column.md) |
| Storing widths per user: which store, the versioned payload that lets a default change land, and why only user-changed columns get written. | [angular-table-column-resize-persistence](angular-table-column-resize-persistence.md) |
| The measured width or overflow disagrees with the screenshot, or you need the check list to run after any resize change. | [angular-table-column-resize-verifying](angular-table-column-resize-verifying.md) |

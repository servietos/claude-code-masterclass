# Angular Table Column Visibility

A user-controlled column picker for a data table: show and hide columns, some
hidden by default, persisted per user. Standalone Angular 22, signals, `OnPush`.

Read `angular-table-column-layout.md` and `angular-table-column-resize.md` first.
Visibility changes which columns compete for width, so it is inseparable from the
sizing model.

**Never let the table go empty**: block hiding the last checked column, and
disable that checkbox rather than silently ignoring the click.

| You want to... | Read |
| --- | --- |
| Place the trigger; button vs right-click menu | [angular-table-column-visibility-placement](angular-table-column-visibility-placement.md) |
| Model per-column state; defaults and unhideable columns | [angular-table-column-visibility-override-model](angular-table-column-visibility-override-model.md) |
| Fix a scrollbar or an under-minimum column on toggle | [angular-table-column-visibility-width-interaction](angular-table-column-visibility-width-interaction.md) |
| Fix one ESC closing two things, or lost focus | [angular-table-column-visibility-overlay-esc](angular-table-column-visibility-overlay-esc.md) |
| Persist the choice: key, envelope, sparse map | [angular-table-column-visibility-persistence](angular-table-column-visibility-persistence.md) |
| Verify: acceptance checklist and ground truth | [angular-table-column-visibility-verify](angular-table-column-visibility-verify.md) |

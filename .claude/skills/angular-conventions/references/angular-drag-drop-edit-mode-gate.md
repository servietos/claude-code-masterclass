# Gating reordering behind edit mode

### Gate reordering behind an explicit edit mode

On a read-first surface (a dashboard, a report, a card wall) permanent grip
handles add clutter and invite accidental reorders. Put the whole affordance
behind an edit toggle:

- An icon toggle (pencil) on the page, `aria-pressed` bound to the mode.
- Mode lives in the page component as `signal(false)`; the grid takes it as
  `readonly editMode = input(false)`.
- `@if (editMode())` around **each grip**, so no handle exists at rest.
- A command bar rendered only in edit mode, `role="toolbar"`, carrying the
  reorder hint plus the mode's commands ("Reset the order", disabled until a
  custom order exists). `position: sticky` keeps it reachable down a long page.
- Guard `onDragStart` on `editMode()` as well. Rendering is the affordance;
  the guard is the rule, and only the guard survives a stale DOM node.

Persist the order (localStorage keyed by id, or the backend) and make the reset
a command in that bar — a reorder that silently resets on reload reads as a bug,
and one with no way back traps the user.


Back to the index: [angular-drag-drop](angular-drag-drop.md)

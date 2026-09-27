# Why pointer-event drag without the CDK, and where it is implemented

A project-agnostic pattern for dragging cards onto grid cells (e.g. a day × time
schedule) and for reordering list rows, using only native **Pointer Events** —
no `@angular/cdk/drag-drop`, no `Renderer2`, no document-level listeners beyond
pointer capture. Use it when a repo does not carry `@angular/cdk` and needs
drag-and-drop for exactly one or two surfaces, where adding a 200KB+ dependency
for one directive isn't worth it.

> **Source note.** This reference distills the *architecture* of bauer-sport's
> schedule/staffing grids (`src/admin.citythong.at/src/app/schedule/`,
> `.../staffing/`) — signals-based drag state, `document.elementsFromPoint()` +
> `data-*` attributes to resolve the drop target, and hand-rolled auto-scroll.
> That source, however, delegates pointer capture and the drag gesture itself
> to `@angular/cdk/drag-drop`'s `CdkDrag` directive (used only in free-drag
> mode, without `CdkDropList`) — it does not call `pointerdown`/`pointermove`
> directly. Since `@angular/cdk` is **not** installed in this repo
> (`src/ui/package.json` has no `@angular/cdk` entry), the TS shape below
> reimplements `CdkDrag`'s pointer-capture mechanics with raw Pointer Events so
> the same architecture is available with zero added dependency. Reordering
> follows bauer-sport's `gallery-image-manager.ts`, which uses the **native
> HTML5 Drag and Drop API** (`dragstart`/`dragover`/`drop`, `DragEvent` +
> `dataTransfer`) rather than Pointer Events — noted as an alternative below.

## Design decisions

| Concern | Decision | Why |
| --- | --- | --- |
| Drag gesture | Pointer Events (`pointerdown`/`pointermove`/`pointerup`/`pointercancel`) + `setPointerCapture` on the source element | One unified event model for mouse, touch, and pen; no separate `touchstart`/`mousedown` handling |
| Click vs. drag | A movement threshold (~6px) or a touch-only `dragStartDelay` gates when a drag "engages" | A tap must still fire `click` to open/edit; only a real drag should suppress it |
| Drop-target lookup | Container resolves `document.elementsFromPoint(x, y)` on every `pointermove`, then reads `data-*` attributes off the first matching element | A schedule grid has dozens–hundreds of cells; one container-level lookup beats binding `(pointerenter)` to every cell, and stays correct even when overlay cards sit on top of cells |
| Overlay passthrough | Absolutely-positioned card wrappers get `pointer-events: none`; only the card itself is `pointer-events: all` | `elementsFromPoint` skips `pointer-events: none` elements during hit-testing, so the lookup falls through wrapper anchors straight to the grid cell underneath |
| Disabled sources | A `disabled` input short-circuits the `pointerdown` handler before any drag state is touched | A truly disabled item should never emit `dragStarted`, not just look disabled |
| Invalid targets | The resolved cell carries its own `blocked`/`occupied` flag; the container renders a distinct "not-allowed" highlight and refuses to persist on drop | One `dragOverCell` signal isn't enough once some cells are droppable and others aren't — validity must travel with the resolved target |
| Reordering | Rewrite an `{id, order}[]` array locally (optimistic), then persist the whole array to the backend | Matches how a sortable list is usually stored — a `SortOrder`/`order` column per row |
| State | `signal()` per concern (`draggedItem`, `dragOverCell`, `isDragging`) on `OnPush` components — no `BehaviorSubject`, no manual change detection | Signal reads in the template auto-invalidate the view; consistent with the rest of the app |

## Suggested home / reference implementation

This pattern is implemented end-to-end in the bico maintenance-planner scheduler
— `src/ui/src/app/planning/schedule/scheduler/`: `scheduler.component` is the
container / target resolver, `scheduler-cell` is the draggable source with
notified/not-allowed gating, and `scheduler-label-cell` is the row-reorder
handle (grip glyph + insertion-line indicator). Use it as the worked example:
cell-move + row-reorder + disabled/not-allowed sources + server-side occupancy
mirroring, with Vitest specs alongside each component. For any new standalone
extraction, follow the `ux-splitter` folder convention (see
`angular-draggable-splitter.md`) — one folder per component, `*.spec.ts`
alongside each.

Back to the index: [angular-drag-drop](angular-drag-drop.md)

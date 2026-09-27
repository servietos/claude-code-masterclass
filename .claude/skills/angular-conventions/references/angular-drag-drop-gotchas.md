# Drag-and-drop gotchas

## Gotchas

- **`pointer-events: none` on overlay wrappers is what makes `elementsFromPoint`
  work at all.** Without it, the dragged item's own absolutely-positioned
  anchor (or a sibling card) intercepts the hit-test and the resolver never
  reaches the grid cell underneath.
- **Release pointer capture on `pointercancel`, not just `pointerup`.** Browsers
  fire `pointercancel` on alt-tab, an incoming notification, or a scroll
  gesture take-over; skipping it leaves `isDragging` stuck `true` and the
  ghost styling stuck on.
- **Call `setPointerCapture` on the element that received `pointerdown`,
  never on the container** — otherwise move/up events stop arriving once the
  pointer leaves the source element's original bounds.
- **Keep the touch start delay off for mouse** (`0`) — a nonzero delay on
  desktop makes dragging feel laggy; only touch needs the press-and-hold
  window to disambiguate a drag from a scroll.
- **A single `dragOverCell` signal isn't enough once "not-allowed" targets
  exist** — resolve validity as part of the cell (`{ ...cell, blocked }`), or a
  blocked cell will show the same gold highlight as a valid one.
- **Don't wire `(pointerenter)`/`(dragenter)` per cell in a large grid.** One
  container-level `elementsFromPoint` call scales regardless of grid size and
  keeps working when cards visually overlap cells.
- **`document.elementsFromPoint` is unavailable in `jsdom`.** Stub it directly
  in tests (see above) rather than trying to dispatch real `PointerEvent`s and
  expecting the browser's layout engine to resolve targets — `jsdom` has none.
- **A disabled source must short-circuit at `pointerdown`, not just hide a CSS
  affordance** — otherwise a fast flick can still start a drag before any
  `disabled` check runs later in the handler chain.
- **An insertion line drawn on an item that clips its own overflow is invisible,
  and the class is applied correctly the whole time.** A card with
  `overflow: hidden` (usually there to round an inner image/rail against the
  card's `border-radius`) clips its own `::before`, so a bar positioned in the
  gutter (`left: -18px`) never paints, and a bar at `left: 0` paints *on top of*
  the card's own artwork where it reads as decoration rather than an insertion
  point. Fix by moving the clip inward: drop `overflow: hidden` from the card and
  give the inner element that actually needed it its own matching radius
  (`border-radius: 7px 0 0 7px` on a left rail). Verify with
  `getComputedStyle(card).overflow === 'visible'` plus a screenshot, not the
  class list — `classList` shows `--drop-before` either way.
- **A "slot taken?" check keys on the (row, position), not the entity.** When one
  entity can occupy multiple rows/strips (e.g. the same employee across several
  schedule rows), the occupancy test — the client's blocked-cell highlight AND
  the server's drop rejection — must key on the *slot* (`row + column/date`),
  never on `(entity, date)`. Keying on the entity wrongly blocks a valid move
  because that entity has an unrelated assignment elsewhere the same day. **The
  server must mirror the client's per-cell occupancy rule**, not a coarser one —
  enforce validity server-side, don't trust the client gate alone.
- **`document.elementsFromPoint` returns `[]` for points outside the visible
  viewport** — including cells scrolled out of a horizontally/vertically clipped
  grid. A drop over an off-screen target silently no-ops (the drag *starts*, the
  drop resolves to nothing). Rely on the edge auto-scroll to bring targets on
  screen; when scripting a synthetic drag to verify, assert the target center is
  within `innerWidth`/`innerHeight` first — an off-viewport target reads as a
  product bug when it's a harness artifact.
- **No droppable targets rendered at all = drag looks completely broken, and no
  amount of fixing the drag *handlers* helps.** When a grid/board only renders
  drop cells for entities that already have data (a data-gated `@for` swimlane
  loop that hits its `@empty` branch when the entity set is empty), a zero-data
  state renders **zero `data-*` targets** — `elementsFromPoint` finds nothing on
  every `pointermove`, so every drop no-ops and the pointer handlers (which are
  fine) appear dead. **Before touching the drag gesture, confirm droppable
  targets actually exist in the DOM** (not the empty state). Fix the empty case
  with an *always-present* drop surface — e.g. a persistent "new assignment"
  row/column that carries the `data-*` keys regardless of whether any entity has
  data yet. And when a drop resolves a *slot* (row/date) but not the owning
  *entity* (no lane was targeted), **prompt for the entity** (an inline picker)
  rather than silently no-op'ing — a drop that can't infer the assignee should
  ask, not do nothing. (Bico plan-board `mode="confirmed"`: an empty week
  rendered no employee lanes → nothing to drop onto; the fix added a "Neue
  Zuteilung" day-cell row plus an employee-picker dialog on a lane-less drop.)
- **Zoneless apps flush signal updates asynchronously.** After dispatching
  synthetic pointer events (browser/e2e verification), `await` an animation frame
  before reading signal-driven classes/badges (`.is-dragging`, the not-allowed
  reason) — a synchronous read misses the not-yet-rendered change.
- **`setPointerCapture` throws for a synthetic `pointerId` with no active
  pointer.** Harmless in real usage (a real `pointerdown` has an active pointer);
  it only bites when scripting `PointerEvent`s — and the state set before that
  line still applies, so the drag proceeds regardless.
- **Angular `HttpClient` with `provideHttpClient(withFetch())` issues `fetch`,
  not `XMLHttpRequest`.** To confirm a drop persisted, hook `window.fetch` (or
  watch the network panel) — an `XMLHttpRequest.prototype` spy sees nothing.


Back to the index: [angular-drag-drop](angular-drag-drop.md)

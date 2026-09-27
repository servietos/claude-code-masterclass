# Splitter design decisions and how it works

## Design decisions (the ones that matter)

- **Resize ONE pane, measure from its own edge.** Pick the pane that resizes
  (usually the right/side pane) and store *its* width as the single source of
  truth. Compute width from the container edge to the pointer:
  `rightWidth = containerRect.right - pointer.clientX`. Anchoring to an edge (not
  a running delta) means no drift and no "grab offset" bookkeeping.
- **State = one `linkedSignal`, not `signal` + manual init.** Seed it lazily from
  `localStorage` (clamped), but keep it freely settable by drag/keyboard
  afterwards. `linkedSignal(() => readInitialWidth())` gives exactly this: a
  computed seed that a `.set()`/`.update()` can override.
- **Drive layout from a CSS var via a host style binding**, not by mutating
  styles imperatively. `host: { '[style.--ux-splitter-right]': 'rightWidthPx()' }`
  keeps it declarative and OnPush-friendly; the SCSS reads `var(--…-right)` in
  `grid-template-columns`.
- **Pointer Events + Pointer Capture on the divider itself** — no
  document-level listeners, no `Renderer2`, no manual add/removeEventListener.
  `setPointerCapture(pointerId)` on `pointerdown` routes every subsequent
  `pointermove`/`pointerup` to the divider even when the pointer leaves it.
- **`touch-action: none`** on the divider so touch drags don't scroll the page.
- **Persist in an `effect`, guarded.** Wrap `window`/`localStorage` access in a
  `typeof window === 'undefined'` check + `try/catch` (quota / disabled storage /
  SSR) so resizing still works when persistence can't.

## How it works (see the file for full source)

- **Right pane is the resizable one**; its width is the single source of truth,
  measured from the container's right edge to the pointer
  (`rect.right - event.clientX`), so dragging the divider **left grows** the right
  pane. State is a `linkedSignal` seeded (clamped) from `localStorage` yet freely
  settable by drag/keyboard.
- Layout is driven by a **CSS custom property via a host style binding**:
  `host: { '[style.--ux-splitter-right]': 'rightWidthPx()' }`; the SCSS reads
  `var(--ux-splitter-right)` in `grid-template-columns`.
- Drag uses **Pointer Events + `setPointerCapture` on the divider** — no
  document listeners, no `Renderer2`. `touch-action: none` on the divider.
- Persistence is an `effect` writing `localStorage[storageKey]`, guarded for
  missing `window`/`localStorage` (SSR / quota / disabled) so resize still works
  without persistence.
- **Mobile-first:** below `md` (768px) the panes stack in one column and the
  divider is `display:none` — nothing to drag on a narrow viewport (home's aside
  must still stack below the chat, as before).


Back to the index: [angular-draggable-splitter](angular-draggable-splitter.md)

# Splitter SCSS and grid

## SCSS — mobile-first, CSS-var-driven grid, grabbable divider

```scss
:host {                       // mobile: stacked column, divider hidden
  display: flex; flex-direction: column;
  min-height: 0; height: 100%; gap: var(--gap-sm);
}
.ux-splitter__pane {
  display: flex; flex-direction: column; min-width: 0; min-height: 0;
  > * { flex: 1 1 auto; min-width: 0; min-height: 0; }   // give projected child a definite height
}
.ux-splitter__divider { display: none; }

@media (min-width: 768px) {   // md+ : 1fr / 6px divider / resizable right col
  :host {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 6px minmax(0, var(--ux-splitter-right, 320px));
    gap: 0;
  }
  .ux-splitter__divider {
    display: block; position: relative; align-self: stretch;
    width: 6px; cursor: col-resize; touch-action: none; border-radius: 3px;
    background: var(--divider-color, #e5e2da);

    &::before { content: ""; position: absolute; inset: 0 -4px; }  // ~14px hit area
    &::after  { content: ""; position: absolute; top: 50%; left: 50%;
                width: 2px; height: 24px; transform: translate(-50%, -50%);
                border-radius: 1px; background: var(--grip-color, #c9c5ba); }  // grip

    &:hover, &.is-dragging, &:focus-visible { background: var(--accent-color, #e7ba43); }
    &:focus-visible { outline: 2px solid var(--accent-color, #e7ba43); outline-offset: 2px; }
    @media (prefers-reduced-motion: no-preference) { transition: background-color .15s ease; }
  }
}
```

Key CSS points:
- **Mobile-first stack, no divider below `md`** — there's nothing to drag on a
  narrow viewport; the panes just stack.
- **`minmax(0, …)` on both flexible tracks** so a pane with long content can
  actually shrink instead of blowing out the grid.
- **Thin 6px visual divider + a ~14px invisible `::before` hit area** — a 6px
  target is too thin to grab reliably.
- **Give the single projected child `flex: 1 1 auto; min-height: 0`** so its own
  internal `overflow-y:auto` scroll regions get a definite height (CSS Grid's
  default `align-items: stretch` gives the pane full row height).
- **Declare that rule from the PROJECTOR's stylesheet, not this one.** The `.ux-splitter__pane > *` rule above
  compiles to `.ux-splitter__pane > *[_ngcontent-splitter]`, so a component
  declared in the host page's template carries the host's content attribute and
  never matches. It still works for a bare `<div slot-left>` whose shape the
  splitter's own template happens to cover, but any real component projected in
  needs the host page to say:

  ```css
  /* the projector's stylesheet */
  .my-side-panel { display: block; flex: 1 1 auto; align-self: stretch; min-height: 0; }
  ```

  Symptom when missed: the pane takes full row height, the projected component
  keeps its content height, and a bottom-aligned footer inside it floats above the
  pane's bottom edge. Verify with `getBoundingClientRect()` on pane and child, not
  a screenshot: equal heights is the receipt. Full write-up:
  [projected-content](angular-css-not-applying-projected-content.md).
- Swap the `var(--…, fallback)` colors for your design system's hairline / accent
  tokens; light up the divider in the brand accent on hover/drag/focus.

Back to the index: [angular-draggable-splitter](angular-draggable-splitter.md)

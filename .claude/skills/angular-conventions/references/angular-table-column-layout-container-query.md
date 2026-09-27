# Collapsible rail: container query, not media query

## When a collapsible rail owns the width, the query must be a container query

The three-width check above catches this bug. This is why a viewport breakpoint
cannot *fix* it.

A shell with a collapsible nav rail changes the row's available width without
changing the viewport by a single pixel. In an Angular secrets list (a six-column
CSS grid, `.sl-row`, not a `<table>`, same geometry problem) the rail is
`--rail-width-expanded: 13rem` against `--rail-width-collapsed: 3.5rem`: a 152px
swing that `@media (max-width: 1024px)` is structurally blind to. Tune the
breakpoint for the expanded state and the collapsed state gets rules meant for a
container 152px narrower than it is; tune it for collapsed and the expanded state
starves. There is no viewport value that is right for both, so moving the
breakpoint is not a fix, it is a choice of which state to break.

Make the row respond to its own column instead:

```css
.sl-root {
  container-type: inline-size;
}

@container (max-width: 700px) { /* was @media (max-width: 1024px) */ }
@container (max-width: 585px) { /* was @media (max-width: 900px)  */ }
```

Two mechanics that decide whether this works:

- **The container must be an ancestor of the rule's subject**, never the element
  being sized. Pick the nearest ancestor whose width already equals the row's
  content column: a plain block wrapper with no horizontal padding of its own.
  A wrapper that adds padding shifts every threshold by that padding.
- **Derive the thresholds, do not guess them.** Measure the chosen container's
  own rendered width at each old viewport breakpoint, in the rail state the
  original tuning was done in, and use those numbers. Here 1024px viewport gave a
  704px container and 900px gave 585px, so `700` and `585` keep the transition
  exactly where it already was for the tuned case and pick up the other rail
  state for free. Re-measure at the old breakpoint afterwards and require the
  same grid tracks you had before: that is the proof the conversion changed
  nothing you had already got right.

Back to the index: [angular-table-column-layout](angular-table-column-layout.md)

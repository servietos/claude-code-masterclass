# Ratio splitter and its E2E races

## Ratio-based sibling: `app-ui-split-pane` in media-creator-ui

`src/media-creator-ui/src/app/shared/ui/ui-split-pane.ts` is the same pattern with
one deliberate variant: it stores a **ratio** (`linkedSignal<number>`, clamped to
`[0.3, 0.75]`), not a pixel width, driving `grid-template-columns: minmax(0,
calc(var(--split-ratio, 0.55) * 100%)) auto minmax(0, 1fr)` through a host style
binding, restored from and persisted to `localStorage` under a per-usage
`storageKey` (the Generate page uses `mc.generate.split`). Testids: `split-pane`,
`split-start`, `split-handle`, `split-end`.

Two things an E2E spec against this component (or any host page that composes it
with a container query) needs to account for, found while writing
`e2e/tests/generate-workspace.spec.ts`:

- **A container-query breakpoint on the left pane and a persisted ratio can
  interact across test runs.** The Generate page switches its Chat/Preview tabs
  to an always-both-visible wide layout once the left pane's own inline size
  crosses a `@container` breakpoint, not the viewport width. Since that pane's
  width is `ratio * container width`, a ratio persisted by an earlier drag or
  keyboard resize can widen the left pane past the breakpoint on the very next
  test, silently flipping the layout and making the tabbed UI a spec expects
  disappear. Any spec built on the narrow, tabbed layout should clear the split
  pane's `localStorage` key before its first navigation: an `addInitScript`
  removing the key works well there, since it runs before the app's first read.
  Exactly one spec, the one that exercises drag and keyboard resize itself,
  should be allowed to write the key, and it needs a different mechanism: it
  cannot clear the key via `addInitScript`, because that script reruns on every
  navigation for the lifetime of the page, including the reload the same test
  performs later to check persistence, and it would erase the very ratio that
  reload is meant to observe. Clear it with a one-off `page.evaluate(() =>
  localStorage.removeItem(key))` followed by a single `page.reload()` before
  taking any measurement, instead.
- **Only the persistence side of the ratio's effects lags the input event that
  changed it, not the layout.** The CSS custom property that drives the grid
  track is a host style binding (`[style.--split-ratio]`), so it updates
  synchronously with the `ratio` signal and the rendered width is correct the
  moment change detection runs. The `localStorage` write sits in a separate
  `effect()`, and that one is not synchronous with the triggering event.
  Measured directly: three ArrowRight presses sent back to back can leave
  `localStorage` reflecting only the first press for a couple hundred
  milliseconds before catching up to the last, while the pane's own rendered
  width already matches the third press. A spec that reads `localStorage` right
  after the interaction can observe a stale, in-between value even though the
  DOM is already correct; poll `localStorage` until it stops changing rather
  than trusting a single read. A related race sits one step earlier, at the
  keyboard step itself: a synthetic keydown sent too soon after a `focus()`
  call can land before Chromium's own keyboard focus target has caught up with
  `document.activeElement`, so a short wait between `focus()` and the first
  key press is needed too.

Back to the index: [angular-draggable-splitter](angular-draggable-splitter.md)

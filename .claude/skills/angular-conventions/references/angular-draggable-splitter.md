# Angular Draggable Splitter

A hand-rolled, reusable **draggable splitter** (resizable two-pane layout: drag a
vertical divider to resize the left/right panes) for standalone Angular 22
(signals + `OnPush`). No third-party library — `@angular/cdk`, `angular-split`,
and `angular-resizable-element` are all unnecessary for a single vertical divider,
and the hand-rolled version is less code with exact px control.

Use this when a fixed `grid-template-columns` split (e.g. `[1fr_16rem]`) should
become user-resizable, with the chosen width persisted across reloads.

| You want to... | Read |
| --- | --- |
| Why is the width anchored to the container edge, why linkedSignal, why a CSS var host binding? Open before changing the mechanism. | [design](angular-draggable-splitter-design.md) |
| Need the component class itself: inputs, linkedSignal seed, pointer handlers, clamp, the persistence effect. | [component-ts](angular-draggable-splitter-component-ts.md) |
| Writing the template, or the divider is not focusable / not announced / arrow keys scroll the page. | [template-a11y](angular-draggable-splitter-template-a11y.md) |
| Divider too thin to grab, panes blowing out the grid, inner scroll areas with no height, or the mobile stack. | [scss](angular-draggable-splitter-scss.md) |
| How do I drop the splitter into a page: the host snippet, the slot selectors, and what each input defaults to. | [api-usage](angular-draggable-splitter-api-usage.md) |
| What must the Vitest spec cover, and what does the existing splitter.component.spec.ts already assert. | [testing](angular-draggable-splitter-testing.md) |
| Resize looks broken in the browser, aria-valuenow never moves, or a component named split turns out not to drag. | [gotchas](angular-draggable-splitter-gotchas.md) |
| Switching px to ratio (or any stored unit) and the pane opens at max for existing users while the code looks correct. | [storage-unit-change](angular-draggable-splitter-storage-unit-change.md) |
| Which pages already use ux-splitter, with their storageKey, min/max numbers and what the replacement left intact. | [usage-sites](angular-draggable-splitter-usage-sites.md) |
| Working on app-ui-split-pane in media-creator-ui, or an E2E spec flips layout / reads a stale localStorage ratio. | [ratio-variant](angular-draggable-splitter-ratio-variant.md) |

- **Unique `storageKey` per usage site** (`home-split`, `edit-split`, …) so pages
  don't share a persisted width.

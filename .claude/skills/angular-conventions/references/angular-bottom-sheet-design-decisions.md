# Bottom sheet design decisions

## Design decisions

| Concern | Decision | Why |
| --- | --- | --- |
| Modal primitive | Native `<dialog>` + `showModal()`/`close()` | No CDK overlay available; the `<dialog>` is in the top layer already |
| Component shape | The bottom sheet owns its `<dialog>` internally (`viewChild` + private show/hide) and exposes public `open()`/`close()` | The host embeds `<app-x-bottom-sheet #sheet>` once and drives it imperatively, instead of owning the `<dialog>` ref itself |
| Positioning | `position: fixed`, `inset: auto 0 0 0`, `width: 100%`, geometry set on the `<dialog>` itself (not a wrapping `<div>`) so the UA's default `dialog[open]` centering is overridden | A `<dialog>` is top-layer already; no extra stacking context or portal needed |
| Entrance transition | CSS `transition` on `transform: translateY(...)`, toggled by an `[open]`-scoped class flip on the next frame (`requestAnimationFrame`) after `showModal()` | `showModal()` makes the dialog visible instantly (no CSS transition fires on the `display: none → flex` jump); animating a `transform` after paint gives the slide-up without the View Transitions API |
| Backdrop | `::backdrop` on the same `<dialog>` | Free with the native element; no extra scrim `<div>` |
| Close affordances | Drag handle / explicit close button (click) + native `cancel` event (Esc) + backdrop click (`mousedown` on `event.target === dialogEl`) | Covers the standard Esc-to-close and click-outside conventions |
| Focus | `showModal()` auto-focuses the first focusable descendant and traps Tab; on close, refocus the element that had focus before opening (captured in `open()`) | WCAG AA — focus must return to the trigger, not silently reset to `<body>` |
| Change detection | `ChangeDetectionStrategy.OnPush`, all state in `signal()` | Standalone-Angular house style |

Back to the index: [angular-bottom-sheet](angular-bottom-sheet.md)

# Constant-footprint indicators, sr-only text and looping animations

## Visually-hidden text & CSS animation

A "constant-footprint" indicator (loader, spinner, status badge shown only while busy) must occupy **identical layout** whether active or idle, or its neighbors shift when the busy state toggles. CSS transforms (`scale`, `translate`) don't affect layout; conditionally-rendered *in-flow* nodes — including screen-reader text — do.

| Wrong | Correct |
|---|---|
| `class="sr-only"` assuming a global visually-hidden utility exists | Scope the rule in the component's own styles (`position:absolute; width:1px; height:1px; margin:-1px; clip:rect(0 0 0 0); overflow:hidden; white-space:nowrap; border:0`) — many apps (and non-configured Tailwind builds) have **no** global `.sr-only`, so the "hidden" text renders in-flow and takes width |
| `@if (active()) { <span class="sr-only">Loading…</span> }` — inserting/removing the a11y text node per state | Keep the node **always present**; toggle only its text content and `aria-hidden`/`role`. Adding/removing an in-flow node reflows siblings → a visible horizontal jump the moment the state ends |
| `animation-play-state: paused` to "stop" a looping animation when idle | Freezes it on whatever random mid-cycle frame it reached. Use `animation: none` in the idle state and attach the `animation` shorthand only under the active class (`.x--active .dot { animation: … }`) so each activation restarts cleanly from 0% |

Verify a constant-footprint indicator by sampling a neighbor's `getBoundingClientRect().left` across idle→active→idle — it must not move.

Back to the index: [angular-antipatterns](angular-antipatterns.md)

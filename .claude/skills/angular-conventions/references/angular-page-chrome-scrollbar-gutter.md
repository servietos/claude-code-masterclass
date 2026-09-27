# Scrollbar gutter jumps, and proving a layout change worked

## Layout stability: reserve the scrollbar gutter

A tab or filter that swaps content of different heights makes the page's own vertical scrollbar
appear and disappear as the document crosses the viewport height. The 15px track toggling shifts
everything horizontally on every click. The customer reports it as "a vertical bar causing jumps",
and will attribute it to whatever content they were switching between: a diagram, a table, a chart.
It is never the content's width.

**Diagnose by height, not width.** Log `document.documentElement.scrollHeight` per filter state and
look for one state that sits at or below `window.innerHeight` while the others tower over it:

```js
// filter A 1847 | filter B 1305 | filter C 1305 | filter D 1305
// innerHeight ~1305 -> three of four states have no scrollbar. That is the jump.
```

**Put `scrollbar-gutter: stable` on the element whose overflow propagates to the viewport.** This is
the trap: almost every app carries `body { overflow-x: hidden }`, and because the root's overflow is
`visible`, the UA propagates *body's* overflow to the viewport. Body then owns the viewport scrollbar,
so the gutter must be declared there. On `html` it is inert:

```css
/* WRONG — computes to "stable", does absolutely nothing */
html { scrollbar-gutter: stable }
body { overflow-x: hidden }

/* RIGHT — body propagates its overflow to the viewport, so body owns the gutter */
body { overflow-x: hidden; scrollbar-gutter: stable }
```

`overflow-x: clip` instead of `hidden` does not rescue the `html` version either; clip is not a
scroll container, but the gutter still failed to reserve in Chrome. Declare it on `body` and move on.

**`getComputedStyle` returning your value is not proof the property took effect.** The inert `html`
version reported `scrollbarGutter: "stable"` while `documentElement.clientWidth` still flipped
2545 ↔ 2560 on every scope change. Only the geometric consequence proves it. Assert on
`document.body.clientWidth` plus a fixed element's `getBoundingClientRect()` across every state and
require identical numbers:

```js
// body clientWidth 2545 in all four states, controls left/right 610.33/1934.33 in all four -> fixed
```

## Verification

- A green build is not evidence a layout change works. Screenshot every route.
- Browser `resize_window` calls can report success and change nothing when the window is maximized.
  Read back `window.innerWidth` before trusting a responsive check, and say so plainly when the
  breakpoints could not be exercised.
- A CSS property that computes to the value you set may still be inert. Measure the geometry it was
  supposed to change, across every state that is supposed to stay put.
EOF

Back to the index: [angular-page-chrome](angular-page-chrome.md)

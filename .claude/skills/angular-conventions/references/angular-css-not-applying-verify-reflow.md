# Verify the reflow, do not assume it

## Verify the reflow, do not assume it

Measure the outcome rather than trusting the rule you just wrote:

```js
const m = document.querySelector('.card-main').getBoundingClientRect();
const s = document.querySelector('.card-side').getBoundingClientRect();
({ sameLine: Math.abs(m.top - s.top) < 2, mainW: Math.round(m.width), sideW: Math.round(s.width) })
```

To check the wrap threshold without resizing the window (window resizing is unreliable when the window
is maximized), drive the container width in-page, measure at each step, and restore it:

```js
const el = document.querySelector('.grid'); const prev = el.style.cssText;
const out = {};
for (const w of [1100, 900, 760, 620]) {
  el.style.width = w + 'px'; el.getBoundingClientRect();
  const m = document.querySelector('.card-main').getBoundingClientRect();
  const s = document.querySelector('.card-side').getBoundingClientRect();
  out[w] = { sameLine: Math.abs(m.top - s.top) < 2 };
}
el.style.cssText = prev; out;
```

A screenshot remains the acceptance criterion; these reads are for locating the fault, not for signing
off on it.

Back to the index: [angular-css-not-applying](angular-css-not-applying.md)

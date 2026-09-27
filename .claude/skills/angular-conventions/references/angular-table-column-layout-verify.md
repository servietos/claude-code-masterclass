# Measuring column geometry, not assuming it

## Verifying it, not assuming it

A green build proves nothing here; this is a pure layout property. Measure it:

```js
const t = document.querySelector('table');
const wrap = t.closest('[class*="overflow-x"]') || t.parentElement;
({
  clientWidth: wrap.clientWidth,
  scrollWidth: wrap.scrollWidth,
  overflow: wrap.scrollWidth - wrap.clientWidth,   // must be 0
  columns: [...t.querySelectorAll('thead th')]
    .filter(th => getComputedStyle(th).display !== 'none')
    .map(th => [th.innerText.trim().split('\n')[0], Math.round(th.getBoundingClientRect().width)])
})
```

For the jump itself, capture the header x-positions, sort, capture again, and
require them to be identical. Screenshots are the ground truth; treat a numeric
read as a cross-check, not as the proof.

Regression checklist for any column-geometry change:

- [ ] Sort by every sortable column: header x-positions unchanged.
- [ ] Switch every filter value: header x-positions unchanged.
- [ ] Scroll far enough to append a page: header x-positions unchanged.
- [ ] Default state: `scrollWidth === clientWidth`, last column fully visible.
- [ ] Narrowest breakpoint where the responsive columns drop: still no overflow.

Back to the index: [angular-table-column-layout](angular-table-column-layout.md)

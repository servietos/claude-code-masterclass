# Height defects left behind when Material's box goes

## Fill-height chains

Getting an editor or preview to use the available height failed three ways before it worked:

- `min-height: 100%` on the card lets it grow past the pane (measured 1405px inside a 393px pane)
- `height: 100%` alone collapses the inner editor to 0 when the pane is short
- `height: 100%` on the textarea itself never resolves at all

The working shape:

```scss
:host { display: block; height: 100%; min-height: 22rem; }   /* floor keeps it usable when short */
.card { display: flex; flex-direction: column; height: 100%; }
.card-content { flex: 1; min-height: 0; overflow: auto; }
:host(app-editor) { display: flex; flex-direction: column; flex: 1; min-height: 0; }
.leaf-textarea { flex: 1; min-height: 0; }                    /* never a percentage height */
```

Every link in the chain needs `min-height: 0`, or a flex item refuses to shrink below its content.

### Fixed heights survive the migration and then overlap

A shared directive composing `host: { style: 'height:100px' }` is invisible while Material supplies its own
box, and becomes a defect once the markup is plain: content taller than the box paints over whatever follows.
Measure rather than squint:

```js
[...document.querySelectorAll('[boxed]')].map(el => ({
  h: Math.round(el.getBoundingClientRect().height),
  scroll: el.scrollHeight,
  overflowing: el.scrollHeight > el.getBoundingClientRect().height + 1,
}))
```

The fix is `min-height` plus a real flex column with a gap, never a fixed `height`.

Back to the index: [material-tailwind-migration](material-tailwind-migration.md)

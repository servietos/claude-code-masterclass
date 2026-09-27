# Cause 3: an unlayered global rule beats your Tailwind utility

## Cause 3: an unlayered global rule beats your Tailwind utility

Tailwind v4 emits its utilities inside `@layer`. Any plain rule you wrote in `styles.css` outside a layer is
**unlayered**, and per the CSS Cascade Layers spec unlayered declarations always win over layered ones,
regardless of specificity or source order. So a hand-rolled global component class silently defeats the
utility you add next to it:

```html
<!-- .btn-ghost:hover is unlayered in styles.css, so hover:text-danger NEVER applies -->
<button class="btn btn-ghost hover:text-danger hover:bg-danger/10">Delete</button>

<!-- .btn sets cursor: pointer unlayered, so cursor-not-allowed NEVER applies -->
<button class="btn cursor-not-allowed" aria-disabled="true">Unavailable</button>
```

Nothing errors, the class is present in the DOM, and reading the markup tells you nothing. Confirm with the
computed style, not the class list:

```js
const b = document.querySelector('button.btn-ghost');
getComputedStyle(b).cursor;            // 'pointer' even though cursor-not-allowed is on the element
```

Two ways out, in order of preference:

1. **Drop the global class** for that control and build it from plain utilities. This is right for one-off
   controls (pills, chips, an aria-disabled mock button) that need hover or cursor treatment the base class
   forbids.
2. **Change the global class** in `styles.css`, or move it into a layer, when the override should apply
   everywhere. Only do this deliberately: it reflavors every button in the app.

The same trap applies to any hand-written global (`.field`, `.filter-input`, `.popup-actionbar`). Treat a
global component class and a Tailwind state utility on the same element as mutually exclusive until proven
otherwise.

Back to the index: [angular-css-not-applying](angular-css-not-applying.md)

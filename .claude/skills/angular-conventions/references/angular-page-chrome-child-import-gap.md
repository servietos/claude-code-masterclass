# A child component inherits none of its shell's imported CSS

## Every consumer imports it, including child components

### Every consumer imports it, including child components

The shells listed above are not the only importers. Emulated encapsulation scopes an imported rule to
the template of the component that imported it, so a **child component rendered inside an importing
shell inherits nothing**. A tab view whose own template renders `<ul class="page-kpis page-kpis--sub">`
must `@import 'page-chrome.css'` itself, even though its parent shell already does.

This failure is quiet and easy to misread as a data bug. The classes are intact in the DOM inspector,
the build is clean, the tests are green, the markup is correct: only the rendered pixels are wrong, and
the element falls back to browser defaults (a bare `<ul>` with disc bullets, value and label with no
separation). Confirm by reading computed styles, not by eye:

```js
getComputedStyle(document.querySelector('.page-kpis--sub'))
// broken: display "block", listStyleType "disc", gridTemplateColumns "none"
// fixed:  display "grid",  listStyleType "none", gridTemplateColumns "177px 177px ..."
```

Re-check the component style budget afterwards: `@import` inlines the whole shared file into every
importing component's stylesheet, so each new importer pays its full size again.

Back to the index: [angular-page-chrome](angular-page-chrome.md)

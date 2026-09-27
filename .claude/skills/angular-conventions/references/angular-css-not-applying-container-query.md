# Cause 2: a container query cannot match its own container

## Cause 2: a container query cannot match its own container

`container-type` establishes a query container for that element's **descendants**. The element that
declares it can never match its own `@container` rule. This fails silently: valid CSS, green build, rule
simply never applies.

```css
/* BROKEN — .card-top declares the container and is also the query target */
.card-top { display: flex; flex-direction: column; container-type: inline-size; }
@container (min-width: 300px) {
  .card-top { flex-direction: row; }   /* never applies, at any width */
  .card-side { flex: 0 0 124px; }      /* applies — it is a descendant */
}
```

The half-applied result is the tell: children pick up their container-query declarations while the
container keeps its base layout, so you get a correctly-sized child in a wrongly-stacked parent.

Two fixes:

```css
/* A: move the container up one level — query the parent, style the child */
.card { container-type: inline-size; }
@container (min-width: 300px) {
  .card-top { flex-direction: row; }
}
```

```css
/* B (preferred for "sits beside, else wraps below"): plain flex-wrap, no query at all */
.card-top  { display: flex; flex-wrap: wrap; align-items: flex-start; gap: 10px 14px; }
.card-main { flex: 1 1 220px; min-width: 0; }   /* basis = the width it needs to stay on one line */
.card-side { flex: 0 1 124px; max-width: 124px; }
```

Option B needs no container at all: the wrap threshold is `main-basis + side-basis + gap`, so choose the
main basis as the narrowest width at which sharing the line still looks right. Prefer it whenever the
requirement is one-dimensional; reach for a container query only when the child must restyle itself
(not merely reflow) based on the space it was given.

Back to the index: [angular-css-not-applying](angular-css-not-applying.md)

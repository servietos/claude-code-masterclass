# Shared chrome CSS lives in an imported file, never styles.css

## Shared CSS: an imported file, not global `styles.css`

Cross-page primitives (`.page-hero`, `.page-kpis`, `.view-nav`) must live in a plain CSS file that
each component `@import`s from its own `styleUrl`:

```
src/app/shared/page-chrome.css
```

```css
/* dashboard.css, deployment-page.css, billing-shell.css */
@import '../../shared/page-chrome.css';
```

**Do not put them in the global `styles.css`.** Angular's default emulated encapsulation rewrites
component rules with an attribute selector, so a component's own `.kpi` always outranks a global
`.kpi` — but the global rule still *applies* its base properties to that element. Any generic class
name (`.kpi`, `.card`, `.tile`) will silently bleed into unrelated components that happen to use the
same word. Importing into the component keeps every rule scoped, and the `@import` is resolved at
build time so there is no extra request.

Corollary: when a shared primitive would collide with an existing component class, **prefix it**
(`.page-kpi`, not `.kpi`) rather than hunting down the collisions.

Back to the index: [angular-page-chrome](angular-page-chrome.md)

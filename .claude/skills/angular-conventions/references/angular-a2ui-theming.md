# A2UI Theming Tokens

## Theming

The BasicCatalog injects a default stylesheet using `:where(:root)` selectors (minimal specificity). Override tokens in your global `styles.css`:

```css
:root {
  /* Primary brand color */
  --a2ui-color-primary: #86efac;

  /* Typography */
  --a2ui-font-family-title:     'Inter', sans-serif;
  --a2ui-font-family-monospace: 'Fira Code', monospace;

  /* Component tokens */
  --a2ui-card-background: #0f3d20;
}

/* Override color scheme in a subtree */
.a2ui-light { color-scheme: light; }
.a2ui-dark  { color-scheme: dark; }
```

Dark mode is auto-detected via `prefers-color-scheme`. Apply `.a2ui-light` or `.a2ui-dark` to an ancestor element to override for a subtree.

The renderer controls _how_ components look. Agents control _what_ to show. Agents must use semantic hints (`"variant": "h1"`) rather than pixel values or color literals.

Back to the index: [angular-a2ui](angular-a2ui.md)

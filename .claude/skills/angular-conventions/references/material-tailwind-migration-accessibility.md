# Accessibility regressions the migration introduces

## Accessibility regressions the migration introduces

Material supplies a lot of accessibility that hand-rolled markup does not. Run axe-core over every
route afterwards. The violations that appeared, and their fixes:

| axe rule | Cause | Fix |
|---|---|---|
| `landmark-one-main`, `region` | no `<main>` once `mat-sidenav-content` is gone | wrap the outlet in `<main>` |
| `page-has-heading-one` | Material card titles were never headings | one `sr-only` `<h1>` in the shell, bound to the router title |
| `landmark-unique` | two `<nav>` elements | distinct `aria-label` on each |
| `heading-order` | `.card-title` as a `div`, sections as `<h4>` | `h2.card-title`, sections `<h3>` |
| `label` | toggle/checkbox with no visible text | `aria-label` input on the shared toggle component |
| `scrollable-region-focusable` | any `overflow: auto` box | `tabindex="0"` + `role="region"` + label |
| `color-contrast` | see below | see below |

Contrast is the one that needs numbers rather than judgement. White text on Material Blue 600
(`#1e88e5`) is **3.68:1** and fails AA; `#1976d2` is **4.63:1** and passes. A translucent active
state such as `bg-white/15` over that blue composites to `#3c8bd9` at 3.56:1 and also fails, so use
a solid darker token instead. Replace `opacity: 0.5/0.6` muted text with an explicit `#64748b`.

Adding the `sr-only` `<h1>` will break `getByText()` assertions that were previously unique. Scope
them to a container.

Back to the index: [material-tailwind-migration](material-tailwind-migration.md)

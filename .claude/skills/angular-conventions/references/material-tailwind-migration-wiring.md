# Wiring Tailwind v4 into an Angular app and removing Material

## Wiring

`scripts/material-to-tailwind.sh --wire <app-dir> [--dry-run]` does the deterministic half of this
section (packages, `.postcssrc.json`, style order, the `*` reset). `--verify <app-dir>` is read-only
and reports whether an app is fully off Material and correctly wired; it is the finish-line check for
the sweep described further down.

```bash
npm install -D tailwindcss @tailwindcss/postcss postcss
npm uninstall @angular/material
```

**Do not uninstall `@angular/cdk` reflexively.** Material depends on the CDK; the CDK does not depend on
Material, and other packages sit on top of it. `@angular/aria` declares a *hard peer* on
`@angular/cdk`, so removing it breaks `@angular/aria/{listbox,tabs,combobox}` imports with unresolved
modules that no source edit can fix. `cdk/scrolling`, `cdk/overlay` and `cdk/testing` are likewise
independent of Material. Check first:

```bash
grep -rn "@angular/cdk" src
npm ls @angular/cdk        # shows the peer edges
```

Uninstall it only when both come back empty. Three of the eleven apps in this repo legitimately keep it.

`.postcssrc.json` in the app root:

```json
{ "plugins": { "@tailwindcss/postcss": {} } }
```

Put the Tailwind entry in `angular.json` **before** the SCSS entry:

```json
"styles": ["src/tailwind.css", "src/styles.scss"]
```

Author `src/tailwind.css` as plain CSS, not SCSS. `@import "tailwindcss"` inside a `.scss` file makes
sass try to resolve `tailwindcss` as a sass partial and fail; a separate `.css` entry sidesteps it
entirely, and `@tailwindcss/postcss` resolves the import itself with no `postcss-import`.

Order matters for a reason worth knowing: Tailwind emits into cascade layers, and **unlayered rules
always beat layered ones regardless of specificity**. That is what keeps existing component SCSS
working as overrides. It is also the source of the first trap below.

Back to the index: [material-tailwind-migration](material-tailwind-migration.md)

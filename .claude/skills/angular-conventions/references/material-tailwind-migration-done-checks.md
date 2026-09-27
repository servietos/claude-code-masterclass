# What proves the migration is finished

## The sweep is not done when the build passes

`ng build` succeeding proves the components compile. It says nothing about:

- **e2e selectors**: `mat-icon`, `mat-card-title`, `mat-label`, `[mattooltip]`, `input[matinput]`,
  `mat-slide-toggle` all appear in Playwright specs and all break silently.
- **markdown or docs** shipped with the app: code samples showing `mat-stroked-button`.
- **fixture data** naming Material as a topic or skill.

The finish line is an empty result from

```bash
grep -rn "mat-\|Mat[A-Z]\|@angular/material\|@angular/cdk" src e2e public
```

## Verify by measuring, not by looking

Two defects in this migration were invisible on screen and obvious in numbers:

- A loading bar rendered `rgb(25,118,210)` on top of a `rgb(25,118,210)` topbar. It worked perfectly
  and could not be seen.
- Two header rows that should have formed one continuous rule sat 16px apart (bottom borders at
  y=112 and y=96) because one was `--toolbar-big` and the other `--toolbar-medium`.

Read back `getBoundingClientRect()` and `getComputedStyle()` for both layers of any overlay, and for
any two edges that are supposed to align. See the global `chrome-devtools` skill (`~/.claude/skills/chrome-devtools/SKILL.md`) for
driving that measurement.

### The build passing is not the finish line, and neither is the suite

Both were green on an app whose every demo rendered its guide twice, because each component embedded the same
markdown renderer the shell already showed. Nothing static could see it. Budget one browser pass per app: open
two routes, compare against the reference app, and measure any two edges that should align.

Back to the index: [material-tailwind-migration](material-tailwind-migration.md)

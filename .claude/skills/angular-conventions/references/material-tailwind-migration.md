# Migrating an Angular app off Angular Material onto Tailwind v4

Verified end to end on an Angular 22 zoneless app with ~40 Material-using components: build clean,
51/51 unit tests, axe-core 0 violations across 20 routes. Then repeated across ten sibling apps in the same
repo: all eleven off Material, all builds clean, 416 unit tests passing. The single-app material is below;
[Rolling it out to many apps](material-tailwind-migration-fleet-split.md) carries what only the repeat run taught.

Hard rule carried from the wiring leaf: **Do not uninstall `@angular/cdk` reflexively.**

| You want to... | Read |
|---|---|
| Starting the migration: which packages to add and remove, whether @angular/cdk may go, .postcssrc.json, and why the Tailwind style entry comes first. | [wiring](material-tailwind-migration-wiring.md) |
| Borders vanished, "Cannot apply unknown utility class", or showModal() renders flush top-left after Tailwind landed. | [css-traps](material-tailwind-migration-css-traps.md) |
| What replaces this specific mat-* component, directive or service, and why toolbar classes are named by position. | [replacement-map](material-tailwind-migration-replacement-map.md) |
| An editor or textarea will not fill the pane, or a formerly invisible fixed height now paints over the content below it. | [height-chains](material-tailwind-migration-height-chains.md) |
| TestBed specs fail on matchMedia, or the suite reports a wall of "Need to call TestBed.initTestEnvironment() first". | [test-failures](material-tailwind-migration-test-failures.md) |
| Which axe-core violations appear once Material's built-in accessibility is gone, and the contrast numbers that pass AA. | [accessibility](material-tailwind-migration-accessibility.md) |
| The build and the suite are green: what is still broken, the grep that is the real finish line, and measuring instead of looking. | [done-checks](material-tailwind-migration-done-checks.md) |
| Migrating a fleet of sibling apps: what to copy yourself, what to fan agents out over, and what to take back to the owner. | [fleet-split](material-tailwind-migration-fleet-split.md) |
| The frame copy broke the target: a missing environment file, an inverted environment convention, or files only the target had. | [fleet-frame-copy](material-tailwind-migration-fleet-frame-copy.md) |

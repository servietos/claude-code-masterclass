# Angular Bottom Sheet (Native `<dialog>`, No CDK)

A bottom sheet on the native `<dialog>` element, no Angular Material and no `@angular/cdk`. The bottom sheet follows shape 1.

| You want to... | Read |
| --- | --- |
| Know what it is, and whether the component owns its dialog or a parent drives one | [angular-bottom-sheet-overview](angular-bottom-sheet-overview.md) |
| Choose between a bottom sheet and a centered `.dialog` | [angular-bottom-sheet-vs-centered-dialog](angular-bottom-sheet-vs-centered-dialog.md) |
| See why fixed inset geometry, the rAF class flip, `::backdrop` and focus return were chosen | [angular-bottom-sheet-design-decisions](angular-bottom-sheet-design-decisions.md) |
| Write the class: `open()`/`close()`, the rAF visible flip, the 200ms close delay, backdrop click, focus restore | [angular-bottom-sheet-component](angular-bottom-sheet-component.md) |
| Get the template and the CSS that pins it to the bottom edge, slides it up, styles the backdrop | [angular-bottom-sheet-markup-and-styles](angular-bottom-sheet-markup-and-styles.md) |
| Embed the sheet in a host and open it from a button | [angular-bottom-sheet-host-usage](angular-bottom-sheet-host-usage.md) |
| Fix a spec failing because jsdom has no `showModal`/`close`, or get the focus-return test | [angular-bottom-sheet-testing](angular-bottom-sheet-testing.md) |

# Picker overlay, ESC stack and focus

## Overlay behaviour

Use the app's existing overlay and escape-stack machinery rather than hand-rolling
(see `angular-overlays.md`). The requirement worth stating explicitly:

> One ESC press pops exactly one layer, the topmost one, and nothing else.

With a detail row expanded and the picker open, ESC closes only the picker; the row
stays expanded. Press again and the next layer down closes. Register the dropdown
on the escape stack when it opens and unregister when it closes, and **do not add a
host or document `keydown` listener alongside it**. That parallel listener is
exactly what produces the "one ESC closed two things" bug.

Focus: move into the first control when it opens, and return to the trigger button
on every close path (ESC, backdrop click, reset).

Back to the index: [angular-table-column-visibility](angular-table-column-visibility.md)

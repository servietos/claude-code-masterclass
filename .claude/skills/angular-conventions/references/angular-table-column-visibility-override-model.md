# The three-valued column override and its two derived signals

## Two states per column, not one

The naive model is a boolean per column. That breaks as soon as the table also has
responsive rules like `hidden lg:table-cell`, because "hidden right now" and "the
user turned it off" are different facts.

Use the same three-valued override the rest of the app uses for panel collapse
(`'expanded' | 'collapsed' | null`, where `null` means "follow the automatic
behaviour"):

- `null` (untouched): the responsive rule decides. Behaviour is unchanged from
  before the feature existed.
- `'expanded'`: visible at every width, even below its breakpoint.
- `'collapsed'`: hidden at every width.

An explicit choice wins over the breakpoint. A column the user deliberately
switched on must not vanish when they narrow the window.

This produces two distinct derived signals, and conflating them is a bug:

- `columnVisible(col)` drives the actual `<th>`/`<td>` rendering.
- `isColumnChecked(col)` drives the checkbox, and is `override !== 'collapsed'`.

A column that is checked but currently below its breakpoint shows as checked while
rendering nothing. That is correct: the user never turned it off, the viewport
narrowed. Deriving the checkbox from `columnVisible` instead would make checkboxes
flicker off as the window shrinks, which reads as the app forgetting settings.

Drive the breakpoint half from a viewport signal updated by the same
`ResizeObserver` already used for width auto-fill, rather than a second listener.

## Defaults, and the rest of the picker

- Some columns ship hidden. Express that as an explicit `'collapsed'` default for
  that column, unconditionally, not as a narrower breakpoint.
- A row-actions column is never listed and never hideable.
- **Never let the table go empty**: block hiding the last checked column, and
  disable that checkbox rather than silently ignoring the click.
- A reset action restores the default visibility set. Scope it to visibility only;
  column widths have their own per-column reset.

Back to the index: [angular-table-column-visibility](angular-table-column-visibility.md)

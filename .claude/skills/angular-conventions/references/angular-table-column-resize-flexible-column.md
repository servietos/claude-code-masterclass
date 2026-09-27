# The flexible column needs an explicit computed width

## The flexible column, and why it needs an explicit width

The tempting design is to leave one column (the widest free-text one, usually
contact/email) unsized so it soaks up whatever the others leave. It is
overflow-proof by construction, and it is **not collapse-proof**. Measured on a
real admin list view at an 821px CSS viewport with the sidebar expanded, once a
responsive column dropped out:

```
Date 152 | Type 136 | Name 144 | Contact 4 | Actions 80
wrapper clientWidth 525, scrollWidth 525, overflow 0
```

Zero overflow, and the contact column rendered **four pixels wide** with no email
visible at all. The invariant "no horizontal overflow" was satisfied by a
completely broken table. Losing the column's content is worse than the scrollbar
it was avoiding.

Adding `min-width` to the table does not rescue this either. With
`table-layout: fixed`, a `min-width` on a cell is not honoured, and forcing the
table's own box wider leaves the surplus unallocated: the table box grew to the
min-width while the flexible cell still rendered at 36.7px against a 110px
minimum, with the difference sitting as an unclaimed gap.

**What works: compute the flexible column's width in JS and always render it
explicitly.**

```
autoWidth = max(
  thisColumn.minWidth,
  wrapper.clientWidth - sum(width of every OTHER column that is CURRENTLY visible)
)
```

Keep that as a pure function taking a list of visible widths, so it is unit
testable and nothing hardcodes one particular column set. Drive recomputation
from a `ResizeObserver` on the scroll wrapper plus an effect over the persisted
widths and the visibility state. Below the floor the column keeps its minimum, the
row simply becomes wider than the wrapper, and the existing `overflow-x-auto`
scrolls. That is the same "explicit widths outgrow the container" path a manual
resize already relies on, so there is one behaviour, not two.

The invariant, which supersedes the weaker one in `angular-table-column-layout.md`:

> Zero horizontal overflow in the default state, **and** every visible column at
> or above its legible minimum in **every** reachable state. When those two cannot
> both hold, the scrollbar wins. Never crush a column.

Back to the index: [angular-table-column-resize](angular-table-column-resize.md)

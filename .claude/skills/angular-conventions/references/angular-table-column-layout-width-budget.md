# Fix part 2: default widths must fit the container

## Fix, part 2: the defaults must fit the container

`table-fixed` alone trades a jump for an overflow. Giving every column an explicit
width and letting the sum exceed the container produces this, measured on the same
page right after the naive fix:

```
container (overflow-x wrapper) clientWidth : 895
table scrollWidth                          : 1036
overflow                                   : 141px
Date 160 | Type 144 | Name 176 | Contact 220 | Preferred 256 | Actions 80
```

The last column (row actions) was pushed entirely outside the visible area behind
a horizontal scrollbar, which is worse for the user than the jump that was fixed.

**The trap to avoid:** CSS2.1 section 17.5.2 says a browser distributes *surplus*
width proportionally when the specified widths sum to **less** than the table
width. That is true, and it is the reason all-explicit widths feel safe. It says
nothing about the deficit case. When the widths sum to **more** than the
container there is nothing to distribute and the table simply overflows. Reasoning
from the surplus rule alone is how the regression above got shipped.

Two workable shapes, both fine:

1. **Leave one column unsized.** Size every column except the widest free-text one
   (contact/email is the natural candidate). It absorbs the remainder, so the sum
   can never exceed the container. Write an explicit width for it only if and when
   the user drags it.
2. **Size all columns, but budget them.** Every column explicit, with the defaults
   chosen so they fit the *narrowest* container in which they are all visible.

Whichever you pick, the invariant is the same and it is what to assert in review:

> In the default, never-resized state the table has **zero horizontal overflow**
> and the last column is **fully visible**.

Verify it at three widths, because the container changes independently of the
viewport:

1. Around 1200 CSS px with the sidebar nav **expanded** (the tightest common case).
2. Same viewport with the nav **collapsed** (wider container, same columns).
3. At `xl` and above, where an `xl:table-cell` column appears and needs its own budget.

Back to the index: [angular-table-column-layout](angular-table-column-layout.md)

# Toggling columns and the width pool

## Interaction with column widths

Hiding a column returns its width to the pool, showing one takes width from it, so
the sizing model must be correct for **every reachable combination**, not tuned for
the default set. Concretely: the flexible column's auto-fill sums the widths of the
columns that are *currently visible*, and the point at which the horizontal
scrollbar appears therefore moves as columns are toggled. Do not hardcode a single
global minimum that only happens to work for the default set.

All-columns-visible is the tightest combination and the one that will force the
scrollbar first. Measured on a real admin list view at a 901px container with
every column switched on:

```
Date 152 | Type 136 | Name 144 | Contact 110 | Tags 120 | Preferred 232 | Actions 80
sum 974, wrapper clientWidth 901, overflow 73, wrapper scrolls by exactly 73
```

The flexible column floored at its 110px minimum and the excess became an honest
scrollbar. That is the correct outcome, and it is what to assert.

Back to the index: [angular-table-column-visibility](angular-table-column-visibility.md)

# Angular Table Column Layout

Stable column geometry for a data table whose rows are loaded a page at a time
(server-side sort plus infinite scroll). Covers the two failure modes that look
opposite but share one cause: **columns that jump**, and **columns that overflow**.

Use this before adding sorting, filtering, resizing, or column visibility to any
list view. Get the geometry right first; every later feature builds on it.

| You want to... | Read |
| --- | --- |
| Pick the next data-table leaf, or place persisted geometry | [family-and-related](angular-table-column-layout-family-and-related.md) |
| Diagnose a table that jumps on sort, filter or append | [sort-jump-bug](angular-table-column-layout-sort-jump-bug.md) |
| Pin the layout with `table-fixed` | [table-fixed](angular-table-column-layout-table-fixed.md) |
| Budget default widths so nothing overflows | [width-budget](angular-table-column-layout-width-budget.md) |
| Measure the geometry and run the regression list | [verify](angular-table-column-layout-verify.md) |
| Handle a collapsible rail with a container query | [container-query](angular-table-column-layout-container-query.md) |
| Know which viewport and rail states to click through | [rail-test-matrix](angular-table-column-layout-rail-test-matrix.md) |

The invariant every leaf here serves:

> In the default, never-resized state the table has **zero horizontal overflow**
> and the last column is **fully visible**.

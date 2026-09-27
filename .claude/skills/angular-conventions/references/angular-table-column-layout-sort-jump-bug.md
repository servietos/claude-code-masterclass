# Symptom: sorting shifts every column sideways

## The bug: sorting shifts every column sideways

Symptom: click a sort header and the whole table visibly jumps horizontally.
Measured on a real admin list view (six columns, server-side sort, infinite
scroll), sorting by the last text column:

```
column      before   after
Type          420      434
Name          545      576
Contact       680      722
Preferred     912      980
```

Cause: `<table class="w-full">` with no `table-fixed` uses **auto** table layout,
so each column is as wide as its widest loaded cell. Sorting is server-side and
the list is infinite-scroll, so a sort click reloads a *different first page* of
rows. Different rows means a different widest cell means every column recomputes.

The row content changing is correct. The columns moving is not.

This is invisible in dev with 5 seed rows and obvious in production with 80. It
also fires on filter changes, on search, and on the first infinite-scroll append,
so "it only happens when I sort" is usually an under-report.

Back to the index: [angular-table-column-layout](angular-table-column-layout.md)
